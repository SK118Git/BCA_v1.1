# ============================================================================================================================
# logger.py - This file and intializes the logger which is then used throughout the project
# ============================================================================================================================
# External Imports
import logging
import os
import sys

# ============================================================================================================================


def setup_logging():
    """Set up logging to file with append mode"""
    if getattr(sys, "frozen", False):  # Running as PyInstaller bundle
        app_dir = os.path.dirname(sys.executable)
        log_file = os.path.join(app_dir, "app.log")
    else:
        log_file = "app.log"

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file, mode="a"),  # 'a' for append mode
        ],
    )

    # Add session separator
    logging.info("=" * 50)
    logging.info("NEW SESSION STARTED")
    logging.info("=" * 50)

    return logging.getLogger(__name__)


# We initialize the project wide logger here.
logger = setup_logging()


def log_print(message):
    """Replace print() with this function"""
    logger.info(message)
    # Optionally also print to console if you want both
    print(message)

