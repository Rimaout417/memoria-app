# AI アイデア生成機能 - 統合テストガイド

このガイドでは、AI アイデア生成機能のエンドツーエンド検証を行います。

## 前提条件

1. Docker 環境でバックエンドが起動していること

   ```bash
   docker-compose up
   ```

2. バックエンドが http://localhost:8000 で稼働していること

3. OpenAI API キーが `.env` ファイルに設定されていること

## テスト実行方法

### 方法 1: 自動テストスクリプト（推奨）

```bash
# Dockerコンテナ内で実行
docker-compose exec backend python test_integration.py
```

### 方法 2: 手動テスト（curl コマンド）

以下の手順で手動テストを実行できます。

#### 1. ユーザー登録

```bash
curl -X POST http://localhost:8000/api/auth/register ^
  -H "Content-Type: application/json" ^
  -d "{\"username\":\"testuser\",\"email\":\"test@example.com\",\"password\":\"TestPass123!\"}"
```

期待される結果: ステータスコード 200、ユーザー情報が返される

#### 2. ログイン

```bash
curl -X POST http://localhost:8000/api/auth/login ^
  -H "Content-Type: application/x-www-form-urlencoded" ^
  -d "username=testuser&password=TestPass123!"
```

期待される結果: ステータスコード 200、`access_token` が返される

**重要**: 返された `access_token` を以下の `YOUR_TOKEN` に置き換えてください。

#### 3. ノート作成

```bash
curl -X POST http://localhost:8000/api/notes ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer YOUR_TOKEN" ^
  -d "{\"title\":\"プロジェクトアイデア1\",\"body\":\"AIを活用した学習支援アプリケーションの開発\"}"
```

期待される結果: ステータスコード 200、ノート情報（`id` を含む）が返される

**重要**: 返された `id` を記録してください（例: `note_id=1`）

#### 4. AI アイデア生成（OpenAI）

```bash
curl -X POST http://localhost:8000/api/ai/generate-idea ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer YOUR_TOKEN" ^
  -d "{\"note_ids\":[1],\"prompt\":\"このアイデアを発展させてください\",\"ai_provider\":\"openai\"}"
```

期待される結果:

- ステータスコード 200
- `generated_content` に AI が生成したアイデアが含まれる
- `ai_provider` が "openai"
- `generation_id` が返される

#### 5. AI アイデア生成（Gemini）

```bash
curl -X POST http://localhost:8000/api/ai/generate-idea ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer YOUR_TOKEN" ^
  -d "{\"note_ids\":[1],\"prompt\":\"このアイデアを発展させてください\",\"ai_provider\":\"gemini\"}"
```

期待される結果:

- ステータスコード 200
- `ai_provider` が "gemini"

#### 6. 生成履歴の取得

```bash
curl -X GET http://localhost:8000/api/ai/generations ^
  -H "Authorization: Bearer YOUR_TOKEN"
```

期待される結果:

- ステータスコード 200
- `items` 配列に生成履歴が含まれる
- `total` に総件数が表示される

#### 7. 特定の生成履歴の取得

```bash
curl -X GET http://localhost:8000/api/ai/generations/1 ^
  -H "Authorization: Bearer YOUR_TOKEN"
```

期待される結果:

- ステータスコード 200
- 指定した生成履歴の詳細が返される

## エラーケースのテスト

### 1. 無効なノート ID

```bash
curl -X POST http://localhost:8000/api/ai/generate-idea ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer YOUR_TOKEN" ^
  -d "{\"note_ids\":[99999],\"ai_provider\":\"openai\"}"
```

期待される結果: ステータスコード 404

### 2. 無効な AI プロバイダー

```bash
curl -X POST http://localhost:8000/api/ai/generate-idea ^
  -H "Content-Type: application/json" ^
  -H "Authorization: Bearer YOUR_TOKEN" ^
  -d "{\"note_ids\":[1],\"ai_provider\":\"invalid_provider\"}"
```

期待される結果: ステータスコード 422（バリデーションエラー）

### 3. 認証なしアクセス

