# ==========================
# storage.py - 数据读写（完整修复版）
# ==========================

import json
import os
import time
from config import DATA_FILE, ANNOUNCE_DATA_FILE, SCHEDULE_FILE, PRESET_FILE, GAME_STATE_FILE


# ============ data.json ============
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data is None:
                    data = {}
                data.setdefault("users", [])
                data.setdefault("groups", [])
                data.setdefault("blacklist", [])
                return data
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    return {"users": [], "groups": [], "blacklist": []}


def save_data(data):
    if data is None:
        data = {}
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_user(user_id):
    data = load_data()
    if user_id not in data["users"]:
        data["users"].append(user_id)
        save_data(data)


def add_group(group_id):
    data = load_data()
    if group_id not in data["groups"]:
        data["groups"].append(group_id)
        save_data(data)


def is_blacklisted(user_id):
    data = load_data()
    return user_id in data.get("blacklist", [])


# ============ announce_data.json ============
def load_announce_data():
    if os.path.exists(ANNOUNCE_DATA_FILE):
        try:
            with open(ANNOUNCE_DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data is None:
                    data = {}
                data.setdefault("subscribers", [])
                data.setdefault("active_members", {})
                return data
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    return {"subscribers": [], "active_members": {}}


def save_announce_data(data):
    if data is None:
        data = {"subscribers": [], "active_members": {}}
    os.makedirs(os.path.dirname(ANNOUNCE_DATA_FILE), exist_ok=True)
    with open(ANNOUNCE_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_subscribers():
    data = load_announce_data()
    return data.get("subscribers", [])


def add_subscriber(user_id):
    data = load_announce_data()
    if user_id not in data["subscribers"]:
        data["subscribers"].append(user_id)
        save_announce_data(data)
        return True
    return False


def save_active_member(chat_id, user, message_type="text"):
    if chat_id > 0:
        return
    data = load_announce_data()
    active = data.setdefault("active_members", {})
    chat_key = str(chat_id)
    if chat_key not in active:
        active[chat_key] = {}
    uid = str(user.id)
    info = active[chat_key].get(uid, {})
    info["id"] = user.id
    info["name"] = user.full_name or ""
    info["first_name"] = user.first_name or ""
    info["last_name"] = user.last_name or ""
    info["username"] = user.username or ""
    info["is_bot"] = user.is_bot
    info["language_code"] = user.language_code or ""
    now = int(time.time())
    info.setdefault("first_seen", now)
    info["last_active"] = now
    info["message_count"] = info.get("message_count", 0) + 1
    info["last_message_type"] = message_type
    active[chat_key][uid] = info
    save_announce_data(data)


def get_active_members(chat_id, days=30):
    data = load_announce_data()
    active = data.get("active_members", {})
    chat = active.get(str(chat_id), {})
    now = int(time.time())
    result = []
    for uid, info in chat.items():
        if info.get("is_bot", False):
            continue
        last_active = info.get("last_active", 0)
        if now - last_active <= days * 86400:
            result.append(info)
    result.sort(key=lambda x: x.get("last_active", 0), reverse=True)
    return result


# ============ schedule.json ============
def load_schedule():
    if os.path.exists(SCHEDULE_FILE):
        try:
            with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data is None:
                    return []
                return data
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    return []


def save_schedule(s):
    if s is None:
        s = []
    os.makedirs(os.path.dirname(SCHEDULE_FILE), exist_ok=True)
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=2)


# ============ presets.json ============
def load_presets():
    if os.path.exists(PRESET_FILE):
        try:
            with open(PRESET_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data is None:
                    return {}
                return data
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    return {}


def save_presets(p):
    if p is None:
        p = {}
    os.makedirs(os.path.dirname(PRESET_FILE), exist_ok=True)
    with open(PRESET_FILE, "w", encoding="utf-8") as f:
        json.dump(p, f, ensure_ascii=False, indent=2)


# ============ game_states.json ============
def load_game_states():
    if os.path.exists(GAME_STATE_FILE):
        try:
            with open(GAME_STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data is None:
                    return {}
                return data
        except (json.JSONDecodeError, FileNotFoundError):
            pass
    return {}


def save_game_states(states):
    if states is None:
        states = {}
    os.makedirs(os.path.dirname(GAME_STATE_FILE), exist_ok=True)
    with open(GAME_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(states, f, ensure_ascii=False, indent=2)


def get_player_state(user_id):
    states = load_game_states()
    if states is None:
        return None
    return states.get(str(user_id))