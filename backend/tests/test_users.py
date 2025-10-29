# User API tests
import json
import pytest
from datetime import datetime
from app.services import user_service


def test_create_user(test_app, monkeypatch):
    """ユーザー作成のテスト"""
    test_request_payload = {"username": "testuser", "password": "password123"}
    test_response_payload = {
        "id": 1,
        "username": "testuser",
        "is_active": True,
        "created_date": "2024-01-01T00:00:00",
    }

    async def mock_get_by_username(username):
        return None

    async def mock_create_user(payload):
        return {
            "id": 1,
            "username": payload.username,
            "is_active": True,
            "created_date": datetime(2024, 1, 1),
        }

    monkeypatch.setattr(user_service, "get_by_username", mock_get_by_username)
    monkeypatch.setattr(user_service, "create_user", mock_create_user)

    response = test_app.post("/api/users/", content=json.dumps(test_request_payload))

    assert response.status_code == 201
    assert response.json()["username"] == "testuser"
    assert response.json()["is_active"] is True


def test_create_user_duplicate_username(test_app, monkeypatch):
    """重複ユーザー名のテスト"""
    test_request_payload = {"username": "testuser", "password": "password123"}

    async def mock_get_by_username(username):
        return {"id": 1, "username": "testuser"}

    monkeypatch.setattr(user_service, "get_by_username", mock_get_by_username)

    response = test_app.post("/api/users/", content=json.dumps(test_request_payload))

    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"


def test_create_user_invalid_json(test_app):
    """無効なユーザーデータのテスト"""
    # パスワードが短すぎる
    response = test_app.post(
        "/api/users/", content=json.dumps({"username": "testuser", "password": "123"})
    )
    assert response.status_code == 422

    # ユーザー名が短すぎる
    response = test_app.post(
        "/api/users/", content=json.dumps({"username": "ab", "password": "password123"})
    )
    assert response.status_code == 422

    # パスワードが欠落
    response = test_app.post(
        "/api/users/", content=json.dumps({"username": "testuser"})
    )
    assert response.status_code == 422


def test_read_user(test_app, monkeypatch):
    """ユーザー取得のテスト"""
    test_data = {
        "id": 1,
        "username": "testuser",
        "is_active": True,
        "created_date": datetime(2024, 1, 1),
    }

    async def mock_get_user(user_id):
        return test_data

    monkeypatch.setattr(user_service, "get_user", mock_get_user)

    response = test_app.get("/api/users/1/")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_read_user_not_found(test_app, monkeypatch):
    """存在しないユーザーのテスト"""

    async def mock_get_user(user_id):
        return None

    monkeypatch.setattr(user_service, "get_user", mock_get_user)

    response = test_app.get("/api/users/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_read_user_invalid_id(test_app):
    """無効なユーザーIDのテスト"""
    response = test_app.get("/api/users/0/")
    assert response.status_code == 422


def test_read_all_users(test_app, monkeypatch):
    """全ユーザー取得のテスト"""
    test_data = [
        {
            "id": 1,
            "username": "user1",
            "is_active": True,
            "created_date": datetime(2024, 1, 1),
        },
        {
            "id": 2,
            "username": "user2",
            "is_active": True,
            "created_date": datetime(2024, 1, 2),
        },
    ]

    async def mock_get_all_users():
        return test_data

    monkeypatch.setattr(user_service, "get_all_users", mock_get_all_users)

    response = test_app.get("/api/users/")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_user(test_app, monkeypatch):
    """ユーザー更新のテスト"""
    test_payload = {"password": "newpassword123", "is_active": False}

    async def mock_get_user(user_id):
        return {
            "id": 1,
            "username": "testuser",
            "is_active": True,
            "created_date": datetime(2024, 1, 1),
        }

    async def mock_update_user(user_id, payload):
        return {
            "id": 1,
            "username": "testuser",
            "is_active": False,
            "created_date": datetime(2024, 1, 1),
        }

    monkeypatch.setattr(user_service, "get_user", mock_get_user)
    monkeypatch.setattr(user_service, "update_user", mock_update_user)

    response = test_app.put("/api/users/1/", content=json.dumps(test_payload))
    assert response.status_code == 200
    assert response.json()["is_active"] is False


def test_update_user_not_found(test_app, monkeypatch):
    """存在しないユーザーの更新テスト"""
    test_payload = {"password": "newpassword123"}

    async def mock_get_user(user_id):
        return None

    monkeypatch.setattr(user_service, "get_user", mock_get_user)

    response = test_app.put("/api/users/999/", content=json.dumps(test_payload))
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


@pytest.mark.parametrize(
    "user_id, payload, status_code",
    [
        [0, {"password": "password123"}, 422],  # 無効なID
        [1, {"password": "123"}, 422],  # パスワードが短すぎる
    ],
)
def test_update_user_invalid(test_app, monkeypatch, user_id, payload, status_code):
    """無効なユーザー更新のテスト"""

    async def mock_get_user(user_id):
        return {
            "id": 1,
            "username": "testuser",
            "is_active": True,
            "created_date": datetime(2024, 1, 1),
        }

    monkeypatch.setattr(user_service, "get_user", mock_get_user)

    response = test_app.put(f"/api/users/{user_id}/", content=json.dumps(payload))
    assert response.status_code == status_code


def test_delete_user(test_app, monkeypatch):
    """ユーザー削除のテスト"""
    test_data = {
        "id": 1,
        "username": "testuser",
        "is_active": True,
        "created_date": datetime(2024, 1, 1),
    }

    async def mock_get_user(user_id):
        return test_data

    async def mock_delete_user(user_id):
        return user_id

    monkeypatch.setattr(user_service, "get_user", mock_get_user)
    monkeypatch.setattr(user_service, "delete_user", mock_delete_user)

    response = test_app.delete("/api/users/1/")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"


def test_delete_user_not_found(test_app, monkeypatch):
    """存在しないユーザーの削除テスト"""

    async def mock_get_user(user_id):
        return None

    monkeypatch.setattr(user_service, "get_user", mock_get_user)

    response = test_app.delete("/api/users/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_delete_user_invalid_id(test_app):
    """無効なIDでの削除テスト"""
    response = test_app.delete("/api/users/0/")
    assert response.status_code == 422
