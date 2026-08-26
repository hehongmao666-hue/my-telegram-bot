# ==========================
# handlers/announce.py - 公告指令处理（V3.1 完整修复版）
# ==========================

import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import ADMIN_IDS, announcement_running
from storage import load_announce_data, save_announce_data
from services.mention import (
    build_announcement_header,
    send_mentions,
    build_finish_message
)
from utils.logger import logger, log_action
from utils.helpers import get_user_info


async def announce(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    发送公告（仅管理员）
    支持两种模式：
    1. /announce [文本] - 发送纯文本公告
    2. 回复消息 + /announce - 转发消息（保留格式）
    """
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    message = update.message

    # ========== 权限检查 ==========
    if user_id not in ADMIN_IDS:
        await context.bot.send_message(
            chat_id=chat_id,
            text="⛔️ သင်တွင် ဤ command ကို အသုံးပြုခွင့်မရှိပါ။"
        )
        return

    # ========== 私聊检查 ==========
    if update.effective_chat.type == "private":
        await context.bot.send_message(
            chat_id=chat_id,
            text="❌ ဤ command ကို Group တွင်သာ အသုံးပြုနိုင်သည်။"
        )
        return

    # ========== 检查是否回复了消息（复制消息模式） ==========
    if message and message.reply_to_message:
        await handle_announce_copy(update, context, message, chat_id)
        return

    # ========== 文本模式 ==========
    text = " ".join(context.args) if context.args else ""
    if not text:
        await context.bot.send_message(
            chat_id=chat_id,
            text="📝 အသုံးပြုပုံ\n\n"
                 "1️⃣ /announce [စာသား] - စာသားကြေငြာ\n"
                 "2️⃣ မက်ဆေ့ခ်ျကို Reply လုပ်ပြီး /announce - မက်ဆေ့ခ်ျပြန်ပို့ကြေငြာ"
        )
        return

    await handle_announce_text(update, context, message, chat_id, text)


async def handle_announce_text(update, context, message, chat_id, text):
    """处理文本公告"""
    chat_key = str(chat_id)
    
    if announcement_running.get(chat_key, False):
        await context.bot.send_message(
            chat_id=chat_id,
            text="⏳ ကြေငြာတစ်ခု ပို့နေပါသည်။ ကျေးဇူးပြု၍ စောင့်ပါ။"
        )
        return

    announcement_running[chat_key] = True

    try:
        from storage import get_active_members
        members = get_active_members(chat_id, days=30)
        total = len(members)

        logger.info(f"[Announcement] Start (Text) | User: {update.effective_user.id} | Members: {total}")

        if total == 0:
            announcement_running[chat_key] = False
            await context.bot.send_message(
                chat_id=chat_id,
                text="ℹ️ ပို့ပေးရန် အဖွဲ့ဝင်မရှိပါ။"
            )
            return

        # ========== 发送公告头部 ==========
        header = build_announcement_header(text)
        await context.bot.send_message(chat_id=chat_id, text=header)
        logger.info(f"[Announcement] Header Sent")

        # ========== 发送 @ 列表 ==========
        stats = await send_mentions(
            context=context,
            chat_id=chat_id,
            members=members,
            stop_flag=announcement_running
        )

        # ========== 发送完成消息 ==========
        finish_text = build_finish_message(
            success=stats["success"],
            total=total,
            failed=stats["failed"],
            skipped=stats["skipped"]
        )
        await context.bot.send_message(chat_id=chat_id, text=finish_text)

        logger.info(
            f"[Announcement] Finished | Success: {stats['success']}, "
            f"Failed: {stats['failed']}, Skipped: {stats['skipped']}, Total: {total}"
        )

        user_id_int, username = get_user_info(update)
        log_action(
            user_id_int, username,
            "ANNOUNCE",
            f"内容: {text[:30]}... | 成功: {stats['success']}/{total}"
        )

    except Exception as e:
        logger.exception("[Announcement] Error")
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"❌ အမှားရှိသည်: {e}"
        )

    finally:
        announcement_running[chat_key] = False


async def handle_announce_copy(update, context, message, chat_id):
    """处理复制消息公告（保留原格式）"""
    chat_key = str(chat_id)
    
    if announcement_running.get(chat_key, False):
        await context.bot.send_message(
            chat_id=chat_id,
            text="⏳ ကြေငြာတစ်ခု ပို့နေပါသည်။ ကျေးဇူးပြု၍ စောင့်ပါ။"
        )
        return

    announcement_running[chat_key] = True

    try:
        from storage import get_active_members
        members = get_active_members(chat_id, days=30)
        total = len(members)

        logger.info(f"[Announcement] Start (Copy) | User: {update.effective_user.id} | Members: {total}")

        if total == 0:
            announcement_running[chat_key] = False
            await context.bot.send_message(
                chat_id=chat_id,
                text="ℹ️ ပို့ပေးရန် အဖွဲ့ဝင်မရှိပါ။"
            )
            return

        # ========== 发送公告头部（使用复制的消息） ==========
        reply_msg = message.reply_to_message

        try:
            await context.bot.forward_message(
                chat_id=chat_id,
                from_chat_id=reply_msg.chat.id,
                message_id=reply_msg.message_id
            )
            logger.info(f"[Announcement] Copied message sent")
        except Exception as e:
            logger.error(f"[Announcement] Copy failed: {e}")
            header = build_announcement_header(
                reply_msg.text or reply_msg.caption or "📢 ကြေငြာချက်"
            )
            await context.bot.send_message(chat_id=chat_id, text=header)

        # ========== 发送 @ 列表 ==========
        stats = await send_mentions(
            context=context,
            chat_id=chat_id,
            members=members,
            stop_flag=announcement_running
        )

        # ========== 发送完成消息 ==========
        finish_text = build_finish_message(
            success=stats["success"],
            total=total,
            failed=stats["failed"],
            skipped=stats["skipped"]
        )
        await context.bot.send_message(chat_id=chat_id, text=finish_text)

        logger.info(
            f"[Announcement] Finished (Copy) | Success: {stats['success']}, "
            f"Failed: {stats['failed']}, Skipped: {stats['skipped']}, Total: {total}"
        )

        user_id_int, username = get_user_info(update)
        log_action(
            user_id_int, username,
            "ANNOUNCE_COPY",
            f"复制消息公告 | 成功: {stats['success']}/{total}"
        )

    except Exception as e:
        logger.exception("[Announcement] Error")
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"❌ အမှားရှိသည်: {e}"
        )

    finally:
        announcement_running[chat_key] = False


async def stop_announce(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """停止公告"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    chat_key = str(chat_id)

    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔️ သင်တွင် ဤ command ကို အသုံးပြုခွင့်မရှိပါ။")
        return

    # 检查是否有公告在运行
    if not announcement_running.get(chat_key, False):
        await update.message.reply_text("ℹ️ လက်ရှိ ကြေငြာတစ်ခုမှ ပို့နေခြင်းမရှိပါ။")
        return

    # 设置停止标志
    announcement_running[chat_key] = False
    await update.message.reply_text("🛑 ကြေငြာကို ရပ်လိုက်ပါပြီ။")
    logger.info(f"[Announcement] Stopped by user: {user_id} | Chat: {chat_id}")

async def announce_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """公告按钮回调"""
    query = update.callback_query
    await query.answer()

    if not query.data.startswith("announce_subscribe_"):
        return

    user = query.from_user
    chat_id = query.message.chat.id

    data = load_announce_data()
    subscribers = data.get("subscribers", [])

    if user.id in subscribers:
        await query.answer("✅ သင်သည် သတင်းရယူပြီးဖြစ်သည်။", show_alert=True)
        return

    subscribers.append(user.id)
    data["subscribers"] = subscribers
    save_announce_data(data)

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"🔔 {user.mention_html()} သည် အသိပေးချက်ကို လက်ခံထားပြီး။ (စုစုပေါင်း {len(subscribers)} ယောက်)",
        parse_mode="HTML"
    )

    try:
        keyboard = [
            [InlineKeyboardButton("✅ သတင်းရယူပြီး", callback_data="already_subscribed")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_reply_markup(reply_markup=reply_markup)
    except Exception:
        pass

    await query.answer(f"✅ {user.first_name} အတွက် အောင်မြင်ပါပြီ။")


async def already_subscribed_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """已订阅用户再次点击按钮"""
    query = update.callback_query
    await query.answer()
    await query.answer("✅ သင်သည် သတင်းရယူပြီးဖြစ်သည်။", show_alert=True)