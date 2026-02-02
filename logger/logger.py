# logger/logger.py
import logging
from logging.handlers import RotatingFileHandler
import os


def setup_logger():
    os.makedirs("./logs", exist_ok=True)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    if root_logger.handlers:
        return

    file_handler = RotatingFileHandler(
        "./logs/task_manager.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
    )

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
