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

Render は`render.yaml`ファイルを使った Blueprint 方式でデプロイします。

### 2.1 Blueprint からデプロイ（推奨）

1. Render ダッシュボード（https://dashboard.render.com）にアクセス
2. 「New +」→「Blueprint」を選択
3. GitHub リポジトリ `memoria-app` を接続
4. Render が自動的に`render.yaml`を検出します
5. サービス名やプランを確認して「Apply」をクリック

これで PostgreSQL データベースとバックエンド Web Service が自動的に作成されます。

### 2.2 環境変数の設定

Blueprint が作成されたら、以下の環境変数を手動で設定します：

1. `memoria-backend` サービスを開く
2. 「Environment」タブで以下を追加：
   - `FRONTEND_URL`: 後で設定（Vercel のデプロイ後）
   - `OPENAI_API_KEY`: OpenAI API キー（オプション）
   - `ANTHROPIC_API_KEY`: Anthropic API キー（オプション）
   - `GEMINI_API_KEY`: Google Gemini API キー（オプション）

注: `DATABASE_URL`、`SECRET_KEY`、`ALGORITHM`、`ACCESS_TOKEN_EXPIRE_MINUTES`は`render.yaml`で自動設定されます。

3. デプロイ完了後、URL をコピー（例：`https://memoria-backend.onrender.com`）

### 2.3 手動デプロイの場合（Blueprint を使わない場合）

もし Blueprint 方式を使わない場合は、以下の手順で手動デプロイできます：

**PostgreSQL データベースの作成**

1. 「New +」→「PostgreSQL」
2. Name: `memoria-db`
3. Plan: Free
4. 「Create Database」をクリック
5. Internal Database URL をコピー

**Web Service の作成**

1. 「New +」→「Web Service」
2. GitHub リポジトリを接続
3. 設定：
   - Name: `memoria-backend`
   - Runtime: Python 3
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Plan: Free
4. 環境変数を手動で設定（上記 2.2 参照 + DATABASE_URL など）

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