```bash
curl -X POST http://localhost:8000/api/ai/generate-idea ^
  -H "Content-Type: application/json" ^
  -d "{\"note_ids\":[1],\"ai_provider\":\"openai\"}"
```

期待される結果: ステータスコード 401

### 4. 他のユーザーのノートへのアクセス

別のユーザーでログインして、最初のユーザーのノート ID を使用してアイデア生成を試みます。

期待される結果: ステータスコード 404（ノートが見つからない）

### 5. レート制限テスト

1 時間に 11 回以上リクエストを送信します。

```bash
# 11回連続でリクエスト
for /L %i in (1,1,11) do curl -X POST http://localhost:8000/api/ai/generate-idea -H "Content-Type: application/json" -H "Authorization: Bearer YOUR_TOKEN" -d "{\"note_ids\":[1],\"ai_provider\":\"openai\"}"
```

期待される結果: 11 回目のリクエストでステータスコード 429（Too Many Requests）

## フロントエンドでの動作確認

### 1. フロントエンド起動

```bash
cd frontend
npm run dev
```

ブラウザで http://localhost:5173 にアクセス

### 2. UI からの動作確認

1. **ユーザー登録/ログイン**

   - 新規ユーザーを登録
   - ログインしてダッシュボードに移動

2. **ノート作成**

   - 「Notes」ページでノートを作成
   - タイトルと本文を入力

3. **AI アイデア生成**

   - ノート一覧でノートを選択
   - 「Generate AI Idea」ボタンをクリック
   - モーダルでプロンプトを入力
   - AI プロバイダーを選択（OpenAI または Gemini）
   - 「Generate」ボタンをクリック
   - 生成されたアイデアが表示されることを確認

4. **生成履歴の確認**

   - 「Generation History」ページに移動
   - 過去の生成履歴が一覧表示されることを確認
   - 各履歴の詳細を確認

5. **エラーケースの確認**
   - 無効なノート ID で生成を試みる → エラーメッセージが表示される
   - ネットワークエラーをシミュレート → 適切なエラーハンドリングが行われる

## テスト結果の確認ポイント

### 正常系

- ✅ ユーザー登録とログインが正常に動作する
- ✅ ノートの作成が正常に動作する
- ✅ OpenAI API を使用したアイデア生成が成功する
- ✅ Gemini API を使用したアイデア生成が成功する
- ✅ 生成履歴の取得が正常に動作する
- ✅ 生成されたコンテンツが適切に表示される

### エラーケース

- ✅ 無効なノート ID で 404 エラーが返される
- ✅ 無効な AI プロバイダーで 422 エラーが返される
- ✅ 認証なしアクセスで 401 エラーが返される
- ✅ 他のユーザーのノートにアクセスできない
- ✅ レート制限が正しく機能する（1 時間に 10 回まで）

### パフォーマンス

- ✅ AI 生成のレスポンスタイムが 30 秒以内
- ✅ 生成履歴の取得が 1 秒以内

## トラブルシューティング

### バックエンドが起動しない

```bash
docker-compose logs backend
```

でログを確認してください。

### API キーのエラー

`.env` ファイルに正しい API キーが設定されているか確認してください。

### データベース接続エラー

```bash
docker-compose restart db
docker-compose restart backend
```

### フロントエンドがバックエンドに接続できない

`frontend/.env` または `frontend/vite.config.ts` で API の URL が正しく設定されているか確認してください。

## 完了チェックリスト

- [ ] Docker 環境でバックエンドが正常に起動
- [ ] ユーザー登録とログインが動作
- [ ] ノート作成が動作
- [ ] OpenAI API でのアイデア生成が成功
- [ ] Gemini API でのアイデア生成が成功
- [ ] 生成履歴の取得が動作
- [ ] エラーケース（無効なノート ID）が正しく処理される
- [ ] エラーケース（無効なプロバイダー）が正しく処理される
- [ ] エラーケース（認証なし）が正しく処理される
- [ ] フロントエンドからの動作確認が完了
- [ ] UI でのエラーハンドリングが適切

すべてのチェックが完了したら、統合テストは成功です！
