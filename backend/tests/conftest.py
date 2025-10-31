import pytest
from starlette.testclient import TestClient
from app.main import app
from app.core.security import create_access_token, get_current_user


@pytest.fixture
def mock_user():
    """モックユーザーデータ"""
    return {
        "id": 1,
        "username": "testuser",
        "is_active": True,
        "created_date": "2024-01-01T00:00:00",
    }


@pytest.fixture
def test_app(mock_user):
    """テスト用のFastAPIクライアント（依存関係をオーバーライド）"""

    async def override_get_current_user():
        return mock_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as client:
        yield client

    # クリーンアップ
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers():
    """認証ヘッダーを生成"""
    token = create_access_token(data={"sub": "testuser"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def mock_current_user(mock_user):
    """モックユーザーを返す（互換性のため）"""
    return mock_user


@pytest.fixture
def test_app_no_auth():
    """認証なしのテスト用FastAPIクライアント"""
    # 依存関係のオーバーライドをクリア
    app.dependency_overrides.clear()

    with TestClient(app) as client:
        yield client

    # クリーンアップ
    app.dependency_overrides.clear()
