# Task Manager API

FastAPI приложение для управления задачами с аутентификацией, RBAC и WebSocket уведомлениями через Redis.

## 📋 Содержание

- [Основной функционал](#основной-функционал)
- [Технологический стек](#технологический-стек)
- [Структура проекта](#структура-проекта)
- [Запуск](#запуск)
- [Переменные окружения](#переменные-окружения)
- [Миграции базы данных](#миграции-базы-данных)
- [Тестирование](#тестирование)
- [API Эндпоинты](#api-эндпоинты)
- [Роли](#роли)
- [Примеры запросов](#примеры-запросов)
- [Архитектура](#архитектура)

---

## Основной функционал

### 🔐 Аутентификация и авторизация

- **Регистрация пользователей**: валидация уникальности имени и email
- **JWT аутентификация**: Bearer токены с настраиваемым временем жизни (15 минут по умолчанию)
- **Cookie-аутентификация**: токен автоматически устанавливается в httpOnly cookie при входе
- **Безопасное хранение**: пароли хешируются с использованием bcrypt
- **Защита эндпоинтов**: декораторы и зависимости FastAPI для проверки токенов
- **Ролевая модель (RBAC)**: разделение прав доступа (user/admin)

### 📝 Управление задачами

- **CRUD операции**: создание, чтение, обновление, удаление задач
- **Статусы задач**: поддержка различных статусов (pending, in_progress, done и др.)
- **Привязка к комнатам**: задачи организуются по комнатам для групповой работы

### 🔔 WebSocket уведомления

- **Real-time обновления**: мгновенная рассылка уведомлений клиентам
- **Redis Pub/Sub**: масштабируемая система обмена сообщениями между комнатами
- **Поддержка комнат**: клиенты могут подключаться к разным комнатам
- **Ping/Pong**: механизм проверки соединения

### ⚠️ Обработка исключений

- **Кастомные исключения**: специализированные классы ошибок для разных модулей
- **Централизованный хендлер**: единая система обработки ошибок

---

## Технологический стек

| Компонент        | Технология                              | Назначение                          |
| ---------------- | --------------------------------------- | ----------------------------------- |
| **Backend**      | FastAPI + Pydantic v2                   | Веб-фреймворк и валидация данных    |
| **Database**     | PostgreSQL 17+                          | Реляционная база данных             |
| **ORM**          | SQLAlchemy 2.0 (Async)                  | Асинхронное взаимодействие с БД     |
| **Migrations**   | Alembic                                 | Управление схемой БД                |
| **Auth**         | JWT (PyJWT) + bcrypt + httpOnly cookies | Аутентификация и безопасность       |
| **Cache/PubSub** | Redis 8+                                | Кэширование и WebSocket уведомления |
| **Testing**      | Pytest                                  | Модульное тестирование              |
| **Container**    | Docker + Docker Compose                 | Контейнеризация                     |
| **API**          | REST + WebSocket                        | Архитектурный стиль                 |

---

## Структура проекта

```
task_manager/
│
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── auth.py           # Маршруты аутентификации
│   │   │   └── task.py           # Маршруты задач + WebSocket
│   │   └── schemas/
│   │       ├── user.py           # Pydantic схемы пользователей
│   │       └── task.py           # Pydantic схемы задач
│   │
│   ├── core/
│   │   ├── config.py             # Конфигурация приложения
│   │   ├── rbac.py               # Проверка прав доступа
│   │   ├── room_manager.py       # Управление WebSocket комнатами (Redis)
│   │   └── security.py           # JWT, хеширование паролей
│   │
│   ├── db/
│   │   ├── base.py               # Базовый класс SQLAlchemy
│   │   ├── database.py           # Сессии и подключение к БД
│   │   └── models.py             # Модели данных
│   │
│   ├── repositories/
│   │   ├── auth_repository.py    # Репозиторий аутентификации
│   │   └── task_repository.py    # Репозиторий задач
│   │
│   └── main.py                   # Точка входа
│
├── tests/
│   ├── conftest.py               # Фикстуры (моки репозиториев)
│   ├── test_auth_api.py          # Тесты аутентификации
│   └── test_task_api.py          # Тесты задач
│
├── .dockerignore
├── .env.example
├── .gitignore
├── alembic.ini
├── compose.yaml
├── docker-entrypoint.sh
├── Dockerfile
├── README.md
└── requirements.txt
```

---

## Запуск

### Предварительные требования

- Python 3.12+
- PostgreSQL 17+
- Redis 8+
- Docker и Docker Compose

---

### Вариант 1: Docker Compose (рекомендуется)

1. **Клонирование репозитория:**

   ```bash
   git clone <repository-url>
   cd task_manager
   ```

2. **Создать файл `.env`:**

   ```bash
   cp .env.example .env
   ```

3. **Запустить все сервисы:**

   ```bash
   docker compose up -d
   ```

4. **Остановка контейнеров:**
   ```bash
   docker compose down
   ```

**Доступные сервисы:**

| Сервис           | URL                        | Описание                                   |
| ---------------- | -------------------------- | ------------------------------------------ |
| **FastAPI**      | http://localhost:8000      | Основное API                               |
| **Swagger Docs** | http://localhost:8000/docs | Интерактивная документация                 |
| **pgAdmin**      | http://localhost:5050      | Веб-интерфейс БД (admin@admin.com / admin) |
| **Redis**        | localhost:6379             | Redis сервер                               |
| **PostgreSQL**   | localhost:5432             | PostgreSQL сервер                          |

---

### Вариант 2: Локальная разработка

1. **Клонирование репозитория:**

   ```bash
   git clone <repository-url>
   cd task_manager
   ```

2. **Создание и активация виртуального окружения:**

   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Установка зависимостей:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Настройка переменных окружения:**

   ```bash
   cp .env.example .env
   ```

5. **Запуск миграций:**

   ```bash
   alembic upgrade head
   ```

6. **Запуск приложения:**
   ```bash
   uvicorn app.main:app --reload
   ```

---

## Переменные окружения

Для корректной работы создайте файл `.env` в корневом каталоге:

```bash
# PostgreSQL
DB_HOST=postgres
DB_PORT=5432
DB_USER=postgres
DB_PASS=mypassword
DB_NAME=task_db

# JWT
SECRET_KEY=<генерировать: openssl rand -hex 32>
ALGORITHM=HS256
ACCES_TOKEN_EXPIRE_MINUTES=15

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
```

| Переменная                   | Описание           | По умолчанию |
| ---------------------------- | ------------------ | ------------ |
| `DB_HOST`                    | Хост PostgreSQL    | `postgres`   |
| `DB_PORT`                    | Порт PostgreSQL    | `5432`       |
| `DB_USER`                    | Пользователь БД    | `postgres`   |
| `DB_PASS`                    | Пароль БД          | `mypassword` |
| `DB_NAME`                    | Имя БД             | `task_db`    |
| `SECRET_KEY`                 | Ключ для JWT       | —            |
| `ALGORITHM`                  | Алгоритм JWT       | `HS256`      |
| `ACCES_TOKEN_EXPIRE_MINUTES` | Время жизни токена | `15`         |
| `REDIS_HOST`                 | Хост Redis         | `redis`      |
| `REDIS_PORT`                 | Порт Redis         | `6379`       |

---

## Миграции базы данных

Проект использует Alembic для управления миграциями БД.

**Создание новой миграции:**

```bash
alembic revision --autogenerate -m "описание изменений"
```

**Применение миграций:**

```bash
alembic upgrade head
```

**Откат миграций:**

```bash
alembic downgrade -1
```

---

## Тестирование

**Запуск всех тестов:**

```bash
pytest tests/ -v
```

**Запуск конкретного теста:**

```bash
pytest tests/test_auth_api.py::TestAuthEndpoints::test_login_user_success -v
```

**Запуск тестов с покрытием:**

```bash
pytest tests/ --cov=app
```

### Структура тестов

```
tests/
├── conftest.py       # Фикстуры (моки репозиториев)
├── test_auth_api.py  # Тесты аутентификации
└── test_task_api.py  # Тесты задач
```

Тесты используют моки вместо реальной БД, что обеспечивает быстрый запуск.

---

## API Эндпоинты

### Аутентификация

| Метод  | Endpoint               | Описание                               |
| ------ | ---------------------- | -------------------------------------- |
| POST   | `/reg`                 | Регистрация пользователя               |
| POST   | `/login`               | Вход пользователя в систему (OAuth2)   |
| GET    | `/about_user`          | Данные пользователя (имя, почта, роли) |
| DELETE | `/del_user/{username}` | Удаление пользователя (admin)          |

> **Примечание:** При успешном входе токен устанавливается в **httpOnly cookie** (`users_acces_token`). Последующие запросы к защищённым эндпоинтам могут использовать cookie или заголовок `Authorization: Bearer <token>`.

### Задачи

| Метод  | Endpoint                     | Описание                |
| ------ | ---------------------------- | ----------------------- |
| POST   | `/create_task/{room}`        | Создать новую задачу    |
| GET    | `/tasks_list`                | Список всех задач       |
| PUT    | `/put_task/{task_id}/{room}` | Обновить задачу (admin) |
| DELETE | `/del_task/{task_id}/{room}` | Удалить задачу (admin)  |

### WebSocket

| Метод | Endpoint     | Описание                                        |
| ----- | ------------ | ----------------------------------------------- |
| WS    | `/ws/{room}` | Подключение к WebSocket комнате для уведомлений |

**WebSocket протокол:**

| Сообщение          | Описание                    |
| ------------------ | --------------------------- |
| `{"token": "..."}` | Авторизация при подключении |
| `{"type": "ping"}` | Проверка соединения         |
| `{"type": "pong"}` | Ответ сервера на ping       |

---

## Роли

| Роль      | Права доступа                                              |
| --------- | ---------------------------------------------------------- |
| **user**  | Создание задач, просмотр списка, подключение к WebSocket   |
| **admin** | Все права user + обновление/удаление задач и пользователей |

---

## Примеры запросов

### Регистрация

```bash
curl -X POST http://localhost:8000/reg \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"123456"}'
```

### Вход

При входе токен устанавливается в **httpOnly cookie** (`users_acces_token`) и возвращается в ответе:

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=123456"
```

**Ответ:**

```json
{
  "access_token": "<token>",
  "token_type": "bearer"
}
```

> **Примечание:** Токен автоматически сохраняется в cookie браузера и будет отправляться с последующими запросами.

### Создание задачи

Для запросов можно использовать токен из cookie (автоматически) или передать в заголовке:

```bash
curl -X POST http://localhost:8000/create_task/room1 \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"name":"Task","description":"Desc","status":"pending"}'
```

### Получение списка задач

```bash
curl -X GET http://localhost:8000/tasks_list \
  -H "Authorization: Bearer <token>"
```

### Получение информации о пользователе

```bash
curl -X GET http://localhost:8000/about_user \
  -H "Authorization: Bearer <token>"
```

### Удаление пользователя (admin)

```bash
curl -X DELETE http://localhost:8000/del_user/testuser \
  -H "Authorization: Bearer <admin-token>"
```

### Подключение к WebSocket

```javascript
const ws = new WebSocket("ws://localhost:8000/ws/room1");

ws.onopen = () => {
  // Авторизация
  ws.send(JSON.stringify({ token: "<jwt-token>" }));
};

ws.onmessage = (event) => {
  console.log("Получено:", event.data);
};

// Ping для проверки соединения
setInterval(() => {
  ws.send(JSON.stringify({ type: "ping" }));
}, 30000);
```

---

## Архитектура

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Client    │────▶│   FastAPI    │────▶│  PostgreSQL │
└─────────────┘     └──────────────┘     └─────────────┘
       │                    │
       │                    ▼
       │             ┌──────────────┐
       └────────────▶│    Redis     │
                     │  (Pub/Sub)   │
                     └──────────────┘
```

**Компоненты:**

- **PostgreSQL** — хранение пользователей и задач
- **Redis** — Pub/Sub для WebSocket уведомлений между комнатами
- **FastAPI** — REST API + WebSocket сервер
- **Alembic** — управление миграциями БД

---
