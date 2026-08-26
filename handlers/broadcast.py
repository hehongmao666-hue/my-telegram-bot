# ==========================
# handlers/broadcast.py - 广播/转发功能（非阻塞版）
# ==========================

import asyncio
from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_IDS
from storage import load_data, save_data
from utils.logger import logger, log_action
from utils.helpers import get_user_info, owner_only


async def send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """发送消息到当前聊天（仅管理员）"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔️ သင်တွင် ဤ command ကို အသုံးပြုခွင့်မရှိပါ။")
        return

    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("📝 /send [စာသား]")
        return

    await context.bot.send_message(chat_id=chat_id, text=text)


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """广播消息给所有用户（后台运行）"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔️ သင်တွင် ဤ command ကို အသုံးပြုခွင့်မရှိပါ။")
        return

    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("📝 /broadcast [စာသား]")
        return

    # ✅ 在后台运行广播任务
    asyncio.create_task(_run_broadcast(update, context, chat_id, text))


async def _run_broadcast(update, context, chat_id, text):
    """后台运行广播"""
    try:
        data = load_data()
        targets = list(set(data.get("users", []) + data.get("groups", [])))
        targets = [t for t in targets if t not in data.get("blacklist", [])]

        if not targets:
            await context.bot.send_message(
                chat_id=chat_id,
                text="ℹ️ ပို့ပေးရန် ပစ်မှတ်မရှိပါ။"
            )
            return

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"⏳ မက်ဆေ့ခ်ျကို {len(targets)} ဦးထံ ပို့နေပါသည်..."
        )

        success_count = 0
        fail_count = 0

        for idx, target in enumerate(targets):
            if idx % 10 == 0:
                await asyncio.sleep(0)

            try:
                await context.bot.send_message(chat_id=target, text=text)
                success_count += 1
            except Exception:
                fail_count += 1

            await asyncio.sleep(0.05)

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ မက်ဆေ့ခ်ျကို အားလုံးသို့ ပို့ပြီးပါပြီ။\n"
                 f"📊 အောင်မြင်: {success_count}\n"
                 f"❌ မအောင်မြင်: {fail_count}"
        )

        user_id_int, username = get_user_info(update)
        log_action(
            user_id_int, username,
            "BROADCAST",
            f"广播: {text[:30]}... | 成功: {success_count}/{len(targets)}"
        )

    except Exception as e:
        logger.exception("[Broadcast] Error")
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"❌ အမှားရှိသည်: {e}"
        )


async def broadcast_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """广播图片给所有用户（后台运行）"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    message = update.message

    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔️ သင်တွင် ဤ command ကို အသုံးပြုခွင့်မရှိပါ။")
        return

    if not message.reply_to_message or not message.reply_to_message.photo:
        await update.message.reply_text("📝 ဓာတ်ပုံကို Reply လုပ်ပြီး /broadcast_image ထည့်ပါ။")
        return

    caption = " ".join(context.args) if context.args else ""

    # ✅ 在后台运行广播任务
    asyncio.create_task(_run_broadcast_image(update, context, chat_id, message, caption))


async def _run_broadcast_image(update, context, chat_id, message, caption):
    """后台运行图片广播"""
    try:
        data = load_data()
        targets = list(set(data.get("users", []) + data.get("groups", [])))
        targets = [t for t in targets if t not in data.get("blacklist", [])]

        if not targets:
            await context.bot.send_message(
                chat_id=chat_id,
                text="ℹ️ ပို့ပေးရန် ပစ်မှတ်မရှိပါ။"
            )
            return

        photo = message.reply_to_message.photo[-1].file_id

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"⏳ ဓာတ်ပုံကို {len(targets)} ဦးထံ ပို့နေပါသည်..."
        )

        success_count = 0
        fail_count = 0

        for idx, target in enumerate(targets):
            if idx % 10 == 0:
                await asyncio.sleep(0)

            try:
                await context.bot.send_photo(chat_id=target, photo=photo, caption=caption)
                success_count += 1
            except Exception:
                fail_count += 1

            await asyncio.sleep(0.05)

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ ဓာတ်ပုံကို အားလုံးသို့ ပို့ပြီးပါပြီ။\n"
                 f"📊 အောင်မြင်: {success_count}\n"
                 f"❌ မအောင်မြင်: {fail_count}"
        )

        user_id_int, username = get_user_info(update)
        log_action(
            user_id_int, username,
            "BROADCAST_IMAGE",
            f"广播图片 | 成功: {success_count}/{len(targets)}"
        )

    except Exception as e:
        logger.exception("[BroadcastImage] Error")
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"❌ အမှားရှိသည်: {e}"
        )


async def broadcast_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """广播到所有群组（后台运行）"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔️ သင်တွင် ဤ command ကို အသုံးပြုခွင့်မရှိပါ။")
        return

    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("📝 /broadcast_group [စာသား]")
        return

    asyncio.create_task(_run_broadcast_group(update, context, chat_id, text))


