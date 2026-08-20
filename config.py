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
ANNOUNCE_DELAY = 2.0
MENTION_BATCH_SIZE = 15
ANNOUNCE_MAX_LENGTH = 3500

MENTION_EMOJIS = [
    # 食物
    "🍎", "🍊", "🍋", "🍇", "🍉", "🍓", "🫐", "🍒", "🍑", "🥭",
    "🍍", "🥝", "🍅", "🍆", "🥑", "🌽", "🥕", "🥦", "🥬", "🥒",
    "🌶️", "🧄", "🧅", "🍄", "🥜", "🌰", "🍞", "🧀", "🍖", "🍗",
    "🥩", "🥓", "🍔", "🍟", "🍕", "🌭", "🥪", "🌮", "🌯", "🥗",
    # 饮料
    "🍸", "🍹", "🍺", "🍻", "🥂", "🍷", "🥃", "🍶", "☕", "🫖",
    "🍵", "🧃", "🥤", "🧋",
    # 自然
    "🌋", "🏔️", "⛰️", "🏕️", "🏖️", "🏜️", "🏝️", "🌋", "🗻", "🌄",
    "🌅", "🌇", "🌉", "🌁", "🗾", "🎑", "🏞️", "🌲", "🌳", "🌴",
    "🌵", "🌾", "🌿", "☘️", "🍀", "🍁", "🍂", "🍃", "🌺", "🌻",
    "🌹", "🥀", "🌷", "🌼", "🌸", "💐",
    # 动物
    "🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼", "🐨", "🐯",
    "🦁", "🐮", "🐷", "🐸", "🐵", "🐔", "🐧", "🐦", "🐤", "🐣",
    "🦆", "🦉", "🦅", "🦇", "🐺", "🐗", "🐴", "🦄", "🐝", "🐞",
    "🦋", "🐙", "🦑", "🦐", "🦞", "🐠", "🐟", "🐡", "🐬", "🐳",
    # 运动
    "⚽", "🏀", "🏈", "⚾", "🥎", "🎾", "🏐", "🏉", "🥏", "🎱",
    "🪀", "🏓", "🏸", "🏒", "🏑", "🥍", "🏏", "⛳", "🏹", "🎣",
    "🥊", "🥋", "🎽", "🛹", "🛼", "⛸️",
    # 其他
    "🎯", "🎮", "🎲", "🧩", "🧸", "🎨", "🎭", "🎪", "🎟️", "🎫",
    "🎗️", "🎖️", "🏆", "🏅", "🥇", "🥈", "🥉", "⚡", "🔥", "💎",
    "🌟", "⭐", "🌙", "☀️", "🌈", "☁️", "⛅", "🌤️", "🌥️", "🌦️",
]

ANNOUNCE_BUTTONS = [
    ("🎮 Activity", "https://t.me/Myanmar_GameFriendss"),
    ("👤 Owner", "https://t.me/MCLP1_1"),
]

# ============ 全局状态 ============
announcement_running = {}

# ============ 随机链接 ============
RANDOM_LINKS = [
    "http://www.cklottery.tv/#/register?invitationCode=682421162801",
    "https://cklottery.cc/#/register?invitationCode=682421162801",
    "http://www.cklottery.top/#/register?invitationCode=682421162801",
    "http://www.cklottery.club/#/register?invitationCode=682421162801",
    "http://www.cklottery.info/#/register?invitationCode=682421162801",
    "https://www.cklottery.online/#/register?invitationCode=682421162801",
]

# ============ 游戏配置 ============
MAX_HP = 80
MAX_ENERGY = 40