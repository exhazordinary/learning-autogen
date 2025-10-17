#!/bin/bash

# Verification script for AutoGen Research Assistant

echo "🔍 Verifying AutoGen Research Assistant Setup"
echo "=============================================="
echo ""

# Check Python
echo "✓ Checking Python..."
python --version || echo "❌ Python not found"

# Check Node
echo "✓ Checking Node.js..."
node --version || echo "❌ Node.js not found"

# Check Redis
echo "✓ Checking Redis..."
redis-cli ping > /dev/null 2>&1 && echo "  ✓ Redis is running" || echo "  ⚠️  Redis is not running (start with: redis-server)"

# Check Docker
echo "✓ Checking Docker..."
docker --version > /dev/null 2>&1 && echo "  ✓ Docker installed" || echo "  ⚠️  Docker not installed"

# Check files
echo ""
echo "✓ Checking required files..."
files=(
  "app.py"
  "docker-compose.yml"
  "frontend/src/App.jsx"
  "frontend/src/store.js"
  "src/autogen_research/database/models.py"
  "src/autogen_research/tasks/celery_app.py"
  ".env.example"
)

for file in "${files[@]}"; do
  if [ -f "$file" ]; then
    echo "  ✓ $file"
  else
    echo "  ❌ $file missing"
  fi
done

# Check for old files (should not exist)
echo ""
echo "✓ Checking for old files (should be cleaned up)..."
old_files=(
  "app_v2.py"
  "app_v1_backup.py"
  "frontend/src/App_v2.jsx"
  "frontend/src/App_v1_backup.jsx"
  "README_V2.md"
  "MIGRATION_GUIDE.md"
)

all_clean=true
for file in "${old_files[@]}"; do
  if [ -f "$file" ]; then
    echo "  ⚠️  $file still exists (should be removed)"
    all_clean=false
  fi
done

if $all_clean; then
  echo "  ✓ All old files cleaned up"
fi

# Check environment
echo ""
echo "✓ Checking environment..."
if [ -f ".env" ]; then
  echo "  ✓ .env file exists"
else
  echo "  ⚠️  .env file not found (copy from .env.example)"
fi

echo ""
echo "=============================================="
echo "Verification complete!"
echo ""
echo "Quick commands:"
echo "  Docker:  docker-compose up -d"
echo "  Local:   python app.py"
echo "  Tests:   pytest tests/ -v"
echo ""
