"""Тесты для конечных точек аутентификации."""
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


class TestAuthEndpoints:
    """Тесты для API аутентификации."""

    def test_register_user_success(self, mock_auth_rep):
        """Тест успешной регистрации пользователя."""
        app.dependency_overrides = {}
        with TestClient(app) as client:
            with patch("app.api.endpoints.auth.SqlAlchemyAuthRep", return_value=mock_auth_rep):
                response = client.post(
                    "/reg",
                    json={
                        "username": "testuser",
                        "email": "test@example.com",
                        "password": "testpass123"
                    }
                )
                assert response.status_code == 200
                assert response.json() == {"message": "You have registered successfully"}
        app.dependency_overrides = {}

    def test_register_user_validation_error(self):
        """Тест ошибки валидации при регистрации (короткий username)."""
        app.dependency_overrides = {}
        with TestClient(app) as client:
            response = client.post(
                "/reg",
                json={
                    "username": "ab",
                    "email": "test@example.com",
                    "password": "testpass123"
                }
            )
            assert response.status_code == 422

    def test_login_user_success(self, mock_auth_rep):
        """Тест успешного входа."""
        app.dependency_overrides = {}
        with TestClient(app) as client:
            with patch("app.api.endpoints.auth.SqlAlchemyAuthRep", return_value=mock_auth_rep):
                response = client.post(
                    "/login",
                    data={
                        "username": "testuser",
                        "password": "testpass123"
                    }
                )
                assert response.status_code == 200
                data = response.json()
                assert data["access_token"] == "test_token"
                assert data["token_type"] == "bearer"
        app.dependency_overrides = {}

    def test_about_user_success(self, mock_auth_rep):
        """Тест получения информации о пользователе."""
        app.dependency_overrides = {
            get_current_user: get_test_user()
        }
        with TestClient(app) as client:
            with patch("app.api.endpoints.auth.SqlAlchemyAuthRep", return_value=mock_auth_rep):
                response = client.get("/about_user")
                assert response.status_code == 200
                assert response.json() == {"username": "testuser", "email": "test@example.com", "roles": "user"}
        app.dependency_overrides = {}

    def test_del_user_requires_admin(self, mock_auth_rep):
        """Тест что удаление пользователя требует прав администратора."""
        app.dependency_overrides = {
            get_current_user: get_test_user()
        }
        with TestClient(app) as client:
            with patch("app.api.endpoints.auth.SqlAlchemyAuthRep", return_value=mock_auth_rep):
                response = client.delete("/del_user/otheruser")
                assert response.status_code == 403
        app.dependency_overrides = {}

    def test_del_user_admin_success(self, mock_auth_rep):
        """Тест успешного удаления пользователя администратором."""
        app.dependency_overrides = {
            get_current_user: get_test_admin()
        }
        with TestClient(app) as client:
            with patch("app.api.endpoints.auth.SqlAlchemyAuthRep", return_value=mock_auth_rep):
                response = client.delete("/del_user/otheruser")
                assert response.status_code == 200
                assert response.json() == {"message": "Пользователь успешно удален"}
        app.dependency_overrides = {}