async def _run_broadcast_group(update, context, chat_id, text):
    """后台运行群组广播"""
    try:
        data = load_data()
        targets = [g for g in data.get("groups", []) if g not in data.get("blacklist", [])]

        if not targets:
            await context.bot.send_message(
                chat_id=chat_id,
                text="ℹ️ ပို့ပေးရန် အုပ်စုမရှိပါ။"
            )
            return

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"⏳ မက်ဆေ့ခ်ျကို အုပ်စု {len(targets)} ခုထံ ပို့နေပါသည်..."
        )

        success_count = 0
        fail_count = 0

        for idx, target in enumerate(targets):
            if idx % 10 == 0:
                await asyncio.sleep(0)

            try:
                await context.bot.send_message(chat_id=target, text=text)
                success_count += 1
            except Exception:
                fail_count += 1

            await asyncio.sleep(0.05)

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ မက်ဆေ့ခ်ျကို အုပ်စုများသို့ ပို့ပြီးပါပြီ။\n"
                 f"📊 အောင်မြင်: {success_count}\n"
                 f"❌ မအောင်မြင်: {fail_count}"
        )

    except Exception as e:
        logger.exception("[BroadcastGroup] Error")
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"❌ အမှားရှိသည်: {e}"
        )


async def broadcast_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """广播到所有用户（后台运行）"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔️ သင်တွင် ဤ command ကို အသုံးပြုခွင့်မရှိပါ။")
        return

    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("📝 /broadcast_user [စာသား]")
        return

    asyncio.create_task(_run_broadcast_user(update, context, chat_id, text))


async def _run_broadcast_user(update, context, chat_id, text):
    """后台运行用户广播"""
    try:
        data = load_data()
        targets = [u for u in data.get("users", []) if u not in data.get("blacklist", [])]

        if not targets:
            await context.bot.send_message(
                chat_id=chat_id,
                text="ℹ️ ပို့ပေးရန် အသုံးပြုသူမရှိပါ။"
            )
            return

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"⏳ မက်ဆေ့ခ်ျကို အသုံးပြုသူ {len(targets)} ဦးထံ ပို့နေပါသည်..."
        )

        success_count = 0
        fail_count = 0

        for idx, target in enumerate(targets):
            if idx % 10 == 0:
                await asyncio.sleep(0)

            try:
                await context.bot.send_message(chat_id=target, text=text)
                success_count += 1
            except Exception:
                fail_count += 1

            await asyncio.sleep(0.05)

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ မက်ဆေ့ခ်ျကို အသုံးပြုသူများသို့ ပို့ပြီးပါပြီ။\n"
                 f"📊 အောင်မြင်: {success_count}\n"
                 f"❌ မအောင်မြင်: {fail_count}"
        )

    except Exception as e:
        logger.exception("[BroadcastUser] Error")
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"❌ အမှားရှိသည်: {e}"
        )


async def forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """转发消息到指定 Chat ID（后台运行）"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    message = update.message

    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔️ သင်တွင် ဤ command ကို အသုံးပြုခွင့်မရှိပါ။")
        return

    if not message.reply_to_message:
        await update.message.reply_text(
            "📝 အသုံးပြုပုံ:\n"
            "/forward [Chat ID] - မက်ဆေ့ခ်ျကို Reply လုပ်ပြီး command ထည့်ပါ။"
        )
        return

    args = context.args
    if not args:
        await update.message.reply_text("❌ ကျေးဇူးပြု၍ Chat ID ထည့်ပါ။\n例如: /forward -100123456789")
        return

    target_chat_id = args[0]
    reply_msg = message.reply_to_message

    asyncio.create_task(_run_forward(update, context, chat_id, target_chat_id, reply_msg))


