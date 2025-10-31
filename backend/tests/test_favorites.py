"""お気に入りAPIのテスト"""

from app.services import favorite_service


def test_add_favorite(test_app, auth_headers, mock_current_user, monkeypatch):
    """お気に入り追加のテスト"""
    test_payload = {"note_id": 1}

    async def mock_add_favorite(payload, user_id):
        return {
            "id": 1,
            "note_id": 1,
            "user_id": user_id,
            "created_date": "2024-01-01T00:00:00",
        }

    monkeypatch.setattr(favorite_service, "add_favorite", mock_add_favorite)

    response = test_app.post("/api/favorites", json=test_payload, headers=auth_headers)

    assert response.status_code == 201
    assert response.json()["note_id"] == 1


def test_add_favorite_not_found(test_app, auth_headers, mock_current_user, monkeypatch):
    """存在しないノートのお気に入り追加テスト"""
    test_payload = {"note_id": 999}

    async def mock_add_favorite(payload, user_id):
        return None

    monkeypatch.setattr(favorite_service, "add_favorite", mock_add_favorite)

    response = test_app.post("/api/favorites", json=test_payload, headers=auth_headers)

    assert response.status_code == 404


def test_remove_favorite(test_app, auth_headers, mock_current_user, monkeypatch):
    """お気に入り削除のテスト"""

    async def mock_remove_favorite(note_id, user_id):
        return 1

    monkeypatch.setattr(favorite_service, "remove_favorite", mock_remove_favorite)

    response = test_app.delete("/api/favorites/1", headers=auth_headers)

    assert response.status_code == 204


def test_remove_favorite_not_found(
    test_app, auth_headers, mock_current_user, monkeypatch
):
    """存在しないお気に入りの削除テスト"""

    async def mock_remove_favorite(note_id, user_id):
        return 0

    monkeypatch.setattr(favorite_service, "remove_favorite", mock_remove_favorite)

    response = test_app.delete("/api/favorites/999", headers=auth_headers)

    assert response.status_code == 404


def test_get_favorites(test_app, auth_headers, mock_current_user, monkeypatch):
    """お気に入り一覧取得のテスト"""
    test_data = [
        {
            "id": 1,
            "title": "Favorite Note 1",
            "content": "Content 1",
            "user_id": 1,
            "created_date": "2024-01-01T00:00:00",
            "updated_date": "2024-01-01T00:00:00",
        },
        {
            "id": 2,
            "title": "Favorite Note 2",
            "content": "Content 2",
            "user_id": 1,
            "created_date": "2024-01-02T00:00:00",
            "updated_date": "2024-01-02T00:00:00",
        },
    ]

    async def mock_get_favorites(user_id):
        return test_data

    monkeypatch.setattr(favorite_service, "get_favorites", mock_get_favorites)

    response = test_app.get("/api/favorites", headers=auth_headers)

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_check_favorite(test_app, auth_headers, mock_current_user, monkeypatch):
    """お気に入りチェックのテスト"""

    async def mock_is_favorite(note_id, user_id):
        return True

    monkeypatch.setattr(favorite_service, "is_favorite", mock_is_favorite)

    response = test_app.get("/api/favorites/1/check", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["is_favorite"] is True


def test_check_favorite_not_favorite(
    test_app, auth_headers, mock_current_user, monkeypatch
):
    """お気に入りでないノートのチェックテスト"""

    async def mock_is_favorite(note_id, user_id):
        return False

    monkeypatch.setattr(favorite_service, "is_favorite", mock_is_favorite)

    response = test_app.get("/api/favorites/999/check", headers=auth_headers)

    assert response.status_code == 200
    assert response.json()["is_favorite"] is False


def test_favorites_unauthorized(test_app_no_auth):
    """認証なしでのお気に入り操作テスト"""
    # 一覧取得
    response = test_app_no_auth.get("/api/favorites")
    assert response.status_code == 401

    # 追加
    response = test_app_no_auth.post("/api/favorites", json={"note_id": 1})
    assert response.status_code == 401

    # 削除
    response = test_app_no_auth.delete("/api/favorites/1")
    assert response.status_code == 401

    # チェック
    response = test_app_no_auth.get("/api/favorites/1/check")
    assert response.status_code == 401
