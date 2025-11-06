# Memoria

AI 搭載のアイデア生成機能、ユーザー認証、お気に入り管理を備えたモダンなノートアプリケーション。

[English](README.md) | 日本語

## 機能

- 📝 リッチテキスト対応のノート作成・編集・削除
- ⭐ お気に入りノート機能でクイックアクセス
- 🤖 AI 搭載のアイデア生成（OpenAI、Anthropic、Google Gemini 対応）
- 🔐 JWT による安全なユーザー認証
- 📤 ノートをテキストファイルとしてエクスポート
- 🎨 React と Tailwind CSS によるクリーンでレスポンシブな UI
- 🚀 高速でモダンな技術スタック

## 技術スタック

### フロントエンド

- React 18
- TypeScript
- Vite
- React Router
- Zustand（状態管理）
- Axios
- Tailwind CSS

### バックエンド

- FastAPI
- Python 3.11+
- PostgreSQL
- SQLAlchemy
- JWT 認証
- OpenAI / Anthropic / Google Gemini API

## はじめに

### 必要要件

- Node.js 18+
- Python 3.11+
- PostgreSQL（または Docker を使用）

### ローカル開発

1. リポジトリをクローン

```bash
git clone https://github.com/YOUR_USERNAME/memoria-app.git
cd memoria-app
```

2. バックエンドのセットアップ

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.sample .env
# .envファイルを編集してデータベース認証情報とAPIキーを設定
uvicorn app.main:app --reload
```

3. フロントエンドのセットアップ

```bash
cd frontend
npm install
npm run dev
```

4. アプリケーションにアクセス

- フロントエンド: http://localhost:5173
- バックエンド API: http://localhost:8000
- API ドキュメント: http://localhost:8000/docs

## 環境変数

### バックエンド (.env)

```
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/memoria_db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
FRONTEND_URL=http://localhost:5173

# オプション: AI APIキー（ローカル開発環境のみ）
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GEMINI_API_KEY=your-gemini-api-key
```

**注意:** AI 機能は予期しない API 料金を防ぐため、本番環境では無効化されています。AI アイデア生成機能を使用するには、ローカル環境で独自の API キーを設定して実行してください。

### フロントエンド (.env)

```
VITE_API_URL=http://localhost:8000
```

## デプロイ

Vercel（フロントエンド）と Render（バックエンド）を使用した詳細なデプロイ手順については、[DEPLOYMENT.md](DEPLOYMENT.md)を参照してください。

## API ドキュメント

バックエンドを起動後、http://localhost:8000/docs にアクセスすると、Swagger UI によるインタラクティブな API ドキュメントを閲覧できます。

## ライセンス

MIT ライセンス - 学習や個人プロジェクトでの使用は自由です。

## コントリビューション

コントリビューションを歓迎します！プルリクエストをお気軽に送信してください。