async def _run_forward(update, context, chat_id, target_chat_id, reply_msg):
    """后台运行转发"""
    try:
        await context.bot.forward_message(
            chat_id=target_chat_id,
            from_chat_id=reply_msg.chat.id,
            message_id=reply_msg.message_id
        )
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ မက်ဆေ့ခ်ျကို {target_chat_id} သို့ ပြန်ပို့ပြီးပါပြီ။"
        )
        logger.info(f"[Forward] User: {update.effective_user.id} | To: {target_chat_id}")
    except Exception as e:
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"❌ ပြန်ပို့ရာတွင် အမှားရှိသည်: {e}"
        )
        logger.error(f"[Forward] Error: {e}")


async def forward_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """转发消息给所有用户（后台运行）"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    message = update.message

    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔️ သင်တွင် ဤ command ကို အသုံးပြုခွင့်မရှိပါ။")
        return

    if not message.reply_to_message:
        await update.message.reply_text(
            "📝 အသုံးပြုပုံ:\n"
            "မက်ဆေ့ခ်ျကို Reply လုပ်ပြီး /forward_all ထည့်ပါ။"
        )
        return

    reply_msg = message.reply_to_message

    asyncio.create_task(_run_forward_all(update, context, chat_id, reply_msg))


async def _run_forward_all(update, context, chat_id, reply_msg):
    """后台运行转发给所有用户"""
    try:
        data = load_data()
        targets = list(set(data.get("users", []) + data.get("groups", [])))
        targets = [t for t in targets if t not in data.get("blacklist", [])]

        if not targets:
            await context.bot.send_message(
                chat_id=chat_id,
                text="ℹ️ ပို့ပေးရန် ပစ်မှတ်မရှိပါ။"
            )
            return

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"⏳ မက်ဆေ့ခ်ျကို {len(targets)} ဦးထံ ပို့နေပါသည်..."
        )

        success_count = 0
        fail_count = 0

        for idx, target in enumerate(targets):
            if idx % 10 == 0:
                await asyncio.sleep(0)

            try:
                await context.bot.forward_message(
                    chat_id=target,
                    from_chat_id=reply_msg.chat.id,
                    message_id=reply_msg.message_id
                )
                success_count += 1
            except Exception:
                fail_count += 1

            if idx % 50 == 0 and idx > 0:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"📊 {idx}/{len(targets)} ဦးထံ ပို့ပြီးပါပြီ။"
                )

            await asyncio.sleep(0.05)

        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ မက်ဆေ့ခ်ျကို အားလုံးသို့ ပြန်ပို့ပြီးပါပြီ။\n"
                 f"📊 အောင်မြင်: {success_count}\n"
                 f"❌ မအောင်မြင်: {fail_count}"
        )

        logger.info(f"[ForwardAll] User: {update.effective_user.id} | Success: {success_count}, Failed: {fail_count}, Total: {len(targets)}")

        user_id_int, username = get_user_info(update)
        log_action(
            user_id_int, username,
            "FORWARD_ALL",
            f"转发消息 | 成功: {success_count}/{len(targets)}"
        )

    except Exception as e:
        logger.exception("[ForwardAll] Error")
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"❌ အမှားရှိသည်: {e}"
        )