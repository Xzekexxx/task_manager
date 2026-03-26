"""Тесты для конечных точек задач."""
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from app.api.schemas.user import UserInDB
from app.main import app
from app.core.security import get_current_user


def get_test_user():
    """Возвращает тестового пользователя."""
    async def _get_user():
        return UserInDB(
            username="testuser",
            email="test@example.com",
            password="hash",
            roles="user"
        )
    return _get_user


def get_test_admin():
    """Возвращает тестового админа."""
    async def _get_user():
        return UserInDB(
            username="adminuser",
            email="admin@example.com",
            password="hash",
            roles="admin"
        )
    return _get_user


class TestTaskEndpoints:
    """Тесты для API задач."""

    def test_create_task_success(self, mock_task_rep):
        """Тест успешного создания задачи."""
        app.dependency_overrides = {
            get_current_user: get_test_user()
        }
        with TestClient(app) as client:
            with patch("app.api.endpoints.task.SqlAlchemyTaskRep", return_value=mock_task_rep):
                response = client.post(
                    "/create_task/test_room",
                    json={
                        "name": "New Task",
                        "description": "Task description",
                        "status": "pending"
                    }
                )
                assert response.status_code == 200
        app.dependency_overrides = {}

    def test_create_task_validation_error(self, mock_task_rep):
        """Тест ошибки валидации при создании задачи (короткое имя)."""
        app.dependency_overrides = {
            get_current_user: get_test_user()
        }
        with TestClient(app) as client:
            with patch("app.api.endpoints.task.SqlAlchemyTaskRep", return_value=mock_task_rep):
                response = client.post(
                    "/create_task/test_room",
                    json={
                        "name": "ab",
                        "description": "Task description",
                        "status": "pending"
                    }
                )
                assert response.status_code == 422
        app.dependency_overrides = {}

    def test_get_tasks_success(self, mock_task_rep):
        """Тест успешного получения списка задач."""
        app.dependency_overrides = {
            get_current_user: get_test_user()
        }
        with TestClient(app) as client:
            with patch("app.api.endpoints.task.SqlAlchemyTaskRep", return_value=mock_task_rep):
                response = client.get("/tasks_list")
                assert response.status_code == 200
        app.dependency_overrides = {}

    def test_put_task_requires_admin(self, mock_task_rep):
        """Тест что обновление задачи требует прав администратора."""
        app.dependency_overrides = {
            get_current_user: get_test_user()
        }
        with TestClient(app) as client:
            with patch("app.api.endpoints.task.SqlAlchemyTaskRep", return_value=mock_task_rep):
                response = client.put(
                    "/put_task/1/test_room",
                    json={
                        "name": "Updated Task",
                        "description": "Updated description",
                        "status": "completed"
                    }
                )
                assert response.status_code == 403
        app.dependency_overrides = {}

    def test_put_task_admin_success(self, mock_task_rep):
        """Тест успешного обновления задачи администратором."""
        app.dependency_overrides = {
            get_current_user: get_test_admin()
        }
        with TestClient(app) as client:
            with patch("app.api.endpoints.task.SqlAlchemyTaskRep", return_value=mock_task_rep):
                response = client.put(
                    "/put_task/1/test_room",
                    json={
                        "name": "Updated Task",
                        "description": "Updated description",
                        "status": "completed"
                    }
                )
                assert response.status_code == 200
        app.dependency_overrides = {}

    def test_del_task_requires_admin(self, mock_task_rep):
        """Тест что удаление задачи требует прав администратора."""
        app.dependency_overrides = {
            get_current_user: get_test_user()
        }
        with TestClient(app) as client:
            with patch("app.api.endpoints.task.SqlAlchemyTaskRep", return_value=mock_task_rep):
                response = client.delete("/del_task/1/test_room")
                assert response.status_code == 403
        app.dependency_overrides = {}

    def test_del_task_admin_success(self, mock_task_rep):
        """Тест успешного удаления задачи администратором."""
        app.dependency_overrides = {
            get_current_user: get_test_admin()
        }
        with TestClient(app) as client:
            with patch("app.api.endpoints.task.SqlAlchemyTaskRep", return_value=mock_task_rep):
                response = client.delete("/del_task/1/test_room")
                assert response.status_code == 200
        app.dependency_overrides = {}
