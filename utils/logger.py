# ==========================
# utils/logger.py - 日志系统
# ==========================

import logging
import os
from datetime import datetime

LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, f"bot_{datetime.now().strftime('%Y-%m-%d')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def log_action(user_id, username, action, details="", status="SUCCESS"):
    user_info = f"User:{user_id}"
    if username:
        user_info += f"(@{username})"
    log_msg = f"{user_info} | {action}"
    if details:
        log_msg += f" | {details}"
    if status != "SUCCESS":
        log_msg += f" | {status}"
    logger.info(log_msg)


def log_error(user_id, username, action, error_msg):
    user_info = f"User:{user_id}"
    if username:
        user_info += f"(@{username})"
    logger.error(f"{user_info} | {action} | ERROR: {error_msg}")


def log_broadcast(action, target_count, details=""):
    log_msg = f"BROADCAST | {action} | 目标数: {target_count}"
    if details:
        log_msg += f" | {details}"
    logger.info(log_msg)