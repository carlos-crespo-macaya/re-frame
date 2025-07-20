#!/bin/bash

# Setup and generate audio fixtures using Google Cloud TTS

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🎙️  Audio Fixtures Setup${NC}\n"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is required but not installed.${NC}"
    exit 1
fi

# Check for Google Cloud credentials
if [ -z "$GOOGLE_APPLICATION_CREDENTIALS" ]; then
    echo -e "${YELLOW}⚠️  GOOGLE_APPLICATION_CREDENTIALS not set${NC}"
    echo "Looking for application default credentials..."
    
    # Check if gcloud is authenticated
    if command -v gcloud &> /dev/null; then
        if gcloud auth application-default print-access-token &> /dev/null; then
            echo -e "${GREEN}✓ Using application default credentials${NC}"
        else
            echo -e "${RED}❌ No Google Cloud credentials found${NC}"
            echo ""
            echo "To set up credentials, either:"
            echo "1. Set GOOGLE_APPLICATION_CREDENTIALS to your service account key:"
            echo "   export GOOGLE_APPLICATION_CREDENTIALS='/path/to/service-account-key.json'"
            echo ""
            echo "2. Or use application default credentials:"
            echo "   gcloud auth application-default login"
            exit 1
        fi
    else
        echo -e "${RED}❌ No credentials found and gcloud CLI not installed${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Using GOOGLE_APPLICATION_CREDENTIALS${NC}"
fi

# Install dependencies
echo -e "\n${YELLOW}📦 Installing dependencies...${NC}"
npm install

# Generate audio fixtures
echo -e "\n${YELLOW}🎵 Generating audio fixtures...${NC}"
node generate-audio-fixtures.js

# Optionally list available voices
if [[ "$1" == "--list-voices" ]]; then
    echo -e "\n${YELLOW}🎤 Available TTS voices:${NC}"
    node generate-audio-fixtures.js --list-voices
fi

# Verify all files were created
echo -e "\n${YELLOW}🔍 Verifying audio files...${NC}"
node generate-audio-fixtures.js verify

echo -e "\n${GREEN}✅ Setup complete!${NC}"
echo -e "Audio fixtures are ready for E2E testing."
echo -e "\nTo run the tests:"
echo -e "  cd ../../.."
echo -e "  ./run-e2e-docker.sh"