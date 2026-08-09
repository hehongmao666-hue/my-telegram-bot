# ==========================
# utils/helpers.py - 通用函数
# ==========================

from config import OWNER_ID


def get_user_info(update):
    user = update.effective_user
    if user:
        return user.id, user.username or user.first_name or "Unknown"
    return None, "Unknown"


def get_user_info_from_query(query):
    user = query.from_user
    if user:
        return user.id, user.username or user.first_name or "Unknown"
    return None, "Unknown"


async def owner_only(update):
    uid = update.effective_user.id
    if uid != OWNER_ID:
        await update.message.reply_text("⛔️ သင့်တွင် ဤ command ကိုသုံးခွင့်မရှိပါ။")
        return False
    return True


def is_game_owner(user_id, owner_id):
    return str(user_id) == str(owner_id)