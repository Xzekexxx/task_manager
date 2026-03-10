from fastapi import WebSocket

import redis.asyncio as redis

redis_client = redis.from_url("redis://localhost")
pubsub = redis_client.pubsub()


async def listener():
    async for message in pubsub.listen():
        if message["type"] == "message":
            data = message["data"]
            channel = message['channel']
            if isinstance(channel, bytes):
                channel = channel.decode()
            if isinstance(data, bytes):
                data = data.decode()
            await room_manager.send_local(channel, data)

class Room_Manager():
    def __init__(self):
        self.rooms : dict[str, set[WebSocket]] = {}

    async def connect(self, room: str, ws: WebSocket):
        self.rooms.setdefault(room, set()).add(ws)
        await pubsub.subscribe(room)

    async def disconnect(self, room: str, ws: WebSocket):
        conn = self.rooms.get(room)
        if not conn:
            return
        conn.discard(ws)
        if not conn:
            self.rooms.pop(room)
            await pubsub.unsubscribe(room)

    async def send_local(self, room: str, msg: str):
        for client in self.rooms.get(room, set()):
            await client.send_text(msg)

    
room_manager = Room_Manager()