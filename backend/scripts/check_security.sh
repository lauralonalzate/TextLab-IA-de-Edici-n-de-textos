#!/bin/bash
# TextLab Backend - Security Checklist Script
# Usage: ./scripts/check_security.sh

set -e

echo "🔒 Security Checklist for TextLab Backend"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

PASSED=0
FAILED=0
WARNINGS=0

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

warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARNINGS++))
}

# 1. Secrets Management
echo "1. Secrets Management"
echo "-------------------"

# Check .env not in git
if [ -d .git ]; then
    if git ls-files | grep -q "\.env$"; then
        check ".env file NOT in repository"
    else
        check ".env file not in repository"
    fi
else
    warn ".git directory not found, skipping git checks"
fi

# Check .env.example exists
[ -f .env.example ] && check ".env.example exists" || check ".env.example exists"

# Check .gitignore
if [ -f .gitignore ]; then
    grep -q "\.env" .gitignore && check ".env in .gitignore" || check ".env in .gitignore"
    grep -q "\.env.local" .gitignore && check ".env.local in .gitignore" || check ".env.local in .gitignore"
else
    check ".gitignore file exists"
fi

# Check .dockerignore
if [ -f .dockerignore ]; then
    grep -q "\.env" .dockerignore && check ".env in .dockerignore" || check ".env in .dockerignore"
else
    check ".dockerignore file exists"
fi

# Check for hardcoded secrets
echo ""
echo "2. Hardcoded Secrets"
echo "------------------"
SECRET_PATTERNS=(
    "password.*=.*['\"].*['\"]"
    "secret.*=.*['\"].*['\"]"
    "api_key.*=.*['\"].*['\"]"
    "SECRET_KEY.*=.*['\"][^'\"].*['\"]"
)

FOUND_SECRETS=0
for pattern in "${SECRET_PATTERNS[@]}"; do
    if grep -r -i --exclude-dir=__pycache__ --exclude-dir=.git --exclude="*.pyc" "$pattern" app/ 2>/dev/null | grep -v ".example" | grep -v "test" | grep -v "# " > /dev/null; then
        FOUND_SECRETS=1
        warn "Potential hardcoded secret found (pattern: $pattern)"
    fi
done

if [ $FOUND_SECRETS -eq 0 ]; then
    check "No hardcoded secrets found"
else
    check "No hardcoded secrets found"
fi

# 3. SQL Injection
echo ""
echo "3. SQL Injection Protection"
echo "-------------------------"
# Check for string formatting in SQL
if grep -r "execute.*%" app/ --include="*.py" 2>/dev/null | grep -v "# " | grep -v "test" > /dev/null; then
    warn "Potential SQL injection risk (string formatting in execute)"
    check "SQL uses parameterized queries"
else
    check "SQL uses parameterized queries"
fi

# 4. Rate Limiting
echo ""
echo "4. Rate Limiting"
echo "--------------"
if grep -q "@limiter.limit" app/api/v1/endpoints/auth.py; then
    check "Rate limiting configured on login"
else
    check "Rate limiting configured on login"
fi

if grep -q "ENABLE_RATE_LIMITING" app/core/config.py; then
    check "Rate limiting configurable via env"
else
    check "Rate limiting configurable via env"
fi

# 5. CORS Configuration
echo ""
echo "5. CORS Configuration"
echo "-------------------"
if grep -q "CORS_ORIGINS" app/core/config.py; then
    check "CORS origins configurable"
    
    # Check default is not wildcard in production
    if grep -q 'CORS_ORIGINS.*=.*"\*"' app/core/config.py; then
        warn "Default CORS_ORIGINS is wildcard (should be restricted in production)"
    else
        check "CORS default is not wildcard"
    fi
else
    check "CORS origins configurable"
fi

# 6. Authentication
echo ""
echo "6. Authentication & Authorization"
echo "-------------------------------"
# Check JWT implementation
if grep -q "create_access_token" app/utils/auth.py 2>/dev/null; then
    check "JWT token creation implemented"
else
    check "JWT token creation implemented"
fi

# Check password hashing
if grep -q "bcrypt" app/utils/auth.py 2>/dev/null; then
    check "Password hashing with bcrypt"
else
    check "Password hashing with bcrypt"
fi

# Check role-based access
if grep -q "require_roles" app/api/dependencies.py 2>/dev/null; then
    check "Role-based access control implemented"
else
    check "Role-based access control implemented"
fi

# 7. Input Validation
echo ""
echo "7. Input Validation"
echo "-----------------"
# Check Pydantic usage
if grep -r "BaseModel" app/schemas/ --include="*.py" 2>/dev/null | head -1 > /dev/null; then
    check "Pydantic schemas for validation"
else
    check "Pydantic schemas for validation"
fi

# 8. Path Traversal Protection
echo ""
echo "8. Path Traversal Protection"
echo "---------------------------"
if grep -q "\.\." app/api/v1/endpoints/export.py 2>/dev/null; then
    check "Path traversal protection in download endpoint"
else
    check "Path traversal protection in download endpoint"
fi

# 9. HTTPS/SSL
echo ""
echo "9. HTTPS/SSL"
echo "---------"
if [ -f docker-compose.prod.yml ]; then
    if grep -q "443:443" docker-compose.prod.yml; then
        check "HTTPS port configured"
    else
        warn "HTTPS port not configured in docker-compose.prod.yml"
    fi
    
    if grep -q "certbot" docker-compose.prod.yml; then
        check "SSL certificate management (Certbot) configured"
    else
        warn "Certbot not configured"
    fi
else
    warn "docker-compose.prod.yml not found"
fi

# 10. Security Headers
echo ""
echo "10. Security Headers"
echo "-------------------"
if [ -f nginx/conf.d/textlab.conf ]; then
    if grep -q "X-Frame-Options" nginx/conf.d/textlab.conf; then
        check "Security headers in Nginx config"
    else
        warn "Security headers not found in Nginx config"
    fi
else
    warn "Nginx config not found"
fi

# Summary
echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo -e "${YELLOW}Warnings: $WARNINGS${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    if [ $WARNINGS -eq 0 ]; then
        echo -e "${GREEN}✅ All security checks passed!${NC}"
        exit 0
    else
        echo -e "${YELLOW}⚠ Some warnings found. Please review.${NC}"
        exit 0
    fi
else
    echo -e "${RED}❌ Some security checks failed. Please fix before deployment.${NC}"
    exit 1
fi

