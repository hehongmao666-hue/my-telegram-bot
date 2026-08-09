# ==========================
# config.py - 所有配置（统一路径版）
# ==========================

import os
from dotenv import load_dotenv

load_dotenv()

# ============ Token & Owner ============
TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")

OWNER_ID = int(os.environ.get("OWNER_ID", 5300063761))

# ============ 管理员配置 ============
ADMIN_IDS = [
    5300063761,  # Owner
    1062259560,  # Admin 1
]

# ============ 文件配置（统一使用 data/ 目录） ============
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "data.json")
ANNOUNCE_DATA_FILE = os.path.join(DATA_DIR, "announce_data.json")
SCHEDULE_FILE = os.path.join(DATA_DIR, "schedule.json")
PRESET_FILE = os.path.join(DATA_DIR, "presets.json")
GAME_STATE_FILE = os.path.join(DATA_DIR, "game_states.json")

# 兼容旧代码
GAME_STATES_FILE = GAME_STATE_FILE

# ============ 公告配置 ============
ANNOUNCE_DELAY = 0.5
MENTION_BATCH_SIZE = 20
ANNOUNCE_MAX_LENGTH = 3500

MENTION_EMOJIS = [
    "🎯", "🔥", "⭐", "💎", "🌟",
    "🎮", "🕹", "🎲", "❤️", "💙",
    "🧡", "🤍", "🖤", "🎉", "🚀",
    "⚡", "🎁", "🍀", "🌈", "☀️",
    "🌙", "🪐", "🌊", "🌋", "🏔️",
    "🌲", "🌵", "🌺", "🌻", "🍄",
    "🦋", "🐉", "🦅", "🐺", "🦁",
    "🐍", "🐳", "🦈", "🕊️", "🌟"
]

ANNOUNCE_BUTTONS = [
    ("🎮 Activity", "https://t.me/Myanmar_GameFriendss"),
    ("👤 Owner", "https://t.me/MCLP1_1"),
]

# ============ 全局状态 ============
announcement_running = {}

# ============ 随机链接 ============
RANDOM_LINKS = [
    "https://mm6805.com/?id=530467052",
    "https://mm6801.com/?id=530467052",
]

# ============ 游戏配置 ============
MAX_HP = 80
MAX_ENERGY = 40