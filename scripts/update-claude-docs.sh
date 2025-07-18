#!/bin/bash

# Script to check if CLAUDE.md files need updating based on recent changes

set -e

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Check if any package files have been modified more recently than CLAUDE.md
check_updates_needed() {
    local claude_file=$1
    local check_files=("${@:2}")
    
    if [ ! -f "$claude_file" ]; then
        echo -e "${YELLOW}Warning: $claude_file does not exist${NC}"
        return 1
    fi
    
    local claude_modified=$(stat -f "%m" "$claude_file" 2>/dev/null || stat -c "%Y" "$claude_file" 2>/dev/null)
    local needs_update=false
    
    for file in "${check_files[@]}"; do
        if [ -f "$file" ]; then
            local file_modified=$(stat -f "%m" "$file" 2>/dev/null || stat -c "%Y" "$file" 2>/dev/null)
            if [ "$file_modified" -gt "$claude_modified" ]; then
                echo -e "${YELLOW}$file has been modified more recently than $claude_file${NC}"
                needs_update=true
            fi
        fi
    done
    
    if [ "$needs_update" = true ]; then
        return 0
    else
        return 1
    fi
}

# Check root CLAUDE.md
echo "Checking root CLAUDE.md..."
if check_updates_needed "CLAUDE.md" "package.json" "Makefile" "docker-compose.yml" ".github/workflows/"*; then
    echo -e "${RED}Root CLAUDE.md may need updating${NC}"
fi

# Check frontend CLAUDE.md
echo -e "\nChecking frontend/CLAUDE.md..."
if check_updates_needed "frontend/CLAUDE.md" "frontend/package.json" "frontend/tsconfig.json" "frontend/next.config.js" "frontend/.eslintrc.json"; then
    echo -e "${RED}Frontend CLAUDE.md may need updating${NC}"
fi

# Check backend CLAUDE.md
echo -e "\nChecking backend/CLAUDE.md..."
if check_updates_needed "backend/CLAUDE.md" "backend/pyproject.toml" "backend/uv.lock" "backend/.env.example"; then
    echo -e "${RED}Backend CLAUDE.md may need updating${NC}"
fi

# Check for new commands in package.json files
echo -e "\n${GREEN}Checking for undocumented commands...${NC}"

# Function to extract commands from package.json
check_package_commands() {
    local package_file=$1
    local claude_file=$2
    
    if [ -f "$package_file" ] && [ -f "$claude_file" ]; then
        echo -e "\nChecking $package_file..."
        
        # Extract script names from package.json
        local scripts=$(jq -r '.scripts | keys[]' "$package_file" 2>/dev/null || echo "")
        
        for script in $scripts; do
            # Check if script is mentioned in CLAUDE.md
            if ! grep -q "$script" "$claude_file"; then
                echo -e "${YELLOW}  Command '$script' not found in $claude_file${NC}"
            fi
        done
    fi
}

check_package_commands "package.json" "CLAUDE.md"
check_package_commands "frontend/package.json" "frontend/CLAUDE.md"

# Check for backend commands
if [ -f "backend/pyproject.toml" ] && [ -f "backend/CLAUDE.md" ]; then
    echo -e "\nChecking backend/pyproject.toml..."
    
    # Extract poe task names
    tasks=$(grep '^\[tool\.poe\.tasks\.' backend/pyproject.toml | sed 's/\[tool\.poe\.tasks\.\(.*\)\]/\1/' | grep -v '^$')
    
    for task in $tasks; do
        if ! grep -q "poe $task" "backend/CLAUDE.md"; then
            echo -e "${YELLOW}  Command 'poe $task' not found in backend/CLAUDE.md${NC}"
        fi
    done
fi

echo -e "\n${GREEN}Check complete!${NC}"
echo -e "Run ${GREEN}/update-claude-docs${NC} to automatically update CLAUDE.md files"