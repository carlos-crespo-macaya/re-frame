#!/bin/bash
# Clean start script for ADK with multilingual support

echo "🧹 Cleaning up old processes and cache..."

# Kill any existing ADK processes
pkill -f "adk web" 2>/dev/null || true
pkill -f "python.*adk" 2>/dev/null || true

# Clear Python cache
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true

# Clear any ADK cache (if exists)
rm -rf .adk_cache 2>/dev/null || true

echo "✅ Cleanup complete"
echo ""
echo "🚀 Starting ADK with Maya Multilingual Agent..."
echo ""
echo "📋 Test with these messages:"
echo "   Spanish: 'hola, estoy ansioso'"
echo "   English: 'hello, I'm anxious'"
echo "   French: 'bonjour, je suis anxieux'"
echo ""

# Start ADK
adk web