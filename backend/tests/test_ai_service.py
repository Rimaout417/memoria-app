"""AI Service のテスト"""

import pytest
from fastapi import HTTPException
from app.services import ai_service


@pytest.mark.asyncio
async def test_get_notes_for_context_success(monkeypatch):
    """正常系: 複数ノートの取得成功"""
    test_notes = [
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

    async def mock_fetch_all(query):
        return test_notes

    from app import database

    monkeypatch.setattr(database.database, "fetch_all", mock_fetch_all)

    result = await ai_service.get_notes_for_context([1, 2], user_id=1)

    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[1]["id"] == 2


@pytest.mark.asyncio
async def test_get_notes_for_context_not_found(monkeypatch):
    """異常系: ノートが見つからない"""

    async def mock_fetch_all(query):
        return []

    from app import database

    monkeypatch.setattr(database.database, "fetch_all", mock_fetch_all)

    with pytest.raises(HTTPException) as exc:
        await ai_service.get_notes_for_context([999], user_id=1)

    assert exc.value.status_code == 404
    assert "not found" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_get_notes_for_context_partial_found(monkeypatch):
    """異常系: 一部のノートのみ見つかる"""
    test_notes = [
        {
            "id": 1,
            "title": "Note 1",
            "content": "Content 1",
            "user_id": 1,
            "created_date": "2024-01-01T00:00:00",
            "updated_date": "2024-01-01T00:00:00",
        }
    ]

    async def mock_fetch_all(query):
        return test_notes

    from app import database

    monkeypatch.setattr(database.database, "fetch_all", mock_fetch_all)

    with pytest.raises(HTTPException) as exc:
        await ai_service.get_notes_for_context([1, 2, 3], user_id=1)

    assert exc.value.status_code == 404
    assert "2" in exc.value.detail
    assert "3" in exc.value.detail


def test_build_context_from_notes():
    """正常系: ノートからコンテキストを構築"""
    notes = [
        {"id": 1, "title": "Note 1", "content": "Content 1"},
        {"id": 2, "title": "Note 2", "content": "Content 2"},
    ]

    context = ai_service.build_context_from_notes(notes)

    assert "# Note 1" in context
    assert "Content 1" in context
    assert "# Note 2" in context
    assert "Content 2" in context
    assert "---" in context


def test_build_context_from_notes_empty():
    """正常系: 空のノートリスト"""
    context = ai_service.build_context_from_notes([])

    assert context == ""


def test_build_context_from_notes_single():
    """正常系: 単一ノート"""
    notes = [{"id": 1, "title": "Single Note", "content": "Single Content"}]

    context = ai_service.build_context_from_notes(notes)

    assert "# Single Note" in context
    assert "Single Content" in context
    assert context.count("---") == 0  # 単一ノートの場合は区切り文字なし


@pytest.mark.asyncio
async def test_generate_idea_basic(monkeypatch):
    """正常系: 基本的なアイデア生成"""
    test_notes = [
        {
            "id": 1,
            "title": "Test Note",
            "content": "Test Content",
            "user_id": 1,
            "created_date": "2024-01-01T00:00:00",
            "updated_date": "2024-01-01T00:00:00",
        }
    ]

    async def mock_fetch_all(query):
        return test_notes

    async def mock_fetch_one(query):
        return {
            "id": 1,
            "user_id": 1,
            "note_ids": [1],
            "prompt": "Test prompt",
            "ai_provider": "openai",
            "generated_content": "Generated test content",
            "created_date": "2024-01-01T00:00:00",
        }

    async def mock_execute(query):
        return 1

    # Mock AI provider
    class MockAIProvider:
        async def generate(self, prompt, context):
            return "Generated test content"

    def mock_get_provider(provider_name):
        return MockAIProvider()

    from app import database

    monkeypatch.setattr(database.database, "fetch_all", mock_fetch_all)
    monkeypatch.setattr(database.database, "fetch_one", mock_fetch_one)
    monkeypatch.setattr(database.database, "execute", mock_execute)
    monkeypatch.setattr(ai_service, "get_ai_provider", mock_get_provider)

    result = await ai_service.generate_idea(
        note_ids=[1], user_id=1, prompt="Test prompt", ai_provider="openai"
    )

    assert result["id"] == 1
    assert result["note_ids"] == [1]
    assert result["prompt"] == "Test prompt"
    assert result["ai_provider"] == "openai"
    assert result["generated_content"] == "Generated test content"


@pytest.mark.asyncio
async def test_generate_idea_default_prompt(monkeypatch):
    """正常系: デフォルトプロンプトの使用"""
    test_notes = [
        {
            "id": 1,
            "title": "Test Note",
            "content": "Test Content",
            "user_id": 1,
            "created_date": "2024-01-01T00:00:00",
            "updated_date": "2024-01-01T00:00:00",
        }
    ]

    async def mock_fetch_all(query):
        return test_notes

    async def mock_fetch_one(query):
        return {
            "id": 1,
            "user_id": 1,
            "note_ids": [1],
            "prompt": "これらのノートから新しいアイデアを生成してください",
            "ai_provider": "openai",
            "generated_content": "Generated content",
            "created_date": "2024-01-01T00:00:00",
        }

    async def mock_execute(query):
        return 1

    # Mock AI provider
    class MockAIProvider:
        async def generate(self, prompt, context):
            return "Generated content"

    def mock_get_provider(provider_name):
        return MockAIProvider()

    from app import database

    monkeypatch.setattr(database.database, "fetch_all", mock_fetch_all)
    monkeypatch.setattr(database.database, "fetch_one", mock_fetch_one)
    monkeypatch.setattr(database.database, "execute", mock_execute)
    monkeypatch.setattr(ai_service, "get_ai_provider", mock_get_provider)

    result = await ai_service.generate_idea(note_ids=[1], user_id=1)

    assert result["prompt"] == "これらのノートから新しいアイデアを生成してください"


@pytest.mark.asyncio
async def test_generate_idea_note_not_found(monkeypatch):
    """異常系: ノートが見つからない場合"""

    async def mock_fetch_all(query):
        return []

    from app import database

    monkeypatch.setattr(database.database, "fetch_all", mock_fetch_all)

    with pytest.raises(HTTPException) as exc:
        await ai_service.generate_idea(note_ids=[999], user_id=1)

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_generations(monkeypatch):
    """正常系: 生成履歴の取得"""
    test_generations = [
        {
            "id": 1,
            "user_id": 1,
            "note_ids": [1, 2],
            "prompt": "Test prompt",
            "ai_provider": "openai",
            "generated_content": "Generated content",
            "created_date": "2024-01-01T00:00:00",
        }
    ]

    async def mock_fetch_all(query):
        return test_generations

    async def mock_fetch_val(query):
        return 1

    from app import database

    monkeypatch.setattr(database.database, "fetch_all", mock_fetch_all)
    monkeypatch.setattr(database.database, "fetch_val", mock_fetch_val)

    result = await ai_service.get_generations(user_id=1, page=1, per_page=20)

    assert result["total"] == 1
    assert result["page"] == 1
    assert result["per_page"] == 20
    assert len(result["items"]) == 1
    assert result["items"][0]["id"] == 1


@pytest.mark.asyncio
async def test_save_generation_as_note(monkeypatch):
    """正常系: 生成結果をノートとして保存"""
    test_generation = {
        "id": 1,
        "user_id": 1,
        "note_ids": [1],
        "prompt": "Test prompt",
        "ai_provider": "openai",
        "generated_content": "Generated content to save",
        "created_date": "2024-01-01T00:00:00",
    }

    test_note = {
        "id": 10,
        "title": "New Note",
        "content": "Generated content to save",
        "user_id": 1,
        "created_date": "2024-01-01T00:00:00",
        "updated_date": "2024-01-01T00:00:00",
    }

    async def mock_fetch_one(query):
        # 最初の呼び出しは生成履歴、2回目はノート
        if not hasattr(mock_fetch_one, "call_count"):
            mock_fetch_one.call_count = 0
        mock_fetch_one.call_count += 1

        if mock_fetch_one.call_count == 1:
            return test_generation
        else:
            return test_note

    async def mock_execute(query):
        return 10

    from app import database

    monkeypatch.setattr(database.database, "fetch_one", mock_fetch_one)
    monkeypatch.setattr(database.database, "execute", mock_execute)

    result = await ai_service.save_generation_as_note(
        generation_id=1, user_id=1, title="New Note"
    )

    assert result["id"] == 10
    assert result["title"] == "New Note"
    assert result["content"] == "Generated content to save"


@pytest.mark.asyncio
async def test_save_generation_as_note_not_found(monkeypatch):
    """異常系: 生成履歴が見つからない"""

    async def mock_fetch_one(query):
        return None

    from app import database

    monkeypatch.setattr(database.database, "fetch_one", mock_fetch_one)

    with pytest.raises(HTTPException) as exc:
        await ai_service.save_generation_as_note(
            generation_id=999, user_id=1, title="New Note"
        )

    assert exc.value.status_code == 404
