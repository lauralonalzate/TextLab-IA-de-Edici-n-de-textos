#!/bin/bash
# TextLab Backend - Deployment Verification Script
# Usage: ./scripts/verify_deployment.sh [API_URL]

set -e

API_URL="${1:-http://localhost:8000/api/v1}"
BASE_URL="${API_URL%/api/v1}"

echo "🔍 Verificando TextLab Backend..."
echo "API URL: $API_URL"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counter
PASSED=0
FAILED=0

# Helper functions
check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $1"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $1"
        ((FAILED++))
        return 1
    fi
}

# 1. Health Checks
echo "1. Health Checks"
echo "---------------"
curl -sf "$BASE_URL/health" > /dev/null && check "Health endpoint" || check "Health endpoint"
curl -sf "$BASE_URL/ready" > /dev/null && check "Readiness endpoint" || check "Readiness endpoint"
echo ""

# 2. OpenAPI
echo "2. OpenAPI Documentation"
echo "----------------------"
curl -sf "$BASE_URL/openapi.json" > /dev/null && check "OpenAPI schema accessible" || check "OpenAPI schema accessible"
curl -sf "$BASE_URL/docs" > /dev/null && check "Swagger UI accessible" || check "Swagger UI accessible"
echo ""

# 3. Database Connection
echo "3. Database"
echo "----------"
if command -v docker-compose &> /dev/null; then
    docker-compose exec -T postgres psql -U textlab -d textlab_db -c "SELECT 1;" > /dev/null 2>&1 && \
        check "Database connection" || check "Database connection"
    
    # Check tables
    TABLES=$(docker-compose exec -T postgres psql -U textlab -d textlab_db -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';" | tr -d ' ')
    if [ "$TABLES" -gt 0 ]; then
        check "Database tables exist ($TABLES tables)"
    else
        check "Database tables exist"
    fi
else
    echo -e "${YELLOW}⚠${NC} Docker Compose not available, skipping database checks"
fi
echo ""

# 4. Services Status
echo "4. Services"
echo "----------"
if command -v docker-compose &> /dev/null; then
    RUNNING=$(docker-compose ps --services --filter "status=running" | wc -l)
    TOTAL=$(docker-compose ps --services | wc -l)
    if [ "$RUNNING" -eq "$TOTAL" ] && [ "$TOTAL" -gt 0 ]; then
        check "All services running ($RUNNING/$TOTAL)"
    else
        check "All services running ($RUNNING/$TOTAL running)"
    fi
else
    echo -e "${YELLOW}⚠${NC} Docker Compose not available, skipping service checks"
fi
echo ""

# 5. Linting (if in development)
echo "5. Code Quality"
echo "-------------"
if command -v black &> /dev/null && command -v flake8 &> /dev/null; then
    black --check app tests > /dev/null 2>&1 && check "Black formatting" || check "Black formatting"
    isort --check-only app tests > /dev/null 2>&1 && check "Import sorting" || check "Import sorting"
    flake8 app tests --max-line-length=127 --exclude=__pycache__,migrations > /dev/null 2>&1 && check "Flake8 linting" || check "Flake8 linting"
else
    echo -e "${YELLOW}⚠${NC} Linters not installed, skipping code quality checks"
fi
echo ""

# 6. Tests (optional, can be slow)
if [ "${RUN_TESTS:-false}" = "true" ]; then
    echo "6. Tests"
    echo "------"
    if command -v pytest &> /dev/null; then
        pytest -v --tb=short -x > /dev/null 2>&1 && check "All tests pass" || check "All tests pass"
    else
        echo -e "${YELLOW}⚠${NC} pytest not available, skipping tests"
    fi
    echo ""
fi

# 7. Security Checks
echo "7. Security"
echo "---------"
# Check .env not in git
if [ -d .git ]; then
    git ls-files | grep -q "\.env$" && check ".env not in repository" || check ".env not in repository"
    grep -q "\.env" .gitignore && check ".env in .gitignore" || check ".env in .gitignore"
fi

# Check .dockerignore
[ -f .dockerignore ] && grep -q "\.env" .dockerignore && check ".env in .dockerignore" || check ".env in .dockerignore"
echo ""

# Summary
echo "===================="
echo "Summary"
echo "===================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some checks failed. Please review above.${NC}"
    exit 1
fi

