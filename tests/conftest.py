"""Фикстуры для тестов API."""
import pytest
from unittest.mock import AsyncMock


@pytest.fixture
def mock_auth_rep():
    """Мок для репозитория аутентификации."""
    rep = AsyncMock()
    rep.register_user = AsyncMock(return_value={"message": "You have registered successfully"})
    rep.login_user = AsyncMock(return_value={"access_token": "test_token", "token_type": "bearer"})
    rep.about_user = AsyncMock(return_value={"username": "testuser", "email": "test@example.com", "roles": "user"})
    rep.del_user = AsyncMock(return_value={"message": "Пользователь успешно удален"})
    return rep


@pytest.fixture
def mock_task_rep():
    """Мок для репозитория задач."""
    rep = AsyncMock()

    task1_dict = {
        "id": 1,
        "name": "Test Task",
        "description": "Test Description",
        "created": "testuser",
        "created_at": "2026-03-17",
        "status": "pending"
    }

    task2_dict = {
        "id": 1,
        "name": "Updated Task",
        "description": "Updated Description",
        "created": "testuser",
        "created_at": "2026-03-17",
        "status": "completed"
    }

    rep.create_new_task = AsyncMock(return_value=task1_dict)
    rep.get_tasks = AsyncMock(return_value=[task1_dict])
    rep.put_task = AsyncMock(return_value=task2_dict)
    rep.del_task = AsyncMock(return_value={"message": "задача успешно удалена"})
    return rep
