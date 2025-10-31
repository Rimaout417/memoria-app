"""認証APIのテスト"""

import json
from app.services import user_service
from app.core.security import verify_password


def test_register_user(test_app, monkeypatch):
    """ユーザー登録のテスト"""
    test_payload = {"username": "newuser", "password": "password123"}

    async def mock_get_by_username(username):
        return None

    async def mock_create_user(payload):
        return {
            "id": 1,
            "username": payload.username,
            "is_active": True,
            "created_date": "2024-01-01T00:00:00",
        }

    monkeypatch.setattr(user_service, "get_by_username", mock_get_by_username)
    monkeypatch.setattr(user_service, "create_user", mock_create_user)

    response = test_app.post("/api/auth/register", json=test_payload)

    assert response.status_code == 201
    assert response.json()["username"] == "newuser"


def test_register_duplicate_username(test_app, monkeypatch):
    """重複ユーザー名での登録テスト"""
    test_payload = {"username": "existinguser", "password": "password123"}

    async def mock_get_by_username(username):
        return {"id": 1, "username": "existinguser"}

    monkeypatch.setattr(user_service, "get_by_username", mock_get_by_username)

    response = test_app.post("/api/auth/register", json=test_payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"


def test_login_success(test_app, monkeypatch):
    """ログイン成功のテスト"""

    async def mock_authenticate_user(username, password):
        return {
            "id": 1,
            "username": "testuser",
            "is_active": True,
            "created_date": "2024-01-01T00:00:00",
        }

    monkeypatch.setattr(user_service, "authenticate_user", mock_authenticate_user)

    response = test_app.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "password123"},
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_credentials(test_app, monkeypatch):
    """無効な認証情報でのログインテスト"""

    async def mock_authenticate_user(username, password):
        return None

    monkeypatch.setattr(user_service, "authenticate_user", mock_authenticate_user)

    response = test_app.post(
        "/api/auth/login",
        data={"username": "testuser", "password": "wrongpassword"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_get_current_user(test_app, auth_headers, mock_current_user, monkeypatch):
    """現在のユーザー情報取得のテスト"""

    async def mock_get_by_username(username):
        return {
            "id": 1,
            "username": "testuser",
            "is_active": True,
            "created_date": "2024-01-01T00:00:00",
        }

    monkeypatch.setattr(user_service, "get_by_username", mock_get_by_username)

    response = test_app.get("/api/auth/me", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_get_current_user_unauthorized(test_app_no_auth):
    """認証なしでのユーザー情報取得テスト"""
    response = test_app_no_auth.get("/api/auth/me")

    assert response.status_code == 401
