# ==========================
# services/copy_message.py - 复制消息（保留格式）
# ==========================

from telegram import Update
from telegram.ext import ContextTypes


async def copy_message_to_chat(
    context: ContextTypes.DEFAULT_TYPE,
    from_chat_id: int,
    message_id: int,
    to_chat_id: int,
    caption: str = None
):
    """
    复制消息到指定群组（保留原格式）

    支持：
    - 文本（含 Markdown/HTML 格式）
    - 图片（含描述）
    - 视频（含描述）
    - 文档（含描述）
    - 音频（含描述）
    - 动画/GIF（含描述）
    - 贴纸
    - 语音
    """
    try:
        # 获取原始消息
        original = await context.bot.forward_message(
            chat_id=to_chat_id,
            from_chat_id=from_chat_id,
            message_id=message_id
        )
        return {"success": True, "message_id": original.message_id}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def copy_message_with_format(
    context: ContextTypes.DEFAULT_TYPE,
    from_chat_id: int,
    message_id: int,
    to_chat_id: int,
    caption: str = None
):
    """
    复制消息（备用方案：逐类型复制）
    """
    try:
        # 获取原始消息对象
        # 注意：需要先 get_chat 获取消息
        # 这里使用 forward_message 作为主要方式
        result = await copy_message_to_chat(
            context, from_chat_id, message_id, to_chat_id, caption
        )
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}