"""Setup logging for ADK debugging."""

import logging
import os
from datetime import datetime

# Create logs directory
os.makedirs("logs", exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # Console handler
        logging.StreamHandler(),
        # File handler
        logging.FileHandler(f'logs/adk_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    ]
)

# Set specific loggers
logging.getLogger("google.adk").setLevel(logging.DEBUG)
logging.getLogger("reframe").setLevel(logging.DEBUG)

print(f"Logging configured. Check logs/ directory for debug output.")