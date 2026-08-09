# ==========================
# handlers/broadcast.py - 广播/转发功能
# ==========================

import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from storage import load_data, save_data, add_user, add_group
from utils.logger import log_action, log_error, log_broadcast
from utils.helpers import get_user_info, owner_only


async def send(update, context):
    if not await owner_only(update):
        return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text("📝 အသုံးပြုပုံ: /send [စာသား]\nHTML သုံးနိုင်သည်: <b>လုံးထူ</b> <i>စောင်း</i> <a href='url'>လင့်</a>")
        return

    user_id, username = get_user_info(update)
    log_action(user_id, username, "SEND", f"发送到当前聊天: {text[:50]}...")

    keyboard = [[InlineKeyboardButton("🎮 Channel သို့သွားရန်", url="https://t.me/Myanmar_GameFriendss")]]
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"📢 {text}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    await update.message.reply_text("✅ ပို့ပြီးပါပြီ။")


async def broadcast(update, context):
    if not await owner_only(update):
        return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text("📝 အသုံးပြုပုံ: /broadcast [စာသား]\nHTML သုံးနိုင်သည်။")
        return

    user_id, username = get_user_info(update)
    log_action(user_id, username, "BROADCAST_START", f"广播内容: {text[:50]}...")

    await do_broadcast(update, context, text, "text")


async def broadcast_image(update, context):
    if not await owner_only(update):
        return
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text("📸 ဓာတ်ပုံတစ်ပုံကို reply လုပ်ပြီး /broadcast_image [စာသား] ထည့်ပါ။")
        return

    user_id, username = get_user_info(update)
    log_action(user_id, username, "BROADCAST_IMAGE", "广播图片")

    caption = ' '.join(context.args) or " "
    photo = update.message.reply_to_message.photo[-1].file_id
    await do_broadcast(update, context, caption, "image", photo)


async def broadcast_group(update, context):
    if not await owner_only(update):
        return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text("📝 အသုံးပြုပုံ: /broadcast_group [စာသား]")
        return

    user_id, username = get_user_info(update)
    log_action(user_id, username, "BROADCAST_GROUP", f"广播到群组: {text[:50]}...")

    data = load_data()
    targets = [g for g in data["groups"] if g not in data.get("blacklist", [])]
    if not targets:
        await update.message.reply_text("အုပ်စုမတွေ့ပါ။")
        return
    await send_to_targets(update, context, targets, text, "text")


async def broadcast_user(update, context):
    if not await owner_only(update):
        return
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text("📝 အသုံးပြုပုံ: /broadcast_user [စာသား]")
        return

    user_id, username = get_user_info(update)
    log_action(user_id, username, "BROADCAST_USER", f"广播到用户: {text[:50]}...")

    data = load_data()
    targets = [u for u in data["users"] if u not in data.get("blacklist", [])]
    if not targets:
        await update.message.reply_text("အသုံးပြုသူမတွေ့ပါ။")
        return
    await send_to_targets(update, context, targets, text, "text")


async def do_broadcast(update, context, text, msg_type, file_id=None):
    data = load_data()
    targets = list(set(data["users"] + data["groups"]))
    targets = [t for t in targets if t not in data.get("blacklist", [])]
    if not targets:
        await update.message.reply_text("ပို့ရန်ပစ်မှတ်မရှိပါ။")
        return
    await send_to_targets(update, context, targets, text, msg_type, file_id)


