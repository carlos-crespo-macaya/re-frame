#!/usr/bin/env python3
"""Launch ADK web interface for re-frame agent development.

This script sets up and launches the ADK web UI for testing and debugging
the multi-agent system. It allows interactive testing of agents and
visualization of agent traces.
"""

import logging
import os
import subprocess
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_adk_installation():
    """Check if ADK is installed."""
    try:
        result = subprocess.run(
            ["adk", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        logger.info(f"ADK version: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.error("ADK is not installed or not in PATH")
        logger.error("Install ADK: pip install google-ai-generativeai-adk")
        return False


def setup_environment():
    """Set up environment for ADK web."""
    # Ensure we're in the backend directory
    backend_dir = Path(__file__).parent
    os.chdir(backend_dir)
    
    # Set environment variables if needed
    if not os.getenv("GOOGLE_AI_API_KEY"):
        logger.warning("GOOGLE_AI_API_KEY not set. ADK may not function properly.")
        logger.info("Set it with: export GOOGLE_AI_API_KEY='your-api-key'")
    
    return backend_dir


def launch_adk_web():
    """Launch the ADK web interface."""
    logger.info("Launching ADK web interface...")
    logger.info("The UI will be available at http://localhost:8000")
    logger.info("Press Ctrl+C to stop the server")
    
    try:
        # Run adk web command
        # Use --no-reload on Windows to avoid subprocess issues
        cmd = ["adk", "web"]
        if sys.platform == "win32":
            cmd.append("--no-reload")
            
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to launch ADK web: {e}")
        return False
    except KeyboardInterrupt:
        logger.info("\nShutting down ADK web interface...")
        return True
    
    return True


def main():
    """Main entry point."""
    logger.info("Starting re-frame ADK Web Interface")
    
    # Check ADK installation
    if not check_adk_installation():
        return 1
    
    # Set up environment
    backend_dir = setup_environment()
    logger.info(f"Working directory: {backend_dir}")
    
    # Launch ADK web
    if launch_adk_web():
        logger.info("ADK web interface closed successfully")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())