"""ノートAPIのテスト"""

import json
from datetime import datetime
from app.services import note_service


def test_create_note(test_app, auth_headers, mock_current_user, monkeypatch):
    """ノート作成のテスト"""
    test_payload = {"title": "Test Note", "content": "Test content"}

    async def mock_create_note(payload, user_id):
        return {
            "id": 1,
            "title": payload.title,
            "content": payload.content,
            "user_id": user_id,
            "created_date": "2024-01-01T00:00:00",
            "updated_date": "2024-01-01T00:00:00",
        }

    monkeypatch.setattr(note_service, "create_note", mock_create_note)

    response = test_app.post("/api/notes", json=test_payload, headers=auth_headers)

    assert response.status_code == 201
    assert response.json()["title"] == "Test Note"
    assert response.json()["content"] == "Test content"


def test_create_note_unauthorized(test_app_no_auth):
    """認証なしでのノート作成テスト"""
    test_payload = {"title": "Test Note", "content": "Test content"}

    response = test_app_no_auth.post("/api/notes", json=test_payload)

    assert response.status_code == 401


def test_get_notes(test_app, auth_headers, mock_current_user, monkeypatch):
    """ノート一覧取得のテスト"""
    test_data = [
        {
            "id": 1,
            "title": "Note 1",
            "content": "Content 1",
            "user_id": 1,
            "created_date": "2024-01-01T00:00:00",
            "updated_date": "2024-01-01T00:00:00",
        },
        {
            "id": 2,
            "title": "Note 2",
            "content": "Content 2",
            "user_id": 1,
            "created_date": "2024-01-02T00:00:00",
            "updated_date": "2024-01-02T00:00:00",
        },
    ]

    async def mock_get_all_notes(user_id):
        return test_data

    monkeypatch.setattr(note_service, "get_all_notes", mock_get_all_notes)

    response = test_app.get("/api/notes", headers=auth_headers)

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_note(test_app, auth_headers, mock_current_user, monkeypatch):
    """ノート詳細取得のテスト"""
    test_data = {
        "id": 1,
        "title": "Test Note",
        "content": "Test content",
        "user_id": 1,
        "created_date": "2024-01-01T00:00:00",
        "updated_date": "2024-01-01T00:00:00",
    }

    async def mock_get_note(note_id, user_id):
        return test_data

    monkeypatch.setattr(note_service, "get_note", mock_get_note)

    response = test_app.get("/api/notes/1", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["title"] == "Test Note"


def test_get_note_not_found(test_app, auth_headers, mock_current_user, monkeypatch):
    """存在しないノートの取得テスト"""

    async def mock_get_note(note_id, user_id):
        return None

    monkeypatch.setattr(note_service, "get_note", mock_get_note)

    response = test_app.get("/api/notes/999", headers=auth_headers)

    assert response.status_code == 404


def test_update_note(test_app, auth_headers, mock_current_user, monkeypatch):
    """ノート更新のテスト"""
    test_payload = {"title": "Updated Title", "content": "Updated content"}

    async def mock_update_note(note_id, user_id, payload):
        return {
            "id": 1,
            "title": "Updated Title",
            "content": "Updated content",
            "user_id": user_id,
            "created_date": "2024-01-01T00:00:00",
            "updated_date": "2024-01-02T00:00:00",
        }

    monkeypatch.setattr(note_service, "update_note", mock_update_note)

    response = test_app.put("/api/notes/1", json=test_payload, headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


def test_update_note_not_found(test_app, auth_headers, mock_current_user, monkeypatch):
    """存在しないノートの更新テスト"""
    test_payload = {"title": "Updated Title"}

    async def mock_update_note(note_id, user_id, payload):
        return None

    monkeypatch.setattr(note_service, "update_note", mock_update_note)

    response = test_app.put("/api/notes/999", json=test_payload, headers=auth_headers)

    assert response.status_code == 404


def test_delete_note(test_app, auth_headers, mock_current_user, monkeypatch):
    """ノート削除のテスト"""

    async def mock_delete_note(note_id, user_id):
        return 1

    monkeypatch.setattr(note_service, "delete_note", mock_delete_note)

    response = test_app.delete("/api/notes/1", headers=auth_headers)

    assert response.status_code == 204


def test_delete_note_not_found(test_app, auth_headers, mock_current_user, monkeypatch):
    """存在しないノートの削除テスト"""

    async def mock_delete_note(note_id, user_id):
        return 0

    monkeypatch.setattr(note_service, "delete_note", mock_delete_note)

    response = test_app.delete("/api/notes/999", headers=auth_headers)

    assert response.status_code == 404


def test_import_notes(test_app, auth_headers, mock_current_user, monkeypatch):
    """ノートインポートのテスト"""
    test_payload = [
        {"title": "Imported Note 1", "content": "Content 1"},
        {"title": "Imported Note 2", "content": "Content 2"},
    ]

    async def mock_import_notes(notes_data, user_id):
        return len(notes_data)

    monkeypatch.setattr(note_service, "import_notes", mock_import_notes)

    response = test_app.post(
        "/api/notes/import", json=test_payload, headers=auth_headers
    )

    assert response.status_code == 201
    assert response.json()["count"] == 2


def test_import_notes_empty(test_app, auth_headers, mock_current_user):
    """空のノートインポートテスト"""
    response = test_app.post("/api/notes/import", json=[], headers=auth_headers)

    assert response.status_code == 400