async def send_to_targets(update, context, targets, text, msg_type, file_id=None):
    user_id, username = get_user_info(update)

    if update.effective_chat.type != "private":
        await context.bot.send_message(chat_id=OWNER_ID, text=f"⏳ ပို့နေသည်... ပစ်မှတ် {len(targets)} ခုသို့")

    msg = await update.message.reply_text(f"⏳ ပို့နေသည်... {len(targets)} ခုသို့")
    sent, failed = 0, 0
    keyboard = [[InlineKeyboardButton("🎮 Channel သို့သွားရန်", url="https://t.me/Myanmar_GameFriendss")]]
    markup = InlineKeyboardMarkup(keyboard)

    for target in targets:
        try:
            if msg_type == "text":
                await context.bot.send_message(chat_id=target, text=f"📢 {text}", parse_mode="HTML", reply_markup=markup)
            elif msg_type == "image":
                await context.bot.send_photo(chat_id=target, photo=file_id, caption=f"📢 {text}", parse_mode="HTML", reply_markup=markup)
            sent += 1
            await asyncio.sleep(0.1)
        except Exception:
            failed += 1

    log_broadcast("SEND_TO_TARGETS", len(targets), f"成功: {sent}, 失败: {failed}, 类型: {msg_type}")

    await msg.edit_text(f"✅ ပြီးပါပြီ။\nပို့ပြီး: {sent}\nမအောင်မြင်: {failed}")
    if update.effective_chat.type != "private":
        await context.bot.send_message(chat_id=OWNER_ID, text=f"✅ ပြီးပါပြီ။\nပို့ပြီး: {sent}\nမအောင်မြင်: {failed}")


async def forward(update, context):
    if not await owner_only(update):
        return

    user_id, username = get_user_info(update)

    if not update.message:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="❌ ဤ command ကို ဤနေရာတွင် မသုံးနိုင်ပါ။")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("📝 မက်ဆေ့ခ်ျတစ်ခုကို reply လုပ်ပြီး /forward [Chat ID] ထည့်ပါ။")
        return

    args = context.args
    if not args:
        await update.message.reply_text("📝 Chat ID ထည့်ပါ။\nဥပမာ: /forward -100123456789")
        return

    target_id = args[0]
    try:
        target_id = int(target_id)
    except ValueError:
        await update.message.reply_text("❌ Chat ID မှားနေသည်။")
        return

    log_action(user_id, username, "FORWARD", f"转发到 Chat ID: {target_id}")

    reply_msg = update.message.reply_to_message

    try:
        await context.bot.forward_message(
            chat_id=target_id,
            from_chat_id=reply_msg.chat.id,
            message_id=reply_msg.message_id
        )
        await update.message.reply_text(f"✅ Chat ID {target_id} သို့ ပြန်ပို့ပြီးပါပြီ။")
        log_action(user_id, username, "FORWARD_SUCCESS", f"目标: {target_id}")
    except Exception as e:
        log_error(user_id, username, "FORWARD_FAILED", str(e))
        await update.message.reply_text(f"❌ ပြန်ပို့မအောင်မြင်: {e}")


async def forward_all(update, context):
    if not await owner_only(update):
        return

    user_id, username = get_user_info(update)

    if not update.message:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="❌ ဤ command ကို ဤနေရာတွင် မသုံးနိုင်ပါ။")
        return

    log_action(user_id, username, "FORWARD_ALL", "转发给所有人")

    if not update.message.reply_to_message:
        await update.message.reply_text("📝 မက်ဆေ့ခ်ျတစ်ခုကို reply လုပ်ပြီး /forward_all ထည့်ပါ။")
        return

    data = load_data()
    targets = list(set(data["users"] + data["groups"]))
    targets = [t for t in targets if t not in data.get("blacklist", [])]

    if not targets:
        await update.message.reply_text("❌ ပြန်ပို့ရန် ပစ်မှတ်မရှိပါ။")
        return

    reply_msg = update.message.reply_to_message
    msg = await update.message.reply_text(f"⏳ ပြန်ပို့နေသည်... {len(targets)} ခုသို့")

    sent = 0
    failed = 0

    for target in targets:
        try:
            await context.bot.forward_message(
                chat_id=target,
                from_chat_id=reply_msg.chat.id,
                message_id=reply_msg.message_id
            )
            sent += 1
            await asyncio.sleep(0.1)
        except Exception:
            failed += 1

    log_broadcast("FORWARD_ALL", len(targets), f"成功: {sent}, 失败: {failed}")

    await msg.edit_text(
        f"✅ ပြန်ပို့ပြီးပါပြီ။\n"
        f"အောင်မြင်: {sent}\n"
        f"မအောင်မြင်: {failed}\n"
        f"စုစုပေါင်း: {len(targets)}"
    )