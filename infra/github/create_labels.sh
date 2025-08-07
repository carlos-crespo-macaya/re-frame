#\!/bin/bash
# Create labels for GitHub issues

echo "Creating epic labels..."
gh label create "epic-0-migration" --color "6B46C1" --description "Monorepo migration tasks" || true
gh label create "epic-1-local" --color "0052CC" --description "Local Docker deployment" || true
gh label create "epic-2-production" --color "5319E7" --description "Cloud Run production" || true

echo "Creating team labels..."
gh label create "team-backend" --color "0E8A16" --description "Backend team tasks" || true
gh label create "team-frontend" --color "FB8C00" --description "Frontend team tasks" || true
gh label create "team-shared" --color "FDD835" --description "Shared team tasks" || true
gh label create "team-devops" --color "00ACC1" --description "DevOps tasks" || true

echo "Creating priority labels..."
gh label create "priority-P0" --color "D32F2F" --description "Critical priority" || true
gh label create "priority-P1" --color "F57C00" --description "High priority" || true
gh label create "priority-P2" --color "FBC02D" --description "Medium priority" || true

echo "Creating size labels..."
gh label create "size-1" --color "E3F2FD" --description "1 story point" || true
gh label create "size-2" --color "BBDEFB" --description "2 story points" || true
gh label create "size-3" --color "90CAF9" --description "3 story points" || true
gh label create "size-5" --color "64B5F6" --description "5 story points" || true

echo "Creating type labels..."
gh label create "type-feature" --color "1D76DB" --description "New feature" || true
gh label create "type-infrastructure" --color "C5DEF5" --description "Infrastructure" || true
gh label create "type-documentation" --color "0075CA" --description "Documentation" || true
gh label create "type-testing" --color "BFD4F2" --description "Testing" || true

echo "Creating special labels..."
gh label create "blocked" --color "000000" --description "Blocked by dependency" || true
gh label create "needs-discussion" --color "7B1FA2" --description "Needs team discussion" || true

echo "Labels created successfully\!"
