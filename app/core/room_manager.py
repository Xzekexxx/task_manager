from fastapi import WebSocket
import asyncio
import redis.asyncio as redis

redis_client = redis.from_url("redis://localhost")


class Room_Manager():
    def __init__(self):
        self.rooms: dict[str, set[WebSocket]] = {}
        self._pubsubs: dict[str, redis.client.PubSub] = {}
        self._listen_tasks: dict[str, asyncio.Task] = {}

    async def _start_listener(self, room: str):
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(room)
        self._pubsubs[room] = pubsub
        self._listen_tasks[room] = asyncio.create_task(self._listener(room))

    async def _listener(self, room: str):
        
        try:
            async for message in self._pubsubs[room].listen():
                if message["type"] == "message":
                    data = message["data"]
                    if isinstance(data, bytes):
                        data = data.decode()
                    await self.send_local(room, data)
        except asyncio.CancelledError:
            pass

    async def connect(self, room: str, ws: WebSocket):
        self.rooms.setdefault(room, set()).add(ws)
        
        # Запустить listener для комнаты, если ещё не запущен
        if room not in self._listen_tasks:
            await self._start_listener(room)

    async def disconnect(self, room: str, ws: WebSocket):
        conn = self.rooms.get(room)
        if not conn:
            return
        conn.discard(ws)
        
        # Остановить listener, если не осталось клиентов
        if not conn:
            self.rooms.pop(room)
            if room in self._listen_tasks:
                self._listen_tasks[room].cancel()
                try:
                    await self._listen_tasks[room]
                except asyncio.CancelledError:
                    pass
                del self._listen_tasks[room]
            
            if room in self._pubsubs:
                await self._pubsubs[room].unsubscribe(room)
                await self._pubsubs[room].close()
                del self._pubsubs[room]
        

    async def send_local(self, room: str, msg: str):
        for client in self.rooms.get(room, set()):
            try:
                await client.send_text(msg)
            except Exception as e:
                return {"error": f"{e}"}

    async def close(self):
        for room, task in self._listen_tasks.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        for room, pubsub in self._pubsubs.items():
            await pubsub.close()
        
        self._listen_tasks.clear()
        self._pubsubs.clear()


room_manager = Room_Manager()