#!/bin/bash
# Local testing script that mirrors CI/CD checks
# Run this before pushing to ensure all checks pass

set -e

echo "🔍 Running local checks that mirror CI/CD..."
echo "================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track failures
FAILED=0

# Function to run a check
run_check() {
    local name=$1
    local cmd=$2
    echo -e "\n${YELLOW}Running: $name${NC}"
    if eval "$cmd"; then
        echo -e "${GREEN}✓ $name passed${NC}"
    else
        echo -e "${RED}✗ $name failed${NC}"
        FAILED=$((FAILED + 1))
    fi
}

# Backend checks
if [ -d "backend" ]; then
    echo -e "\n📦 Backend Checks"
    echo "=================="
    cd backend
    
    # Activate virtual environment if it exists
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    fi
    
    run_check "Python linting (ruff)" "poe lint"
    run_check "Python formatting (black)" "poe format-check"
    run_check "Python type checking (mypy)" "poe type-check"
    run_check "Python tests (pytest)" "poe test"
    run_check "Python security scan (bandit)" "bandit -r . -ll || true"
    
    cd ..
fi

# Frontend checks
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    echo -e "\n🎨 Frontend Checks"
    echo "==================="
    cd frontend
    
    run_check "Frontend linting (ESLint)" "pnpm lint || npm run lint"
    run_check "Frontend build" "pnpm build || npm run build"
    
    cd ..
fi

# Infrastructure checks
if [ -d "infrastructure/terraform" ]; then
    echo -e "\n🏗️ Infrastructure Checks"
    echo "========================="
    cd infrastructure
    
    run_check "Terraform formatting" "terraform fmt -check -recursive"
    run_check "Terraform validation" "terraform init -backend=false && terraform validate"
    
    cd ..
fi

# Git checks
echo -e "\n📝 Git Checks"
echo "=============="
run_check "No large files" "find . -type f -size +1M ! -path './.git/*' ! -path './node_modules/*' ! -path './.venv/*' -exec echo 'Large file: {}' \; | grep -q 'Large file:' && exit 1 || exit 0"

# Security checks
echo -e "\n🔒 Security Checks"
echo "=================="
run_check "No secrets in code" "git ls-files -z | xargs -0 grep -E '(api_key|apikey|password|secret|token|private_key)\\s*=\\s*[\"'\''`][^\"'\''`]+[\"'\''`]' || true | grep -q . && exit 1 || exit 0"

# Summary
echo -e "\n================================================"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Safe to push.${NC}"
else
    echo -e "${RED}❌ $FAILED check(s) failed. Please fix before pushing.${NC}"
    exit 1
fi