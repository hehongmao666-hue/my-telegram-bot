from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, CallbackQueryHandler
import json
import os
import asyncio
import time
import re
import random
from datetime import datetime
import logging
from dotenv import load_dotenv

# ============ 加载环境变量 ============
load_dotenv()

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")

OWNER_ID = int(os.environ.get("OWNER_ID", 5300063761))

DATA_FILE = "data.json"
SCHEDULE_FILE = "schedule.json"
PRESET_FILE = "presets.json"

# ============ 日志系统 ============

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

# ============ 广告功能 ============

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"users": [], "groups": [], "blacklist": []}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_schedule():
    if os.path.exists(SCHEDULE_FILE):
        with open(SCHEDULE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_schedule(s):
    with open(SCHEDULE_FILE, "w", encoding="utf-8") as f:
        json.dump(s, f, ensure_ascii=False, indent=2)

def load_presets():
    if os.path.exists(PRESET_FILE):
        with open(PRESET_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_presets(p):
    with open(PRESET_FILE, "w", encoding="utf-8") as f:
        json.dump(p, f, ensure_ascii=False, indent=2)

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

async def owner_only(update):
    uid = update.effective_user.id
    if uid != OWNER_ID:
        await update.message.reply_text("⛔️ သင့်တွင် ဤ command ကိုသုံးခွင့်မရှိပါ။")
        return False
    return True

async def start(update, context):
    uid = update.effective_user.id
    cid = update.effective_chat.id
    add_user(uid)
    if cid != uid:
        add_group(cid)
    
    user_id, username = get_user_info(update)
    log_action(user_id, username, "START", "用户启动Bot")
    
    keyboard = [
        [InlineKeyboardButton("🎮 ချစ်သူရှာမယ် Gp 1", url="https://t.me/Myanmar_GameFriendss", style="primary")],
        [InlineKeyboardButton("🎮 ချစ်သူရှာမယ် Gp 2", url="https://t.me/Myanmar_GameFriends", style="primary")],
        [InlineKeyboardButton("🛒 Game Friend Shop ဆိုင် 1", url="https://t.me/PUBGUCshop_01", style="success")],
        [InlineKeyboardButton("🎰 စလော့နှင့်ငါးပစ်ဂိမ်းများ", callback_data="random_link", style="success")],
        [InlineKeyboardButton("👤 အုံနာ ဆက်သွယ်ရန်", url="https://t.me/MCLP1_1", style="danger")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "♥️ *ဂိမ်းချစ်သူများ စုံစည်းရာရပ်ကွက် ♥️*\n"
        "📌 *ချစ်သူရှာမယ်။ ဂိမ်းဆော့ဖော်ရှာမယ်။ စကားပြောကြမယ်။*\n"
        "📌 *အောက်ပါခလုတ်များမှ တစ်ဆင့် ဝင်ရောက်နိုင်ပါသည်။*\n\n"
        "➡️ *ဂိမ်းနဲ့ပတ်သတ်တာတစ်နေရာထဲမှာ လိုချင်တာ အကုန်ရနေပီ။✅*\n"
        "➡️ *အပြောနဲ့အလုပ် တိတိကျကျ မှန်မှန်ကန်ကန် စိတ်ချယုံကြည့်ချင်တယ်ဆိုရင် အုံနာကို ဆက်သွယ်ပါ။🙏*",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def help(update, context):
    await update.message.reply_text(
        "🤖 *Bot Commands*\n\n"
        "/start - ကြိုဆိုစာမျက်နှာ\n"
        "/stats - စာရင်းအင်းကြည့်ရန်\n"
        "/count - အုပ်စုဝင်အရေအတွက်\n\n"
        "📤 *ကြော်ငြာပို့ရန် (Owner only)*\n"
        "/send [စာသား] - လက်ရှိ chat သို့\n"
        "/broadcast [စာသား] - အားလုံးသို့\n"
        "/broadcast_image - ဓာတ်ပုံ+စာသားပို့ရန်\n"
        "/broadcast_group [စာသား] - အုပ်စုများသို့\n"
        "/broadcast_user [စာသား] - အသုံးပြုသူများသို့\n\n"
        "⏰ အချိန်မှန်ပို့ရန် (Owner only)\n"
        "/at [YYYY-MM-DD HH:MM] [စာသား]\n"
        "/in [30s/5m/2h] [စာသား]\n"
        "/list_schedule - အချိန်မှန်စာရင်း\n"
        "/cancel_schedule [id] - ဖျက်ရန်\n\n"
        "📋 Presets (Owner only)\n"
        "/preset list - သိမ်းထားသောစာသားများ\n"
        "/preset save [အမည်] [စာသား]\n"
        "/preset send [အမည်]\n\n"
        "📤 မက်ဆေ့ခ်ျပြန်ပို့ရန် (Owner only)\n"
        "/forward [Chat ID] - မက်ဆေ့ခ်ျပြန်ပို့ရန်\n"
        "/forward_all - အားလုံးသို့ပြန်ပို့ရန်\n\n"
        "🎮 *ဂိမ်း (အားလုံးသုံးနိုင်သည်)*\n"
        "/game - စွန့်စားခန်းဂိမ်းစမည်\n"
        "/restartgame - ဂိမ်းပြန်စမည်\n"
        "/back - နောက်တစ်ဆင့်ပြန်သွားမည်\n\n"
        "🛠 *အခြား (Owner only)*\n"
        "/blacklist add/remove/list\n"
        "/cancel - လုပ်ဆောင်နေသော broadcast ရပ်ရန်",
        parse_mode="Markdown"
    )

async def stats(update, context):
    if not await owner_only(update):
        return
    data = load_data()
    await update.message.reply_text(
        f"📊 *စာရင်းအင်း*\n\n👤 အသုံးပြုသူ: {len(data['users'])}\n👥 အုပ်စု: {len(data['groups'])}\n🚫 Blacklist: {len(data.get('blacklist', []))}",
        parse_mode="Markdown"
    )

async def count(update, context):
    if not await owner_only(update):
        return
    try:
        n = await context.bot.get_chat_member_count(update.effective_chat.id)
        await update.message.reply_text(f"👥 ဤအုပ်စုတွင် အဖွဲ့ဝင် {n} ဦးရှိသည်။")
    except Exception as e:
        await update.message.reply_text(f"❌ အမှားရှိသည်: {e}")

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

async def at(update, context):
    if not await owner_only(update):
        return
    args = context.args
    if len(args) < 3:
        await update.message.reply_text("📅 အသုံးပြုပုံ: /at [YYYY-MM-DD HH:MM] [စာသား]\nဥပမာ: /at 2026-12-31 23:59 နှစ်သစ်ကူးမင်္ဂလာပါ!")
        return
    try:
        dt_str = f"{args[0]} {args[1]}"
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        text = ' '.join(args[2:])
        schedule = load_schedule()
        schedule.append({
            "id": int(time.time()),
            "time": dt.timestamp(),
            "text": text,
            "type": "text"
        })
        save_schedule(schedule)
        await update.message.reply_text(f"✅ {dt_str} တွင် ပို့ရန် သိမ်းပြီးပါပြီ။\nစာသား: {text}")
    except Exception as e:
        await update.message.reply_text(f"❌ အမှားရှိသည်: {e}")

async def in_(update, context):
    if not await owner_only(update):
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("⏰ အသုံးပြုပုံ: /in [30s/5m/2h] [စာသား]")
        return
    try:
        delay_str = args[0]
        match = re.match(r"(\d+)(s|m|h)", delay_str)
        if not match:
            await update.message.reply_text("❌ ပုံစံမှားသည်။ ဥပမာ: 30s, 5m, 2h")
            return
        val, unit = int(match.group(1)), match.group(2)
        seconds = val * {"s": 1, "m": 60, "h": 3600}[unit]
        text = ' '.join(args[1:])
        schedule = load_schedule()
        schedule.append({
            "id": int(time.time()),
            "time": time.time() + seconds,
            "text": text,
            "type": "text"
        })
        save_schedule(schedule)
        await update.message.reply_text(f"✅ {delay_str} အတွင်းပို့ရန် သိမ်းပြီးပါပြီ။\nစာသား: {text}")
    except Exception as e:
        await update.message.reply_text(f"❌ အမှားရှိသည်: {e}")

async def list_schedule(update, context):
    if not await owner_only(update):
        return
    sched = load_schedule()
    if not sched:
        await update.message.reply_text("📭 အချိန်မှန်ပို့ရန် သိမ်းထားခြင်းမရှိပါ။")
        return
    lines = []
    for item in sched:
        dt = datetime.fromtimestamp(item["time"]).strftime("%Y-%m-%d %H:%M")
        lines.append(f"ID: {item['id']} | {dt} | {item['text'][:30]}...")
    await update.message.reply_text("\n".join(lines))

async def cancel_schedule(update, context):
    if not await owner_only(update):
        return
    if not context.args:
        await update.message.reply_text("📝 အသုံးပြုပုံ: /cancel_schedule [id]")
        return
    try:
        sid = int(context.args[0])
        sched = load_schedule()
        new_sched = [s for s in sched if s["id"] != sid]
        if len(new_sched) == len(sched):
            await update.message.reply_text("❌ ID မတွေ့ပါ။")
            return
        save_schedule(new_sched)
        await update.message.reply_text(f"✅ Schedule ID {sid} ကိုဖျက်ပြီးပါပြီ။")
    except Exception as e:
        await update.message.reply_text(f"❌ အမှားရှိသည်: {e}")

async def preset(update, context):
    if not await owner_only(update):
        return
    args = context.args
    if not args:
        await update.message.reply_text("📝 အသုံးပြုပုံ:\n/preset list\n/preset save [အမည်] [စာသား]\n/preset delete [အမည်]\n/preset send [အမည်]")
        return
    action = args[0].lower()
    presets = load_presets()
    
    if action == "list":
        if not presets:
            await update.message.reply_text("📭 သိမ်းထားသောစာသားမရှိပါ။")
            return
        await update.message.reply_text("\n".join([f"📌 {k}" for k in presets.keys()]))
    
    elif action == "save":
        if len(args) < 3:
            await update.message.reply_text("📝 /preset save [အမည်] [စာသား]")
            return
        name = args[1]
        text = ' '.join(args[2:])
        presets[name] = text
        save_presets(presets)
        await update.message.reply_text(f"✅ '{name}' ကိုသိမ်းပြီးပါပြီ။")
    
    elif action == "delete":
        if len(args) < 2:
            await update.message.reply_text("📝 /preset delete [အမည်]")
            return
        name = args[1]
        if name in presets:
            del presets[name]
            save_presets(presets)
            await update.message.reply_text(f"✅ '{name}' ကိုဖျက်ပြီးပါပြီ။")
        else:
            await update.message.reply_text("❌ မတွေ့ပါ။")
    
    elif action == "send":
        if len(args) < 2:
            await update.message.reply_text("📝 /preset send [အမည်]")
            return
        name = args[1]
        if name in presets:
            await do_broadcast(update, context, presets[name], "text")
        else:
            await update.message.reply_text("❌ မတွေ့ပါ။")

async def blacklist(update, context):
    if not await owner_only(update):
        return
    args = context.args
    data = load_data()
    if len(args) < 2:
        await update.message.reply_text("📝 အသုံးပြုပုံ:\n/blacklist add [id]\n/blacklist remove [id]\n/blacklist list")
        return
    action = args[0].lower()
    try:
        uid = int(args[1])
        if action == "add":
            if uid not in data["blacklist"]:
                data["blacklist"].append(uid)
                save_data(data)
                await update.message.reply_text(f"✅ {uid} ကို blacklist ထည့်ပြီးပါပြီ။")
            else:
                await update.message.reply_text("ℹ️ ရှိပြီးသားဖြစ်သည်။")
        elif action == "remove":
            if uid in data["blacklist"]:
                data["blacklist"].remove(uid)
                save_data(data)
                await update.message.reply_text(f"✅ {uid} ကို blacklist မှဖယ်ပြီးပါပြီ။")
            else:
                await update.message.reply_text("ℹ️ မတွေ့ပါ။")
    except:
        await update.message.reply_text("❌ ID မှားယွင်းနေသည်။")

async def cancel(update, context):
    if not await owner_only(update):
        return
    await update.message.reply_text("ℹ️ အချိန်မှန်ပို့ရန်ကိုဖျက်ရန် /cancel_schedule [id] ကိုသုံးပါ။")

# ============ 消息转发功能 ============

async def forward(update, context):
    if not await owner_only(update):
        return
    
    user_id, username = get_user_info(update)
    
    # ✅ 检查 update.message 是否存在
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
    
    # ✅ 检查 update.message 是否存在
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

# ============ 随机链接 ============

RANDOM_LINKS = [
    "https://mm6805.com/?id=530467052",
    "https://mm6801.com/?id=530467052",
]

async def random_link_callback(update, context):
    """处理随机链接按钮点击"""
    query = update.callback_query
    await query.answer()
    
    selected_url = random.choice(RANDOM_LINKS)
    
    keyboard = [
        [InlineKeyboardButton("🔗 နှိပ်ပြီးဝင်ရောက်ရန်", url=selected_url, style="success")],
        [InlineKeyboardButton("🔙 နောက်သို့ပြန်သွားရန်", callback_data="back_to_menu",style="danger")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"🎰 သင့်အတွက် ရွေးချယ်ထားသော လင့်ခ်:\n\n`{selected_url}`\n\nအောက်ပါခလုတ်ကိုနှိပ်ပြီး ဝင်ရောက်ပါ။",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

async def back_to_menu_callback(update, context):
    """返回主菜单"""
    query = update.callback_query
    await query.answer()
    
    keyboard = [
        [InlineKeyboardButton("🎮 ချစ်သူရှာမယ် Gp 1", url="https://t.me/Myanmar_GameFriendss", style="primary")],
        [InlineKeyboardButton("🎮 ချစ်သူရှာမယ် Gp 2", url="https://t.me/Myanmar_GameFriends", style="primary")],
        [InlineKeyboardButton("🛒 Game Friend Shop ဆိုင် 1", url="https://t.me/PUBGUCshop_01", style="success")],
        [InlineKeyboardButton("🎰 စလော့နှင့်ငါးပစ်ဂိမ်းများ", callback_data="random_link", style="success")],
        [InlineKeyboardButton("👤 အုံနာ ဆက်သွယ်ရန်", url="https://t.me/MCLP1_1", style="danger")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "♥️ *ဂိမ်းချစ်သူများ စုံစည်းရာရပ်ကွက် ♥️*\n"
        "📌 *ချစ်သူရှာမယ်။ ဂိမ်းဆော့ဖော်ရှာမယ်။ စကားပြောကြမယ်။*\n"
        "📌 *အောက်ပါခလုတ်များမှ တစ်ဆင့် ဝင်ရောက်နိုင်ပါသည်။*\n\n"
        "➡️ *ဂိမ်းနဲ့ပတ်သတ်တာတစ်နေရာထဲမှာ လိုချင်တာ အကုန်ရနေပီ။✅*\n"
        "➡️ *အပြောနဲ့အလုပ် တိတိကျကျ မှန်မှန်ကန်ကန် စိတ်ချယုံကြည့်ချင်တယ်ဆိုရင် အုံနာကို ဆက်သွယ်ပါ။🙏*",
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

# ============ 🎮 30关通关游戏 ============

GAME_STATE_FILE = "game_states.json"

def load_game_states():
    if os.path.exists(GAME_STATE_FILE):
        with open(GAME_STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_game_states(states):
    with open(GAME_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(states, f, ensure_ascii=False, indent=2)

def get_player_state(user_id):
    states = load_game_states()
    return states.get(user_id)

def is_game_owner(user_id, owner_id):
    return str(user_id) == str(owner_id)

LEVELS = {
    1: {"name": "🌲 မြူခိုးတော", "desc": "မြူခိုးတောအုပ်ထဲမှာ လမ်းပျောက်နေတယ်။ ထွက်ပေါက်ကိုရှာပါ။"},
    2: {"name": "🏔️ နှင်းတောင်", "desc": "နှင်းတောင်ထိပ်ကိုတက်ပြီး အလံကိုစိုက်ပါ။"},
    3: {"name": "🏜️ သဲကန္တာရမြို့", "desc": "သဲကန္တာရထဲမှာ ပျောက်ဆုံးနေတဲ့မြို့ကိုရှာပါ။"},
    4: {"name": "🌋 မီးတောင်ချိုင့်", "desc": "မီးတောင်ထဲက မီးအိမ်သားကိုအနိုင်ယူပါ။"},
    5: {"name": "🌊 ရေအောက်နန်းတော်", "desc": "ရေအောက်နန်းတော်ထဲက သုံးခွသွားကိုရှာပါ။"},
    6: {"name": "🏰 မှောင်မိုက်ရဲတိုက်", "desc": "မှောင်မိုက်ရဲတိုက်ထဲက သူရဲကောင်းကိုအနိုင်ယူပါ။"},
    7: {"name": "🌌 ကြယ်မျှော်စင်", "desc": "ကြယ်မျှော်စင်ထဲက ကြယ်ပဟေဠိကိုဖြေပါ။"},
    8: {"name": "🐉 နဂါးဂူ", "desc": "နဂါးဂူထဲက နဂါးငယ်ကိုအနိုင်ယူပါ။"},
    9: {"name": "🌑 ကွက်လပ်နယ်မြေ", "desc": "ကွက်လပ်နယ်မြေထဲက နှလုံးသားကိုရှာပါ။"},
    10: {"name": "👑 နောက်ဆုံးပလ္လင်", "desc": "မှောင်မိုက်ဘုရင်ကိုအနိုင်ယူပြီး ငြိမ်းချမ်းရေးကိုပြန်လည်ရယူပါ။"},
}

LEVEL_SCENES = {}

for level in range(1, 11):
    base_name = LEVELS[level]["name"].split(" ")[1] if " " in LEVELS[level]["name"] else f"关卡{level}"
    LEVEL_SCENES[f"level_{level}_start"] = {
        "text": f"📍 *{LEVELS[level]['name']}*\n\n{LEVELS[level]['desc']}\n\nလမ်းကြောင်းသုံးခုကွဲနေတယ်။ ဘယ်ကိုသွားမလဲ?",
        "options": {
            f"level_{level}_path1": "🌿 လမ်းကြောင်း ၁",
            f"level_{level}_path2": "🌲 လမ်းကြောင်း ၂",
            f"level_{level}_path3": "🏔️ လမ်းကြောင်း ၃"
        }
    }
    LEVEL_SCENES[f"level_{level}_path1"] = {
        "text": f"🌿 လမ်းကြောင်းပေါ်မှာ ထူးဆန်းတဲ့အရာတစ်ခုကိုတွေ့တယ်။\n\nဆက်သွားမလား?",
        "options": {
            f"level_{level}_boss": "⚔️ ရှေ့ဆက်မယ်",
            f"level_{level}_start": "🔙 ပြန်သွားမယ်"
        }
    }
    LEVEL_SCENES[f"level_{level}_path2"] = {
        "text": f"🌲 ဒီလမ်းက အန္တရာယ်များတယ်။ သတ္တဝါတွေရဲ့အသံတွေကြားနေရတယ်။",
        "options": {
            f"level_{level}_boss": "⚔️ ရှေ့ဆက်မယ်",
            f"level_{level}_start": "🔙 ပြန်သွားမယ်"
        }
    }
    LEVEL_SCENES[f"level_{level}_path3"] = {
        "text": f"🏔️ ဒီလမ်းက သာယာပေမယ့် လှည့်ကွက်တွေရှိတယ်။",
        "options": {
            f"level_{level}_boss": "⚔️ ရှေ့ဆက်မယ်",
            f"level_{level}_start": "🔙 ပြန်သွားမယ်"
        }
    }
    LEVEL_SCENES[f"level_{level}_boss"] = {
        "text": f"⚔️ *{LEVELS[level]['name']} ရဲ့ အဆုံးစွန်စိန်ခေါ်မှု!*\n\nဒီနေရာကို ရောက်ဖို့ မင်းအောင်မြင်ပြီ။\n\nအနိုင်ရဖို့ နောက်ဆုံးတိုက်ပွဲကိုရင်ဆိုင်ပါ!",
        "options": {}
    }

for level in range(1, 11):
    LEVEL_SCENES[f"level_{level}_win"] = {
        "text": f"🎉 *{LEVELS[level]['name']} ကိုအောင်မြင်ပြီ!*\n\nမင်းဟာ ဒီအဆင့်ကိုကျော်ဖြတ်နိုင်ခဲ့တယ်။\n\nနောက်အဆင့်ကိုဆက်သွားမလား?",
        "options": {}
    }

def get_or_create_player(user_id):
    states = load_game_states()
    if user_id not in states:
        states[user_id] = {
            "name": generate_adventurer_name(),
            "level": 1,
            "max_level": 1,
            "is_playing": False,
            "owner_id": user_id,
            "current_scene": "level_1_start"
        }
        save_game_states(states)
    return states[user_id]

def reset_player_game(user_id):
    states = load_game_states()
    if user_id not in states:
        get_or_create_player(user_id)
        states = load_game_states()
    states[user_id]["level"] = 1
    states[user_id]["is_playing"] = True
    states[user_id]["current_scene"] = "level_1_start"
    save_game_states(states)
    return states[user_id]

def mark_level_complete(user_id, level):
    states = load_game_states()
    if user_id in states:
        if level > states[user_id].get("max_level", 1):
            states[user_id]["max_level"] = level
        if level == 10:
            states[user_id]["is_playing"] = False
        save_game_states(states)

def get_level_title(level):
    if level >= 9:
        return "👑 ဒဏ္ဍာရီ"
    elif level >= 7:
        return "🏆 သူရဲကောင်း"
    elif level >= 5:
        return "⚔️ စစ်သည်တော်"
    elif level >= 3:
        return "🌟 စွန့်စားသူ"
    else:
        return "🌱 အစပြုသူ"

def get_level_emoji(level):
    if level >= 9:
        return "👑"
    elif level >= 7:
        return "🏆"
    elif level >= 5:
        return "⚔️"
    elif level >= 3:
        return "🌟"
    else:
        return "🌱"

RANDOM_PREFIXES = [
    "သတ္တိရှင်", "ရဲစွမ်းသူ", "မှော်ဆရာ", "ဓားပြ", "စွန့်စားသူ",
    "ရွှေရှင်", "လမ်းပြ", "တောလိုက်", "မြားပစ်", "အိပ်မက်သူ",
]

RANDOM_SUFFIXES = [
    "မောင်", "ထွေး", "လွင်", "စိုး", "အောင်",
    "ထက်", "ခိုင်", "မြင့်", "ကျော်", "စံ",
]

def generate_adventurer_name():
    prefix = random.choice(RANDOM_PREFIXES)
    suffix = random.choice(RANDOM_SUFFIXES)
    return f"{prefix} {suffix}"

async def render_scene(target, context, scene_id, user_id, is_callback=False):
    scene = LEVEL_SCENES.get(scene_id)
    if not scene:
        if scene_id.endswith("_win"):
            level = int(scene_id.split("_")[1])
            mark_level_complete(user_id, level)
            state = get_player_state(user_id)
            player_name = state.get("name", "စွန့်စားသူ")
            max_level = state.get("max_level", 1)
            title = get_level_title(max_level)
            
            if level >= 10:
                final_text = f"🎉 *{player_name}* ဂိမ်းကိုအောင်မြင်ပြီ!\n\n👑 မင်းဟာ ဒဏ္ဍာရီဖြစ်သွားပြီ!\n\nပြန်စချင်ရင် /restartgame ကိုနှိပ်ပါ။"
                if is_callback:
                    await target.edit_message_text(final_text, parse_mode="Markdown")
                else:
                    await target.reply_text(final_text, parse_mode="Markdown")
                return
            else:
                next_level = level + 1
                final_text = f"🎉 *{player_name}* အဆင့် {level} ကိုအောင်မြင်ပြီ!\n\n👉 နောက်အဆင့်ကိုဆက်သွားမလား?"
                keyboard = [[InlineKeyboardButton("✅ ဆက်သွားမယ်", callback_data=f"level_{next_level}_start")]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                if is_callback:
                    await target.edit_message_text(final_text, parse_mode="Markdown", reply_markup=reply_markup)
                else:
                    await target.reply_text(final_text, parse_mode="Markdown", reply_markup=reply_markup)
                return
        
        msg = "❌ ဇာတ်လမ်းမှားယွင်းနေသည်။ /restartgame ကိုနှိပ်ပါ။"
        if is_callback:
            await target.edit_message_text(msg)
        else:
            await target.reply_text(msg)
        return
    
    state = get_player_state(user_id)
    if not state:
        msg = "❌ ဂိမ်းမစရသေးပါ။ /game ကိုနှိပ်ပါ။"
        if is_callback:
            await target.edit_message_text(msg)
        else:
            await target.reply_text(msg)
        return
    
    current_level = state.get("level", 1)
    max_level = state.get("max_level", 1)
    title = get_level_title(max_level)
    level_emoji = get_level_emoji(current_level)
    
    text = scene["text"]
    options = scene.get("options", {})
    
    header = f"━━━━━━━━━━━━━━━━\n"
    header += f"{level_emoji} အဆင့် {current_level}/10 | {title}\n"
    header += f"━━━━━━━━━━━━━━━━\n\n"
    
    if not options:
        if scene_id.endswith("_boss"):
            level = int(scene_id.split("_")[1])
            win_scene = f"level_{level}_win"
            states = load_game_states()
            states[user_id]["level"] = level + 1 if level < 10 else 10
            save_game_states(states)
            await render_scene(target, context, win_scene, user_id, is_callback)
            return
        
        final_text = f"{header}{text}\n\n✨ ပြန်စချင်ရင် /restartgame ကိုနှိပ်ပါ။"
        if is_callback:
            await target.edit_message_text(final_text, parse_mode="Markdown")
        else:
            await target.reply_text(final_text, parse_mode="Markdown")
        return
    
    keyboard = []
    for key, label in options.items():
        callback_data = f"game_{key}_{user_id}"
        keyboard.append([InlineKeyboardButton(label, callback_data=callback_data)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    full_text = f"{header}{text}"
    if is_callback:
        await target.edit_message_text(full_text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await target.reply_text(full_text, parse_mode="Markdown", reply_markup=reply_markup)

async def render_scene_with_send(context, chat_id, scene_id, user_id):
    scene = LEVEL_SCENES.get(scene_id)
    if not scene:
        await context.bot.send_message(chat_id=chat_id, text="❌ ဇာတ်လမ်းမှားယွင်းနေသည်။ /restartgame ကိုနှိပ်ပါ။")
        return
    
    state = get_player_state(user_id)
    if not state:
        await context.bot.send_message(chat_id=chat_id, text="❌ ဂိမ်းမစရသေးပါ။ /game ကိုနှိပ်ပါ။")
        return
    
    current_level = state.get("level", 1)
    max_level = state.get("max_level", 1)
    title = get_level_title(max_level)
    level_emoji = get_level_emoji(current_level)
    
    text = scene["text"]
    options = scene.get("options", {})
    
    header = f"━━━━━━━━━━━━━━━━\n"
    header += f"{level_emoji} အဆင့် {current_level}/10 | {title}\n"
    header += f"━━━━━━━━━━━━━━━━\n\n"
    
    if not options:
        if scene_id.endswith("_boss"):
            level = int(scene_id.split("_")[1])
            win_scene = f"level_{level}_win"
            states = load_game_states()
            states[user_id]["level"] = level + 1 if level < 10 else 10
            save_game_states(states)
            await render_scene_with_send(context, chat_id, win_scene, user_id)
            return
        
        final_text = f"{header}{text}\n\n✨ ပြန်စချင်ရင် /restartgame ကိုနှိပ်ပါ။"
        await context.bot.send_message(chat_id=chat_id, text=final_text, parse_mode="Markdown")
        return
    
    keyboard = []
    for key, label in options.items():
        callback_data = f"game_{key}_{user_id}"
        keyboard.append([InlineKeyboardButton(label, callback_data=callback_data)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    full_text = f"{header}{text}"
    await context.bot.send_message(chat_id=chat_id, text=full_text, parse_mode="Markdown", reply_markup=reply_markup)

async def game_start(update, context):
    user_id = str(update.effective_user.id)
    user_id_int, username = get_user_info(update)
    log_action(user_id_int, username, "GAME_START", "开始闯关游戏")
    
    state = get_player_state(user_id)
    
    if state and state.get("is_playing", False):
        keyboard = [
            [InlineKeyboardButton("✅ ဟုတ်ကဲ့၊ ပြန်စမည်", callback_data=f"restart_confirm_{user_id}")],
            [InlineKeyboardButton("❌ မဟုတ်ဘူး၊ ဆက်ကစားမယ်", callback_data=f"restart_cancel_{user_id}")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "⚠️ သတိပေးချက်\n\nမင်းမှာ ဂိမ်းတစ်ခုရှိနေပြီ။\nပြန်စမယ်ဆိုရင် အဟောင်းအကုန်ပျက်သွားမယ်။\n\nသေချာပြီလား?",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        return
    
    player = get_or_create_player(user_id)
    current_level = player.get("level", 1)
    max_level = player.get("max_level", 1)
    title = get_level_title(max_level)
    player_name = player.get("name", "စွန့်စားသူ")
    
    states = load_game_states()
    states[user_id]["is_playing"] = True
    states[user_id]["current_scene"] = f"level_{current_level}_start"
    save_game_states(states)
    
    level_data = LEVELS.get(current_level, LEVELS[1])
    level_emoji = get_level_emoji(current_level)
    
    await update.message.reply_text(
        f"🌟 {player_name} မင်္ဂလာပါ!\n\n"
        f"{level_emoji} အဆင့် {current_level}/10 | {title}\n"
        f"🏆 အမြင့်ဆုံး: {max_level}\n\n"
        f"🎯 *{level_data['name']}*\n"
        f"{level_data['desc']}",
        parse_mode="Markdown"
    )
    await render_scene(update.message, context, f"level_{current_level}_start", user_id)

async def game_restart(update, context):
    user_id = str(update.effective_user.id)
    user_id_int, username = get_user_info(update)
    log_action(user_id_int, username, "GAME_RESTART", "重新开始闯关游戏")
    
    reset_player_game(user_id)
    state = get_player_state(user_id)
    player_name = state.get("name", "စွန့်စားသူ")
    
    await update.message.reply_text(
        f"🔄 {player_name} ဂိမ်းကိုပြန်စပါပြီ။\n\n"
        "🌱 အဆင့် 1/10 | အစပြုသူ\n\n"
        f"🎯 *{LEVELS[1]['name']}*\n"
        f"{LEVELS[1]['desc']}",
        parse_mode="Markdown"
    )
    await render_scene(update.message, context, "level_1_start", user_id)

async def game_back(update, context):
    user_id = str(update.effective_user.id)
    state = get_player_state(user_id)
    
    if not state:
        await update.message.reply_text("❌ မင်းမှာ ဂိမ်းမရှိပါ။ /game နဲ့စပါ။")
        return
    
    if not state.get("is_playing", False):
        await update.message.reply_text("❌ ဂိမ်းပြီးသွားပြီ။ /restartgame နဲ့ပြန်စပါ။")
        return
    
    current_scene = state.get("current_scene", "level_1_start")
    if "_start" in current_scene:
        await update.message.reply_text("🔙 မင်းက ပထမဆုံးအဆင့်မှာရှိနေတယ်။ နောက်မပြန်နိုင်ဘူး။")
        return
    
    level = state.get("level", 1)
    start_scene = f"level_{level}_start"
    states = load_game_states()
    states[user_id]["current_scene"] = start_scene
    save_game_states(states)
    
    await update.message.reply_text("🔙 နောက်တစ်ဆင့်ကိုပြန်သွားပါပြီ။")
    await render_scene(update.message, context, start_scene, user_id)

async def game_callback(update, context):
    query = update.callback_query
    
    user_id = str(query.from_user.id)
    user_id_int, username = get_user_info_from_query(query)
    data = query.data
    chat_id = query.message.chat.id
    
    log_action(user_id_int, username, "CALLBACK", f"点击按钮: {data}")
    
    try:
        await query.delete_message()
    except Exception:
        pass
    
    try:
        await query.answer()
    except Exception:
        pass
    
    get_or_create_player(user_id)
    
    if data.startswith("restart_confirm_"):
        owner_id = data.replace("restart_confirm_", "")
        if not is_game_owner(user_id, owner_id):
            try:
                await query.answer("⛔️ ဒီဂိမ်းက မင်းရဲ့မဟုတ်ဘူး!", show_alert=True)
            except Exception:
                pass
            return
        
        reset_player_game(user_id)
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ ဂိမ်းကိုပြန်စပါပြီ။\n\n🌱 အဆင့် 1/10 | အစပြုသူ\n\n🎯 *{LEVELS[1]['name']}*\n{LEVELS[1]['desc']}",
            parse_mode="Markdown"
        )
        await render_scene_with_send(context, chat_id, "level_1_start", user_id)
        return
    
    if data.startswith("restart_cancel_"):
        owner_id = data.replace("restart_cancel_", "")
        if not is_game_owner(user_id, owner_id):
            try:
                await query.answer("⛔️ ဒီဂိမ်းက မင်းရဲ့မဟုတ်ဘူး!", show_alert=True)
            except Exception:
                pass
            return
        state = get_player_state(user_id)
        if state and state.get("is_playing", False):
            await context.bot.send_message(chat_id=chat_id, text="ℹ️ ဂိမ်းကိုဆက်ကစားပါ။")
            current_scene = state.get("current_scene", "level_1_start")
            await render_scene_with_send(context, chat_id, current_scene, user_id)
        else:
            await context.bot.send_message(chat_id=chat_id, text="❌ ဂိမ်းမရှိတော့ပါ။ /game နဲ့စပါ။")
        return
    
    if data.startswith("game_"):
        parts = data.rsplit("_", 1)
        if len(parts) != 2:
            return
        scene_key = parts[0].replace("game_", "")
        owner_id = parts[1]
        
        if not is_game_owner(user_id, owner_id):
            try:
                await query.answer("⛔️ ဒီဂိမ်းက မင်းရဲ့မဟုတ်ဘူး။\nကိုယ်ပိုင် /game နဲ့စပါ။", show_alert=True)
            except Exception:
                pass
            return
        
        state = get_player_state(user_id)
        if not state:
            await context.bot.send_message(chat_id=chat_id, text="❌ ဂိမ်းမစရသေးပါ။ /game ကိုနှိပ်ပါ။")
            return
        
        if not state.get("is_playing", False):
            await context.bot.send_message(chat_id=chat_id, text="❌ ဂိမ်းပြီးသွားပြီ။ /restartgame နဲ့ပြန်စပါ။")
            return
        
        if scene_key.startswith("level_") and scene_key.endswith("_start"):
            level = int(scene_key.split("_")[1])
            states = load_game_states()
            states[user_id]["level"] = level
            states[user_id]["current_scene"] = scene_key
            save_game_states(states)
        
        states = load_game_states()
        states[user_id]["current_scene"] = scene_key
        save_game_states(states)
        
        await render_scene_with_send(context, chat_id, scene_key, user_id)
        return
    
    if data.startswith("level_"):
        scene_key = data
        state = get_player_state(user_id)
        if not state:
            await context.bot.send_message(chat_id=chat_id, text="❌ ဂိမ်းမစရသေးပါ။ /game ကိုနှိပ်ပါ။")
            return
        
        if "_start" in scene_key:
            level = int(scene_key.split("_")[1])
            states = load_game_states()
            states[user_id]["level"] = level
            states[user_id]["current_scene"] = scene_key
            states[user_id]["is_playing"] = True
            save_game_states(states)
        
        await render_scene_with_send(context, chat_id, scene_key, user_id)
        return

# ============ check_schedule ============

async def check_schedule(app):
    while True:
        sched = load_schedule()
        now = time.time()
        for item in sched[:]:
            if item["time"] <= now:
                try:
                    await app.bot.send_message(chat_id=OWNER_ID, text=f"⏰ အချိန်မှန်ပို့နေသည်...\nစာသား: {item['text']}")
                    data = load_data()
                    targets = list(set(data["users"] + data["groups"]))
                    targets = [t for t in targets if t not in data.get("blacklist", [])]
                    for t in targets:
                        try:
                            await app.bot.send_message(chat_id=t, text=f"📢 {item['text']}", parse_mode=None)
                            await asyncio.sleep(0.1)
                        except:
                            pass
                except Exception as e:
                    await app.bot.send_message(chat_id=OWNER_ID, text=f"❌ အချိန်မှန်ပို့ရာတွင် အမှားရှိသည်: {e}")
                sched.remove(item)
                save_schedule(sched)
        await asyncio.sleep(10)

# ============ main ============
async def main():
    print("📌 Entering main()...")
    app = Application.builder().token(TOKEN).build()
    
    try:
        await app.bot.delete_webhook(drop_pending_updates=True)
        print("📌 Webhook cleared...")
    except Exception as e:
        print(f"⚠️ Webhook clear warning: {e}")
    
    print("📌 Application built successfully...")
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("count", count))
    app.add_handler(CommandHandler("send", send))
    app.add_handler(CommandHandler("broadcast", broadcast))
    app.add_handler(CommandHandler("broadcast_image", broadcast_image))
    app.add_handler(CommandHandler("broadcast_group", broadcast_group))
    app.add_handler(CommandHandler("broadcast_user", broadcast_user))
    app.add_handler(CommandHandler("at", at))
    app.add_handler(CommandHandler("in", in_))
    app.add_handler(CommandHandler("list_schedule", list_schedule))
    app.add_handler(CommandHandler("cancel_schedule", cancel_schedule))
    app.add_handler(CommandHandler("preset", preset))
    app.add_handler(CommandHandler("blacklist", blacklist))
    app.add_handler(CommandHandler("cancel", cancel))
    app.add_handler(CommandHandler("forward", forward))
    app.add_handler(CommandHandler("forward_all", forward_all))
    app.add_handler(CommandHandler("game", game_start))
    app.add_handler(CommandHandler("restartgame", game_restart))
    app.add_handler(CommandHandler("back", game_back))
    app.add_handler(CallbackQueryHandler(random_link_callback, pattern="^random_link$"))
    app.add_handler(CallbackQueryHandler(back_to_menu_callback, pattern="^back_to_menu$"))
    app.add_handler(CallbackQueryHandler(game_callback, pattern="^game_"))
    app.add_handler(CallbackQueryHandler(game_callback, pattern="^restart_"))
    app.add_handler(CallbackQueryHandler(game_callback, pattern="^level_"))
    
    print("📌 All handlers added...")
    
    # ✅ 创建后台任务
    schedule_task = asyncio.create_task(check_schedule(app))
    
    print("🤖 Advanced Bot started.")
    print("📊 Loaded commands. Owner-only functions active.")
    
    try:
        await app.run_polling()
    except KeyboardInterrupt:
        print("🛑 Bot stopped by user")
    finally:
        # ✅ 取消后台任务
        schedule_task.cancel()
        try:
            await schedule_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    print("🔵 Script started...")
    asyncio.run(main())