# Notes API tests

import json

import pytest

from app.services import note_service


def test_create_note(test_app, monkeypatch):
    test_request_payload = {"title": "something", "description": "something else"}
    test_response_payload = {
        "id": 1,
        "title": "something",
        "description": "something else",
    }

    async def mock_create_note(payload):
        return 1

    monkeypatch.setattr(note_service, "create_note", mock_create_note)

    response = test_app.post(
        "/api/notes/",
        content=json.dumps(test_request_payload),
    )

    assert response.status_code == 201
    assert response.json() == test_response_payload


def test_create_note_invalid_json(test_app):
    response = test_app.post("/api/notes/", content=json.dumps({"title": "something"}))
    assert response.status_code == 422

    response = test_app.post(
        "/api/notes/", content=json.dumps({"title": "1", "description": "2"})
    )
    assert response.status_code == 422


def test_read_note(test_app, monkeypatch):
    test_data = {"id": 1, "title": "something", "description": "something else"}

    async def mock_get_note(id):
        return test_data

    monkeypatch.setattr(note_service, "get_note", mock_get_note)

    response = test_app.get("/api/notes/1/")
    assert response.status_code == 200
    assert response.json() == test_data


def test_read_note_incorrect_id(test_app, monkeypatch):
    async def mock_get_note(id):
        return None

    monkeypatch.setattr(note_service, "get_note", mock_get_note)

    response = test_app.get("/api/notes/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"

    response = test_app.get("/api/notes/0/")
    assert response.status_code == 422


def test_read_all_notes(test_app, monkeypatch):
    test_data = [
        {"title": "something", "description": "something else", "id": 1},
        {"title": "someone", "description": "someone else", "id": 2},
    ]

    async def mock_get_all_notes():
        return test_data

    monkeypatch.setattr(note_service, "get_all_notes", mock_get_all_notes)

    response = test_app.get("/api/notes/")
    assert response.status_code == 200
    assert response.json() == test_data


@pytest.mark.parametrize(
    "id, payload, status_code",
    [
        [1, {}, 422],
        [1, {"description": "bar"}, 422],
        [999, {"title": "foo", "description": "bar"}, 404],
        [1, {"title": "1", "description": "bar"}, 422],
        [1, {"title": "foo", "description": "1"}, 422],
        [0, {"title": "foo", "description": "bar"}, 422],
    ],
)
def test_update_note_invalid(test_app, monkeypatch, id, payload, status_code):
    async def mock_get_note(note_id):
        if note_id == 999:
            return None
        return {"id": 1, "title": "old", "description": "old"}

    monkeypatch.setattr(note_service, "get_note", mock_get_note)

    response = test_app.put(
        f"/api/notes/{id}/",
        content=json.dumps(payload),
    )
    assert response.status_code == status_code


def test_remove_note(test_app, monkeypatch):
    test_data = {"title": "something", "description": "something else", "id": 1}

    async def mock_get_note(id):
        return test_data

    monkeypatch.setattr(note_service, "get_note", mock_get_note)

    async def mock_delete_note(id):
        return id

    monkeypatch.setattr(note_service, "delete_note", mock_delete_note)

    response = test_app.delete("/api/notes/1/")
    assert response.status_code == 200
    assert response.json() == test_data


def test_remove_note_incorrect_id(test_app, monkeypatch):
    async def mock_get_note(id):
        return None

    monkeypatch.setattr(note_service, "get_note", mock_get_note)

    response = test_app.delete("/api/notes/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"

    response = test_app.delete("/api/notes/0/")
    assert response.status_code == 422
