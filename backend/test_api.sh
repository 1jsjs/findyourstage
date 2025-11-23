#!/bin/bash

echo "=== Testing FindYourStage API ==="
echo ""

echo "1. 회원가입 테스트..."
REGISTER_RESPONSE=$(curl -s -X POST 'http://localhost:8000/api/users/register' \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@example.com","password":"password123","name":"Test User"}')
echo "$REGISTER_RESPONSE" | python3 -m json.tool
TOKEN=$(echo "$REGISTER_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)
echo ""

echo "2. 로그인 테스트..."
LOGIN_RESPONSE=$(curl -s -X POST 'http://localhost:8000/api/users/login' \
  -H 'Content-Type: application/json' \
  -d '{"email":"test@example.com","password":"password123"}')
echo "$LOGIN_RESPONSE" | python3 -m json.tool
echo ""

echo "3. 사용자 정보 조회..."
curl -s -X GET 'http://localhost:8000/api/users/me' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "4. 북마크 추가..."
curl -s -X POST 'http://localhost:8000/api/users/me/bookmarks' \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"concert_id":"PF123456","concert_name":"Test Concert","poster_url":"http://example.com/poster.jpg"}' | python3 -m json.tool
echo ""

echo "5. 북마크 목록 조회..."
curl -s -X GET 'http://localhost:8000/api/users/me/bookmarks' \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
echo ""

echo "6. 북마크 삭제..."
curl -s -X DELETE 'http://localhost:8000/api/users/me/bookmarks/PF123456' \
  -H "Authorization: Bearer $TOKEN"
echo "Deleted successfully!"
echo ""

echo "=== 모든 테스트 완료! ==="
