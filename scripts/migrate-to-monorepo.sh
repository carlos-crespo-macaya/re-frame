#!/bin/bash
set -e

echo "🚀 Starting monorepo migration..."

# Frontend files and directories to move
FRONTEND_ITEMS=(
  "app"
  "components"
  "lib"
  "public"
  "types"
  "next.config.mjs"
  "next.config.cloudrun.mjs"
  "next-env.d.ts"
  "postcss.config.mjs"
  "tailwind.config.ts"
  "tsconfig.json"
  "tsconfig.tsbuildinfo"
  "jest.config.js"
  "jest.setup.js"
  "package.json"
  "package-lock.json"
  "pnpm-lock.yaml"
  "Dockerfile"
)

# Files to keep in root (removed - not used in script)

echo "📁 Moving frontend files to frontend/ directory..."

for item in "${FRONTEND_ITEMS[@]}"; do
  if [ -e "$item" ]; then
    echo "  → Moving $item"
    mv "$item" "frontend/" || echo "  ⚠️  Failed to move $item"
  else
    echo "  ⚠️  $item not found, skipping"
  fi
done

# Move shell scripts to root/scripts if they're general purpose
if [ -f "add_to_project.sh" ]; then
  mv "add_to_project.sh" "scripts/"
fi
if [ -f "create_labels.sh" ]; then
  mv "create_labels.sh" "scripts/"
fi
if [ -f "organize_project_items.sh" ]; then
  mv "organize_project_items.sh" "scripts/"
fi
if [ -f "setup-gcp.sh" ]; then
  mv "setup-gcp.sh" "scripts/"
fi

echo "✅ Frontend files moved successfully!"

# Create README files for each directory
echo "📝 Creating directory README files..."

cat > frontend/README.md << 'EOF'
# Frontend - re-frame.social

This directory contains the Next.js 14 frontend application for the CBT Assistant.

## Quick Start

```bash
cd frontend
pnpm install
pnpm run dev
```

## Build

```bash
pnpm run build
pnpm run start
```

## Testing

```bash
pnpm run test
pnpm run test:watch
```

See the main [README.md](../README.md) for full project documentation.
EOF

cat > backend/README.md << 'EOF'
# Backend - CBT Assistant API

This directory will contain the FastAPI backend with Google's Agent Development Kit (ADK).

## Structure (Coming Soon)

- `app/` - FastAPI application
- `agents/` - ADK agents and conversation logic
- `tests/` - Backend tests
- `requirements.txt` - Python dependencies

The backend code will be merged here via git subtree from the reframe-agents repository.
EOF

echo "✅ README files created!"

# Update root gitignore
if [ -f ".gitignore" ]; then
  echo "📝 Updating existing .gitignore file..."
  
  # Check if monorepo entries already exist
  if ! grep -q "# Monorepo" .gitignore; then
    cat >> .gitignore << 'EOF'

# Monorepo specific
frontend/node_modules/
backend/__pycache__/
backend/venv/
backend/.env
frontend/.next/
frontend/out/
EOF
  fi
else
  echo "📝 Creating new .gitignore file..."
  cat > .gitignore << 'EOF'
# Dependencies
node_modules/
__pycache__/
*.pyc
.env
.env.local

# Build outputs
.next/
out/
dist/
build/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Monorepo specific
frontend/node_modules/
backend/__pycache__/
backend/venv/
backend/.env
frontend/.next/
frontend/out/
EOF
fi

echo "🎉 Monorepo structure created successfully!"
echo ""
echo "📋 Next steps:"
echo "1. Update import paths in frontend code"
echo "2. Update frontend package.json scripts"
echo "3. Create root package.json for monorepo commands"
echo "4. Test frontend build from new location"