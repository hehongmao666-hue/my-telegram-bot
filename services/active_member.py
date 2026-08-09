# ==========================
# services/active_member.py - 活跃成员（使用公告数据文件）
# ==========================

import time
from storage import save_active_member, get_active_members, load_announce_data, save_announce_data
from utils.logger import logger


def save_active_member_old(chat_id, user, message_type="text"):
    """保存群活跃成员（旧版 - 已弃用，请使用 storage.save_active_member）"""
    # 这个函数已移到 storage.py
    pass


async def active_member_listener(update, context):
    """Active Member System - 静默记录群成员"""
    if update.message is None:
        return

    if update.effective_chat is None:
        return

    if update.effective_chat.type == "private":
        return

    if update.effective_user is None:
        return

    if update.effective_user.is_bot:
        return

    msg = update.message

    if msg.text:
        message_type = "text"
    elif msg.photo:
        message_type = "photo"
    elif msg.video:
        message_type = "video"
    elif msg.animation:
        message_type = "gif"
    elif msg.sticker:
        message_type = "sticker"
    elif msg.voice:
        message_type = "voice"
    elif msg.video_note:
        message_type = "video_note"
    elif msg.audio:
        message_type = "audio"
    elif msg.document:
        message_type = "document"
    elif msg.contact:
        message_type = "contact"
    elif msg.location:
        message_type = "location"
    elif msg.poll:
        message_type = "poll"
    else:
        message_type = "other"

    try:
        # ✅ 使用 storage.py 中的函数，写入 announce_data.json
        from storage import save_active_member
        save_active_member(
            chat_id=update.effective_chat.id,
            user=update.effective_user,
            message_type=message_type,
        )
    except Exception:
        logger.exception("[ActiveMember]")


# ============ 以下函数已移至 storage.py ============
# 为了兼容性保留引用
def get_active_members(chat_id, days=30):
    """获取最近 N 天活跃成员（从 storage 调用）"""
    from storage import get_active_members as _get_active_members
    return _get_active_members(chat_id, days)