# curlコマンドによるAPI動作確認ガイド

## 前提条件

```bash
# 1. Djangoサーバーを起動
python manage.py runserver

# 2. 別のターミナルでテストを実行
```

---

## 方法1: 自動テストスクリプト（推奨）

```bash
# スクリプトに実行権限を付与
chmod +x test_api.sh

# テスト実行
./test_api.sh
```

**このスクリプトは以下を自動的にテストします**:

1. JWTトークン生成
2. プロフィール取得（ユーザー自動作成）
3. プロフィール設定状態確認
4. username更新
5. ユーザー詳細情報取得
6. 認証エラー（トークンなし）
7. 認証エラー（無効なトークン）
8. バリデーションエラー（短いusername）
9. CORS設定確認

---

## 方法2: 手動でcurlコマンドを実行

### Step 1: JWTトークンを生成

```bash
python manage.py test_supabase_auth
```

出力されたトークンをコピーして環境変数に設定:

```bash
export TOKEN="ここにトークンを貼り付け"
```

---

### Step 2: 各APIエンドポイントをテスト

#### 2-1. プロフィール取得（GET）

```bash
curl -X GET http://localhost:8000/api/accounts/profile/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" | jq
```

**期待結果**: ユーザー情報が返却される

---

#### 2-2. プロフィール設定状態確認（GET）

```bash
curl -X GET http://localhost:8000/api/accounts/check-profile/ \
  -H "Authorization: Bearer $TOKEN" | jq
```

**期待結果**:

```json
{
  "is_complete": true/false,
  "needs_username": true/false,
  "user": { ... }
}
```

---

#### 2-3. username更新（PATCH）

```bash
curl -X PATCH http://localhost:8000/api/accounts/profile/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username": "new_username"}' | jq
```

**期待結果**: 更新されたユーザー情報が返却される

---

#### 2-4. 初回プロフィール設定（POST）

**前提**: usernameが初期値（@を含む）の場合のみ動作

```bash
curl -X POST http://localhost:8000/api/accounts/complete-profile/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username": "my_username"}' | jq
```

**期待結果**:

```json
{
  "message": "プロフィールを設定しました",
  "user": { ... }
}
```

---

#### 2-5. ユーザー詳細情報取得（GET）

```bash
curl -X GET http://localhost:8000/api/accounts/detail/ \
  -H "Authorization: Bearer $TOKEN" | jq
```

**期待結果**: ユーザー情報 + 学習統計が返却される

---

### Step 3: エラーケースのテスト

#### 3-1. 認証エラー（トークンなし）

```bash
curl -X GET http://localhost:8000/api/accounts/profile/ | jq
```

**期待結果**:

```json
{
  "detail": "認証情報が含まれていません。"
}
```

---

#### 3-2. 認証エラー（無効なトークン）

```bash
curl -X GET http://localhost:8000/api/accounts/profile/ \
  -H "Authorization: Bearer invalid_token" | jq
```

**期待結果**:

```json
{
  "detail": "無効なトークンです"
}
```

---

#### 3-3. バリデーションエラー（短いusername）

```bash
curl -X PATCH http://localhost:8000/api/accounts/profile/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username": "a"}' | jq
```

**期待結果**:

```json
{
  "username": ["ユーザー名は2文字以上にしてください"]
}
```

---

#### 3-4. バリデーションエラー（usernameが空）

```bash
curl -X POST http://localhost:8000/api/accounts/complete-profile/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}' | jq
```

**期待結果**:

```json
{
  "username": ["ユーザー名を入力してください"]
}
```

---

### Step 4: CORS設定の確認

```bash
curl -X GET http://localhost:8000/api/accounts/profile/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Origin: http://localhost:3000" \
  -v 2>&1 | grep -i "access-control"
```

**期待結果**:

```
< Access-Control-Allow-Origin: http://localhost:3000
< Access-Control-Allow-Credentials: true
```

---

## トラブルシューティング

### エラー: "SUPABASE_JWT_SECRET must be set in .env file"

**原因**: `.env`ファイルに`SUPABASE_JWT_SECRET`が設定されていない

**解決方法**:

```bash
# .envファイルに追加
echo "SUPABASE_JWT_SECRET=your-secret-here" >> .env
```

---

### エラー: "jq: command not found"

**原因**: `jq`がインストールされていない

**解決方法**:

```bash
# macOS
brew install jq

# Ubuntu/Debian
sudo apt-get install jq

# またはjqなしで実行
curl -X GET http://localhost:8000/api/accounts/profile/ \
  -H "Authorization: Bearer $TOKEN"
```

---

### エラー: "relation "custom_user" does not exist"

**原因**: マイグレーションが実行されていない

**解決方法**:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### エラー: "ModuleNotFoundError: No module named 'rest_framework'"

**原因**: 必要なパッケージがインストールされていない

**解決方法**:

```bash
pip install -r requirements.txt
```

---

## 成功判定基準

以下がすべて成功すればPhase 1完了です：

- [ ] テスト用JWTトークンが生成できる
- [ ] プロフィール取得でユーザーが自動作成される
- [ ] username更新が動作する
- [ ] 認証エラーが正しく返される
- [ ] バリデーションエラーが正しく返される
- [ ] CORS設定が動作している
- [ ] 既存のDjango Templateログインが正常動作（手動確認）

---

## 次のステップ

Phase 1のテストが成功したら:

1. すべての変更をGitにcommit & push
2. Phase 2（Next.js側の実装）に進む
