#!/bin/bash

# DRF API テストスクリプト
# 使用方法: ./test_api.sh

echo "======================================"
echo "DRF API テストスクリプト"
echo "======================================"
echo ""

# 色付き出力
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# ベースURL
BASE_URL="http://localhost:8000"

# テスト用JWTトークンを生成
echo -e "${YELLOW}[1/9] テスト用JWTトークンを生成中...${NC}"
TOKEN_OUTPUT=$(python manage.py test_supabase_auth 2>&1 | grep -o 'eyJ[A-Za-z0-9_.-]*' | head -1)

if [ -z "$TOKEN_OUTPUT" ]; then
    echo -e "${RED}❌ トークンの生成に失敗しました${NC}"
    echo -e "${RED}エラー詳細:${NC}"
    python manage.py test_supabase_auth 2>&1
    exit 1
fi

TOKEN="$TOKEN_OUTPUT"
echo -e "${GREEN}✅ トークン生成成功${NC}"
echo ""

# テスト2: プロフィール取得（ユーザー自動作成）
echo -e "${YELLOW}[2/9] プロフィール取得（初回 = ユーザー自動作成）${NC}"
RESPONSE=$(curl -s -X GET "$BASE_URL/api/accounts/profile/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

if echo "$RESPONSE" | jq -e '.email' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ プロフィール取得成功${NC}"
    echo "$RESPONSE" | jq '.'
else
    echo -e "${RED}❌ プロフィール取得失敗${NC}"
    echo "$RESPONSE"
fi
echo ""

# テスト3: プロフィール設定状態の確認
echo -e "${YELLOW}[3/9] プロフィール設定状態の確認${NC}"
RESPONSE=$(curl -s -X GET "$BASE_URL/api/accounts/check-profile/" \
  -H "Authorization: Bearer $TOKEN")

if echo "$RESPONSE" | jq -e '.is_complete' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ プロフィール設定状態取得成功${NC}"
    echo "$RESPONSE" | jq '.'
else
    echo -e "${RED}❌ プロフィール設定状態取得失敗${NC}"
    echo "$RESPONSE"
fi
echo ""

# テスト4: username更新
echo -e "${YELLOW}[4/9] username更新${NC}"
RESPONSE=$(curl -s -X PATCH "$BASE_URL/api/accounts/profile/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username": "updated_username"}')

if echo "$RESPONSE" | jq -e '.username' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ username更新成功${NC}"
    echo "$RESPONSE" | jq '.'
else
    echo -e "${RED}❌ username更新失敗${NC}"
    echo "$RESPONSE"
fi
echo ""

# テスト5: ユーザー詳細情報取得
echo -e "${YELLOW}[5/9] ユーザー詳細情報（学習統計）の取得${NC}"
RESPONSE=$(curl -s -X GET "$BASE_URL/api/accounts/detail/" \
  -H "Authorization: Bearer $TOKEN")

if echo "$RESPONSE" | jq -e '.user' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ ユーザー詳細情報取得成功${NC}"
    echo "$RESPONSE" | jq '.'
else
    echo -e "${RED}❌ ユーザー詳細情報取得失敗${NC}"
    echo "$RESPONSE"
fi
echo ""

# テスト6: 認証エラー（トークンなし）
echo -e "${YELLOW}[6/9] 認証エラーテスト（トークンなし）${NC}"
RESPONSE=$(curl -s -X GET "$BASE_URL/api/accounts/profile/")

if echo "$RESPONSE" | jq -e '.detail' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 正しくエラーが返却されました${NC}"
    echo "$RESPONSE" | jq '.'
else
    echo -e "${RED}❌ 予期しないレスポンス${NC}"
    echo "$RESPONSE"
fi
echo ""

# テスト7: 認証エラー（無効なトークン）
echo -e "${YELLOW}[7/9] 認証エラーテスト（無効なトークン）${NC}"
RESPONSE=$(curl -s -X GET "$BASE_URL/api/accounts/profile/" \
  -H "Authorization: Bearer invalid_token_123")

if echo "$RESPONSE" | jq -e '.detail' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 正しくエラーが返却されました${NC}"
    echo "$RESPONSE" | jq '.'
else
    echo -e "${RED}❌ 予期しないレスポンス${NC}"
    echo "$RESPONSE"
fi
echo ""

# テスト8: バリデーションエラー（短すぎるusername）
echo -e "${YELLOW}[8/9] バリデーションエラーテスト（短すぎるusername）${NC}"
RESPONSE=$(curl -s -X PATCH "$BASE_URL/api/accounts/profile/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"username": "a"}')

if echo "$RESPONSE" | jq -e '.username' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 正しくエラーが返却されました${NC}"
    echo "$RESPONSE" | jq '.'
else
    echo -e "${RED}❌ 予期しないレスポンス${NC}"
    echo "$RESPONSE"
fi
echo ""

# テスト9: CORS設定の確認
echo -e "${YELLOW}[9/9] CORS設定の確認${NC}"
HEADERS=$(curl -s -X GET "$BASE_URL/api/accounts/profile/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Origin: http://localhost:3000" \
  -D - -o /dev/null)

if echo "$HEADERS" | grep -qi "access-control-allow-origin"; then
    echo -e "${GREEN}✅ CORS設定が正しく動作しています${NC}"
    echo "$HEADERS" | grep -i "access-control"
else
    echo -e "${RED}❌ CORS設定が見つかりません${NC}"
fi
echo ""

echo "======================================"
echo -e "${GREEN}テスト完了！${NC}"
echo "======================================"
