# デプロイ手順

## 前提条件

- GitHub アカウント
- Vercel アカウント（フロントエンド用）
- Render アカウント（バックエンド用）

## 1. GitHub にプッシュ

```bash
git add .
git commit -m "Add deployment configuration"
git push origin main
```

## 2. バックエンドのデプロイ（Render）

### 2.1 PostgreSQL データベースの作成

1. Render ダッシュボードで「New +」→「PostgreSQL」を選択
2. 名前を入力（例：`memoria-db`）
3. 無料プランを選択
4. 「Create Database」をクリック
5. データベースの「Internal Database URL」をコピー

### 2.2 Web Service の作成

1. Render ダッシュボードで「New +」→「Web Service」を選択
2. GitHub リポジトリを接続
3. 以下の設定を入力：

   - **Name**: `memoria-backend`（任意）
   - **Region**: Oregon（無料プラン）
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

4. 環境変数を設定：

   - `DATABASE_URL`: 先ほどコピーした PostgreSQL の URL
   - `SECRET_KEY`: ランダムな文字列（例：`openssl rand -hex 32`で生成）
   - `ALGORITHM`: `HS256`
   - `ACCESS_TOKEN_EXPIRE_MINUTES`: `30`
   - `OPENAI_API_KEY`: OpenAI API キー（オプション）
   - `ANTHROPIC_API_KEY`: Anthropic API キー（オプション）
   - `GEMINI_API_KEY`: Google Gemini API キー（オプション）
   - `FRONTEND_URL`: 後で設定（Vercel のデプロイ後）

5. 「Create Web Service」をクリック

6. デプロイ完了後、URL をコピー（例：`https://memoria-backend.onrender.com`）

## 3. フロントエンドのデプロイ（Vercel）

### 3.1 プロジェクトのインポート

1. Vercel ダッシュボードで「Add New...」→「Project」を選択
2. GitHub リポジトリをインポート
3. 以下の設定を入力：
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### 3.2 環境変数の設定

1. 「Environment Variables」セクションで以下を追加：

   - **Name**: `VITE_API_URL`
   - **Value**: Render のバックエンド URL（例：`https://memoria-backend.onrender.com`）

2. 「Deploy」をクリック

3. デプロイ完了後、URL をコピー（例：`https://your-app.vercel.app`）

## 4. バックエンドの環境変数を更新

1. Render のダッシュボードでバックエンドの Web Service を開く
2. 「Environment」タブで`FRONTEND_URL`を追加：
   - **Key**: `FRONTEND_URL`
   - **Value**: Vercel のフロントエンド URL（例：`https://your-app.vercel.app`）
3. 「Save Changes」をクリック（自動的に再デプロイされます）

## 5. 動作確認

1. Vercel の URL にアクセス
2. ユーザー登録とログインをテスト
3. ノートの作成・編集・削除をテスト
4. AI 機能をテスト（API キーを設定している場合）

## トラブルシューティング

### Render の無料プランの制限

- 15 分間アクセスがないとスリープ状態になります
- 初回アクセス時は起動に 30 秒〜1 分かかります
- データベースは 90 日間のデータ保持制限があります

### CORS エラーが出る場合

- バックエンドの`FRONTEND_URL`環境変数が正しく設定されているか確認
- Render のサービスが再起動されているか確認

### データベース接続エラー

- `DATABASE_URL`が正しく設定されているか確認
- PostgreSQL データベースが起動しているか確認

## 更新方法

GitHub にプッシュすると自動的にデプロイされます：

```bash
git add .
git commit -m "Update feature"
git push origin main
```

- Vercel: 自動デプロイ（約 1-2 分）
- Render: 自動デプロイ（約 3-5 分）
