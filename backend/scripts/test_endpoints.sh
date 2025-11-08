#!/bin/bash
# TextLab Backend - Endpoint Testing Script
# Usage: ./scripts/test_endpoints.sh [API_URL] [EMAIL] [PASSWORD]

set -e

API_URL="${1:-http://localhost:8000/api/v1}"
EMAIL="${2:-test@example.com}"
PASSWORD="${3:-TestPassword123!}"

echo "🧪 Testing TextLab Backend Endpoints"
echo "API URL: $API_URL"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# Helper
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local token=$4
    local expected_status=$5
    
    if [ -n "$token" ]; then
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$API_URL$endpoint" \
            -H "Authorization: Bearer $token" \
            -H "Content-Type: application/json" \
            ${data:+-d "$data"})
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$API_URL$endpoint" \
            -H "Content-Type: application/json" \
            ${data:+-d "$data"})
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✓${NC} $method $endpoint -> $http_code"
        echo "$body" | jq '.' 2>/dev/null || echo "$body"
        return 0
    else
        echo -e "${RED}✗${NC} $method $endpoint -> $http_code (expected $expected_status)"
        echo "$body"
        return 1
    fi
    echo ""
}

# 1. Register
echo -e "${BLUE}1. Authentication${NC}"
echo "-------------------"
REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/auth/register" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$EMAIL\",
        \"full_name\": \"Test User\",
        \"password\": \"$PASSWORD\",
        \"role\": \"student\"
    }")

HTTP_CODE=$(echo "$REGISTER_RESPONSE" | tail -n1)
if [ "$HTTP_CODE" = "201" ] || [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓${NC} POST /auth/register -> $HTTP_CODE"
    TOKEN=$(echo "$REGISTER_RESPONSE" | jq -r '.access_token // empty')
else
    echo -e "${RED}✗${NC} POST /auth/register -> $HTTP_CODE"
    # Try login instead
    LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$EMAIL\",
            \"password\": \"$PASSWORD\"
        }")
    TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token // empty')
fi

if [ -z "$TOKEN" ] || [ "$TOKEN" = "null" ]; then
    echo -e "${RED}✗${NC} Failed to get access token"
    exit 1
fi

echo "Token: ${TOKEN:0:20}..."
echo ""

# 2. Get current user
echo -e "${BLUE}2. User Endpoints${NC}"
echo "-----------------"
test_endpoint "GET" "/users/me" "" "$TOKEN" "200"
echo ""

# 3. Documents CRUD
echo -e "${BLUE}3. Documents CRUD${NC}"
echo "----------------"

# Create
CREATE_RESPONSE=$(curl -s -X POST "$API_URL/documents" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "title": "Test Document",
        "content": "# Test\n\nThis is a test document.",
        "metadata": {"language": "en"},
        "is_public": false
    }')

DOC_ID=$(echo "$CREATE_RESPONSE" | jq -r '.id // empty')
if [ -n "$DOC_ID" ] && [ "$DOC_ID" != "null" ]; then
    echo -e "${GREEN}✓${NC} POST /documents -> Created (ID: $DOC_ID)"
else
    echo -e "${RED}✗${NC} POST /documents -> Failed"
    exit 1
fi

# List
test_endpoint "GET" "/documents?page=1&per_page=10" "" "$TOKEN" "200"

# Get
test_endpoint "GET" "/documents/$DOC_ID" "" "$TOKEN" "200"

# Update
test_endpoint "PUT" "/documents/$DOC_ID" '{"title": "Updated", "content": "New content"}' "$TOKEN" "200"
echo ""

# 4. Analysis
echo -e "${BLUE}4. NLP Analysis${NC}"
echo "---------------"
ANALYZE_RESPONSE=$(curl -s -X POST "$API_URL/documents/$DOC_ID/analyze" \
    -H "Authorization: Bearer $TOKEN")
JOB_ID=$(echo "$ANALYZE_RESPONSE" | jq -r '.job_id // empty')
if [ -n "$JOB_ID" ]; then
    echo -e "${GREEN}✓${NC} POST /documents/{id}/analyze -> Job created"
    sleep 2
    test_endpoint "GET" "/documents/$DOC_ID/analysis" "" "$TOKEN" "200"
else
    echo -e "${RED}✗${NC} POST /documents/{id}/analyze -> Failed"
fi
echo ""

# 5. APA References
echo -e "${BLUE}5. APA 7${NC}"
echo "--------"
test_endpoint "POST" "/documents/$DOC_ID/apa/generate-references" \
    '{
        "references": [{
            "authors": ["Doe, J."],
            "year": 2023,
            "title": "Test Article",
            "type": "article",
            "source": "Test Journal"
        }],
        "format": "text"
    }' "$TOKEN" "200"

test_endpoint "GET" "/documents/$DOC_ID/apa/validate" "" "$TOKEN" "200"
echo ""

# 6. Export
echo -e "${BLUE}6. Export${NC}"
echo "------"
EXPORT_RESPONSE=$(curl -s -X POST "$API_URL/documents/$DOC_ID/export" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "format": "pdf",
        "include_stats": true
    }')
EXPORT_JOB_ID=$(echo "$EXPORT_RESPONSE" | jq -r '.job_id // empty')
if [ -n "$EXPORT_JOB_ID" ]; then
    echo -e "${GREEN}✓${NC} POST /documents/{id}/export -> Job created"
    sleep 2
    test_endpoint "GET" "/export_jobs/$EXPORT_JOB_ID" "" "$TOKEN" "200"
else
    echo -e "${RED}✗${NC} POST /documents/{id}/export -> Failed"
fi
echo ""

# 7. Statistics
echo -e "${BLUE}7. Statistics${NC}"
echo "------------"
test_endpoint "POST" "/documents/$DOC_ID/stats" "" "$TOKEN" "202"
test_endpoint "GET" "/documents/$DOC_ID/stats" "" "$TOKEN" "200"
echo ""

# 8. Cleanup
echo -e "${BLUE}8. Cleanup${NC}"
echo "--------"
test_endpoint "DELETE" "/documents/$DOC_ID" "" "$TOKEN" "204"
echo ""

echo -e "${GREEN}✅ Endpoint testing complete!${NC}"

