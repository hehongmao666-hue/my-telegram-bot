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

# ============ 管理员配置 ============
# 在这里添加允许使用 /announce 的管理员 ID
ADMIN_IDS = [
    5300063761,  # Owner
    1062259560,  # Admin 1
]

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
            data = json.load(f)
            # ✅ 确保 subscribers 字段存在
            if "subscribers" not in data:
                data["subscribers"] = []
            return data
    return {"users": [], "groups": [], "blacklist": [], "subscribers": []}

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

# ============ @所有人 公告功能 ============

async def announce(update, context):
    """在群里 @所有人 发送公告（仅 Owner 和指定管理员）"""
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    # 检查是否有权限
    if user_id not in ADMIN_IDS:
        await update.message.reply_text("⛔️ သင့်တွင် ဤ command ကိုသုံးခွင့်မရှိပါ။")
        return
    
    # 检查是否在群组中使用
    if update.effective_chat.type == "private":
        await update.message.reply_text("❌ ဤ command ကို အုပ်စုများတွင်သာ သုံးနိုင်သည်။")
        return
    
    # 获取公告内容
    text = ' '.join(context.args)
    if not text:
        await update.message.reply_text(
            "📝 *အသုံးပြုပုံ:* `/announce [စာသား]`\n\n"
            "ဥပမာ: `/announce ဒီနေ့ အထူးလျှော့စျေး 30%!`",
            parse_mode="Markdown"
        )
        return
    
    try:
        chat = await context.bot.get_chat(chat_id)
        chat_title = chat.title or "အုပ်စု"
    except Exception:
        chat_title = "အုပ်စု"
    
    try:
        bot_member = await context.bot.get_chat_member(chat_id, context.bot.id)
        can_mention = bot_member.status in ["administrator", "creator"]
    except Exception:
        can_mention = False
    
    # ✅ 使用 Telegram 原生 @所有人 格式
    mention_text = ""
    if can_mention:
        mention_text = '<a href="tg://mention?user=all">@all</a>\n\n'
    
    # ✅ 全部使用缅文
    announcement = f"📢 *ကြေငြာ*\n"
    announcement += f"━━━━━━━━━━━━━━━━\n\n"
    if mention_text:
        announcement += mention_text
    announcement += f"{text}\n\n"
    announcement += f"━━━━━━━━━━━━━━━━\n"
    announcement += f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    announcement += f"👤 {update.effective_user.first_name or 'Admin'}"
    
    keyboard = [
        [InlineKeyboardButton("🔔 သတင်းရယူမည်", callback_data=f"announce_subscribe_{chat_id}_{int(time.time())}")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=announcement,
            parse_mode="HTML",
            reply_markup=reply_markup
        )
        
        if not can_mention:
            await update.message.reply_text(
                "ℹ️ Bot သည် အုပ်စုတွင် အက်ဒမင်မဟုတ်သောကြောင့် @all ကို မသုံးနိုင်ပါ။\n"
                "ကျေးဇူးပြု၍ Bot ကို အက်ဒမင်အဖြစ်သတ်မှတ်ပါ။"
            )
        
        user_id_int, username = get_user_info(update)
        log_action(user_id_int, username, "ANNOUNCE", f"公告: {text[:50]}... | 群组: {chat_title}")
        
    except Exception as e:
        await update.message.reply_text(f"❌ ပို့ရာတွင် အမှားရှိသည်: {e}")

async def announce_callback(update, context):
    """公告按钮回调 - 支持多人点击，不删除原公告"""
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("announce_subscribe_"):
        user = query.from_user
        chat_id = query.message.chat.id
        
        # 获取当前订阅人数
        data = load_data()
        subscribers = data.get("subscribers", [])
        if user.id not in subscribers:
            subscribers.append(user.id)
            data["subscribers"] = subscribers
            save_data(data)
        
        # ✅ 只在原公告下方发送一条通知（不修改原公告）
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🔔 {user.mention_html()} သည် အသိပေးချက်ကို လက်ခံထားပြီး။ (စုစုပေါင်း {len(subscribers)} ယောက်)",
            parse_mode="HTML"
        )
        
        # ✅ 只提示用户，不修改按钮
        await query.answer(f"✅ {user.first_name} အတွက် အောင်မြင်ပါပြီ။", show_alert=False)

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

# ============ 消息管理 ============

def save_game_message(user_id, chat_id, message_id):
    """保存游戏消息ID"""
    states = load_game_states()
    if user_id not in states:
        return
    if "game_messages" not in states[user_id]:
        states[user_id]["game_messages"] = []
    # 只保留最近50条，防止内存溢出
    if len(states[user_id]["game_messages"]) >= 50:
        states[user_id]["game_messages"] = states[user_id]["game_messages"][-40:]
    if message_id not in states[user_id]["game_messages"]:
        states[user_id]["game_messages"].append(message_id)
    save_game_states(states)

async def clear_game_messages(context, user_id, chat_id, keep_last=0):
    """清除游戏消息"""
    states = load_game_states()
    if user_id not in states:
        return
    messages = states[user_id].get("game_messages", [])
    if not messages:
        return
    
    # 保留最后几条（如果有指定）
    if keep_last > 0 and len(messages) > keep_last:
        messages = messages[:-keep_last]
    
    deleted = 0
    for msg_id in messages:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
            deleted += 1
        except Exception:
            pass
    
    # 清空已删除的消息记录
    states[user_id]["game_messages"] = []
    save_game_states(states)
    return deleted

# ============ RPG 游戏配置（地狱级难度） ============

MAX_HP = 80
MAX_ENERGY = 40

# 地狱级敌人模板（强度大幅提升）
ENEMY_TEMPLATES = [
    {"name": "🐺 ဝံပုလွေသိုက်", "hp": 50, "attack": 15, "defense": 3, "reward": 15, "exp": 8},
    {"name": "🐻 ဝက်ဝံဧရာမ", "hp": 80, "attack": 20, "defense": 5, "reward": 25, "exp": 15},
    {"name": "🐉 နဂါးရိုင်း", "hp": 120, "attack": 30, "defense": 8, "reward": 45, "exp": 25},
    {"name": "🧙 မှော်ဆရာမည်း", "hp": 70, "attack": 35, "defense": 2, "reward": 35, "exp": 20},
    {"name": "⚔️ သူရဲကောင်းကျဆုံး", "hp": 100, "attack": 25, "defense": 12, "reward": 50, "exp": 28},
    {"name": "👹 နတ်ဆိုးမင်း", "hp": 150, "attack": 40, "defense": 10, "reward": 70, "exp": 35},
    {"name": "🐍 မြွေဘုရင်", "hp": 90, "attack": 30, "defense": 6, "reward": 40, "exp": 22},
    {"name": "🦅 လင်းယုန်မင်းကြီး", "hp": 110, "attack": 35, "defense": 8, "reward": 55, "exp": 30},
    {"name": "👑 မှောင်မိုက်မင်းကြီး", "hp": 200, "attack": 50, "defense": 15, "reward": 100, "exp": 50},
    {"name": "🐲 နဂါးမင်းကြီး", "hp": 300, "attack": 60, "defense": 20, "reward": 150, "exp": 70},
]

# 地狱级装备（价格更贵，效果稍好）
WEAPON_TEMPLATES = [
    {"name": "🗡️ သံဓားမ", "attack": 4, "price": 30},
    {"name": "⚔️ ငွေဓားမ", "attack": 8, "price": 60},
    {"name": "🗡️ ရွှေဓားမ", "attack": 13, "price": 120},
    {"name": "⚔️ မှော်ဓားမ", "attack": 20, "price": 200},
    {"name": "⚔️ ဒဏ္ဍာရီဓားမ", "attack": 32, "price": 400},
]

ARMOR_TEMPLATES = [
    {"name": "🛡️ သားရေဒိုင်း", "defense": 4, "price": 30},
    {"name": "🛡️ သံဒိုင်း", "defense": 8, "price": 60},
    {"name": "🛡️ ငွေဒိုင်း", "defense": 13, "price": 120},
    {"name": "🛡️ မှော်ဒိုင်း", "defense": 20, "price": 200},
    {"name": "🛡️ ဒဏ္ဍာရီဒိုင်း", "defense": 32, "price": 400},
]

POTION_TEMPLATES = [
    {"name": "🧪 သေးငယ်သောဆေး", "heal": 15, "price": 10},
    {"name": "🧪 ပုံမှန်ဆေး", "heal": 30, "price": 25},
    {"name": "🧪 ကြီးမားသောဆေး", "heal": 50, "price": 50},
    {"name": "🧪 အသက်ဆေး", "heal": 80, "price": 80},
]

# 成就系统（需要更高等级）
ACHIEVEMENTS = {
    5: "🌱 ရှင်သန်သူ",
    10: "🌟 ခရီးသည်",
    20: "⚔️ စစ်သည်တော်",
    30: "🔥 သူရဲကောင်း",
    40: "⭐ ဒဏ္ဍာရီ",
    50: "👑 မင်းသား",
    60: "🏆 ချန်ပီယံ",
    70: "💀 သေခြင်းကိုအောင်သူ",
    80: "👑 ဘုရင်မင်းမြတ်",
    90: "🌟 အဆုံးစွန်ဘုရင်",
}

def generate_enemy(level):
    """地狱级敌人生成 - 区分普通/精英/Boss"""
    is_boss = level % 10 == 0
    is_elite = level % 5 == 0 and not is_boss
    
    # 根据类型选择不同模板
    if is_boss:
        base = random.choice([e for e in ENEMY_TEMPLATES if "နဂါး" in e["name"] or "မင်း" in e["name"] or "ဘုရင်" in e["name"]])
        multiplier = 1 + (level - 1) * 0.8
    elif is_elite:
        base = random.choice([e for e in ENEMY_TEMPLATES if "ဧရာမ" in e["name"] or "ဘုရင်" in e["name"]])
        multiplier = 1 + (level - 1) * 0.6
    else:
        base = random.choice(ENEMY_TEMPLATES)
        multiplier = 1 + (level - 1) * 0.5
    
    return {
        "name": base["name"],
        "hp": int(base["hp"] * multiplier),
        "max_hp": int(base["hp"] * multiplier),
        "attack": int(base["attack"] * multiplier),
        "defense": int(base["defense"] * multiplier),
        "reward": int(base["reward"] * multiplier * (3 if is_boss else 1.5 if is_elite else 1)),
        "exp": int(base["exp"] * multiplier * (3 if is_boss else 1.5 if is_elite else 1)),
        "level": level,
        "is_boss": is_boss,
        "is_elite": is_elite
    }

def generate_shop_items(level):
    items = []
    for w in WEAPON_TEMPLATES:
        if level >= 4 or w["price"] <= 60:
            items.append({"type": "weapon", **w})
    for a in ARMOR_TEMPLATES:
        if level >= 4 or a["price"] <= 60:
            items.append({"type": "armor", **a})
    for p in POTION_TEMPLATES:
        items.append({"type": "potion", **p})
    return items

# ============ 90关地狱级关卡 ============

LEVELS = {}
LEVEL_NAMES = [
    # 第1-10关：新手试炼
    "🌲 မြူခိုးတော", "🏔️ နှင်းတောင်", "🏜️ သဲကန္တာရမြို့",
    "🌋 မီးတောင်ချိုင့်", "🌊 ရေအောက်နန်းတော်", "🏰 မှောင်မိုက်ရဲတိုက်",
    "🌌 ကြယ်မျှော်စင်", "🐉 နဂါးဂူ", "🌑 ကွက်လပ်နယ်မြေ", "👑 နောက်ဆုံးပလ္လင်",
    # 第11-20关：勇者之路
    "🌿 ဧရာဝင်တော", "❄️ ရေခဲဂူ", "🔥 မီးလျှံတောင်တန်း", "🌊 ပင်လယ်ပျော်ကျွန်း",
    "🏚️ မြေပြိုမြို့", "🌪️ လေဝဲချိုင့်", "💎 ကျောက်မျက်တွင်း", "🌙 လပြည့်အိုင်",
    "☀️ နေဝင်မြို့", "🌌 နဂါးငွေ့တန်း",
    # 第21-30关：英雄试炼
    "🕯️ မီးရှူးတန်ဆောင်", "⚡ လျှပ်စစ်တောင်", "🌿 ဝါးတောအုပ်", "🏔️ ငွေတောင်",
    "🌊 ငါးမန်းပင်လယ်", "🏰 သဲရဲတိုက်", "🌋 မီးခိုးတောင်", "🌌 ကြယ်ပွင့်တော",
    "👑 ရွှေပလ္လင်", "🌟 နောက်ဆုံးကြယ်",
    # 第31-40关：地狱之门
    "🔥 မီးငရဲတံခါး", "💀 သေမင်းချိုင့်", "🦇 လင်းနို့ဂူ", "🌊 သွေးမြစ်",
    "🏚️ ပျက်စီးသောမြို့", "⚰️ သင်္ချိုင်းတော", "🕷️ ပင့်ကူတော", "🌑 မှောင်မိုက်နယ်မြေ",
    "👹 နတ်ဆိုးတောင်", "💀 သေမင်းနန်းတော်",
    # 第41-50关：传奇之路
    "⚔️ သူရဲကောင်းလမ်း", "🛡️ ဒိုင်းတောင်", "🗡️ ဓားချိုင့်", "🏹 မြားတော",
    "🧙 မှော်ဆရာတောင်", "🐲 နဂါးတောင်တန်း", "👑 မင်းသားလမ်း", "⭐ ကြယ်တောင်တန်း",
    "🌌 နဂါးငွေ့တန်းလမ်း", "🏆 ချန်ပီယံတော",
    # 第51-60关：暗影领域
    "🌑 အမှောင်နယ်မြေ", "🕯️ မီးစုန်းတော", "🧛 သွေးစုပ်ဖုတ်ကောင်", "🌊 မှောင်မိုက်ပင်လယ်",
    "🏚️ ပျက်စီးသောအိမ်", "⚡ လျှပ်စစ်မုန်တိုင်း", "🌪️ လေဆူးတော", "🔥 မီးမုန်တိုင်း",
    "❄️ ရေခဲမုန်တိုင်း", "🌋 မီးတောင်ပေါက်ကွဲ",
    # 第61-70关：众神领域
    "⚡ လျှပ်စစ်နတ်ဘုရား", "🔥 မီးနတ်ဘုရား", "🌊 ရေနတ်ဘုရား", "🌪️ လေနတ်ဘုရား",
    "🌍 မြေနတ်ဘုရား", "🌙 လနတ်ဘုရား", "☀️ နေနတ်ဘုရား", "⭐ ကြယ်နတ်ဘုရား",
    "🌌 စကြဝဠာနတ်ဘုရား", "👑 ဘုရင်မင်းမြတ်",
    # 第71-80关：混沌深渊
    "🌀 ဖရိုဖရဲတွင်း", "💀 သေခြင်းတွင်း", "👹 နတ်ဆိုးတွင်း", "🐲 နဂါးတွင်း",
    "🦇 လင်းနို့တွင်း", "🕷️ ပင့်ကူတွင်း", "🌑 မှောင်မိုက်တွင်း", "🔥 မီးတွင်း",
    "❄️ ရေခဲတွင်း", "🌊 ရေတွင်း",
    # 第81-90关：最终决战
    "⚔️ နောက်ဆုံးတိုက်ပွဲ", "👑 နောက်ဆုံးဘုရင်", "🐲 နဂါးဘုရင်", "👹 နတ်ဆိုးဘုရင်",
    "💀 သေမင်းဘုရင်", "🌑 အမှောင်ဘုရင်", "🔥 မီးဘုရင်", "🌊 ရေဘုရင်",
    "⭐ ကြယ်ဘုရင်", "🌟 အဆုံးစွန်ဘုရင်"
]

LEVEL_DESCS = [
    # 第1-10关
    "မြူခိုးတောအုပ်ထဲမှာ လမ်းပျောက်နေတယ်။", "နှင်းတောင်ထိပ်ကိုတက်ပြီး အလံကိုစိုက်ပါ။",
    "သဲကန္တာရထဲမှာ ပျောက်ဆုံးနေတဲ့မြို့ကိုရှာပါ။", "မီးတောင်ထဲက မီးအိမ်သားကိုအနိုင်ယူပါ။",
    "ရေအောက်နန်းတော်ထဲက သုံးခွသွားကိုရှာပါ။", "မှောင်မိုက်ရဲတိုက်ထဲက သူရဲကောင်းကိုအနိုင်ယူပါ။",
    "ကြယ်မျှော်စင်ထဲက ကြယ်ပဟေဠိကိုဖြေပါ။", "နဂါးဂူထဲက နဂါးငယ်ကိုအနိုင်ယူပါ။",
    "ကွက်လပ်နယ်မြေထဲက နှလုံးသားကိုရှာပါ။", "မှောင်မိုက်ဘုရင်ကိုအနိုင်ယူပြီး ငြိမ်းချမ်းရေးကိုပြန်လည်ရယူပါ။",
    # 第11-20关
    "ဧရာဝင်တောအုပ်ထဲမှာ ရှေးဟောင်းဘုရားကိုရှာပါ။", "ရေခဲဂူထဲမှာ ရေခဲပန်းကိုရှာပါ။",
    "မီးလျှံတောင်တန်းကိုဖြတ်ပါ။", "ပင်လယ်ပျော်ကျွန်းပေါ်မှာ ရတနာကိုရှာပါ။",
    "မြေပြိုမြို့ထဲက ရှေးဟောင်းပစ္စည်းကိုရှာပါ။", "လေဝဲချိုင့်ထဲမှာ လေနတ်သားကိုအနိုင်ယူပါ။",
    "ကျောက်မျက်တွင်းထဲမှာ စိန်ကိုရှာပါ။", "လပြည့်အိုင်ထဲမှာ လရောင်ပုလဲကိုရှာပါ။",
    "နေဝင်မြို့ထဲမှာ နေရောင်ခြည်ကိုရှာပါ။", "နဂါးငွေ့တန်းပေါ်မှာ ကြယ်တွေကိုရေတွက်ပါ။",
    # 第21-30关
    "မီးရှူးတန်ဆောင်ထဲမှာ မီးအိမ်ကိုရှာပါ။", "လျှပ်စစ်တောင်ပေါ်မှာ လျှပ်စီးကိုရှာပါ။",
    "ဝါးတောအုပ်ထဲမှာ ဝါးမျှင်ကိုရှာပါ။", "ငွေတောင်ထိပ်မှာ ငွေသတ္တုကိုရှာပါ။",
    "ငါးမန်းပင်လယ်ထဲမှာ သင်္ဘောပျက်ကိုရှာပါ။", "သဲရဲတိုက်ထဲမှာ သဲဘုရင်ကိုအနိုင်ယူပါ။",
    "မီးခိုးတောင်ထဲမှာ မီးခိုးနတ်ကိုအနိုင်ယူပါ။", "ကြယ်ပွင့်တောထဲမှာ ကြယ်ပွင့်ကိုရှာပါ။",
    "ရွှေပလ္လင်ပေါ်မှာ ရွှေသရဖူကိုရှာပါ။", "နောက်ဆုံးကြယ်ပေါ်မှာ စွမ်းအားကိုရှာပြီး ဂိမ်းကိုအနိုင်ရပါ။",
    # 第31-40关
    "မီးငရဲတံခါးကိုဖွင့်ပါ။", "သေမင်းချိုင့်ကိုဖြတ်ပါ။", "လင်းနို့ဂူထဲက လင်းနို့ဘုရင်ကိုအနိုင်ယူပါ။",
    "သွေးမြစ်ကိုဖြတ်ပါ။", "ပျက်စီးသောမြို့ထဲက ရတနာကိုရှာပါ။", "သင်္ချိုင်းတောထဲက သရဲဘုရင်ကိုအနိုင်ယူပါ။",
    "ပင့်ကူတောထဲက ပင့်ကူဘုရင်ကိုအနိုင်ယူပါ။", "မှောင်မိုက်နယ်မြေကိုဖြတ်ပါ။",
    "နတ်ဆိုးတောင်ပေါ်ကို တက်ပါ။", "သေမင်းနန်းတော်ထဲက သေမင်းကိုအနိုင်ယူပါ။",
    # 第41-50关
    "သူရဲကောင်းလမ်းကိုလျှောက်ပါ။", "ဒိုင်းတောင်ပေါ်ကိုတက်ပါ။",
    "ဓားချိုင့်ထဲက ဓားကိုရှာပါ။", "မြားတောထဲက မြားကိုရှာပါ။",
    "မှော်ဆရာတောင်ပေါ်ကိုတက်ပါ။", "နဂါးတောင်တန်းကိုဖြတ်ပါ။",
    "မင်းသားလမ်းကိုလျှောက်ပါ။", "ကြယ်တောင်တန်းကိုဖြတ်ပါ။",
    "နဂါးငွေ့တန်းလမ်းကိုလျှောက်ပါ။", "ချန်ပီယံတောထဲက ချန်ပီယံကိုအနိုင်ယူပါ။",
    # 第51-60关
    "အမှောင်နယ်မြေကိုဖြတ်ပါ။", "မီးစုန်းတောထဲက မီးစုန်းကိုအနိုင်ယူပါ။",
    "သွေးစုပ်ဖုတ်ကောင်ဂူထဲက သွေးစုပ်ဖုတ်ကောင်ကိုအနိုင်ယူပါ။", "မှောင်မိုက်ပင်လယ်ကိုဖြတ်ပါ။",
    "ပျက်စီးသောအိမ်ထဲက ရတနာကိုရှာပါ။", "လျှပ်စစ်မုန်တိုင်းကိုဖြတ်ပါ။",
    "လေဆူးတောထဲက လေနတ်ကိုအနိုင်ယူပါ။", "မီးမုန်တိုင်းကိုဖြတ်ပါ။",
    "ရေခဲမုန်တိုင်းကိုဖြတ်ပါ။", "မီးတောင်ပေါက်ကွဲကိုရှောင်ပါ။",
    # 第61-70关
    "လျှပ်စစ်နတ်ဘုရားကိုအနိုင်ယူပါ။", "မီးနတ်ဘုရားကိုအနိုင်ယူပါ။",
    "ရေနတ်ဘုရားကိုအနိုင်ယူပါ။", "လေနတ်ဘုရားကိုအနိုင်ယူပါ။",
    "မြေနတ်ဘုရားကိုအနိုင်ယူပါ။", "လနတ်ဘုရားကိုအနိုင်ယူါ။",
    "နေနတ်ဘုရားကိုအနိုင်ယူပါ။", "ကြယ်နတ်ဘုရားကိုအနိုင်ယူပါ။",
    "စကြဝဠာနတ်ဘုရားကိုအနိုင်ယူပါ။", "ဘုရင်မင်းမြတ်ကိုအနိုင်ယူပါ။",
    # 第71-80关
    "ဖရိုဖရဲတွင်းထဲက ရှာပါ။", "သေခြင်းတွင်းထဲက ရှာပါ။",
    "နတ်ဆိုးတွင်းထဲက ရှာပါ။", "နဂါးတွင်းထဲက ရှာပါ။",
    "လင်းနို့တွင်းထဲက ရှာပါ။", "ပင့်ကူတွင်းထဲက ရှာပါ။",
    "မှောင်မိုက်တွင်းထဲက ရှာပါ။", "မီးတွင်းထဲက ရှာပါ။",
    "ရေခဲတွင်းထဲက ရှာပါ။", "ရေတွင်းထဲက ရှာပါ။",
    # 第81-90关
    "နောက်ဆုံးတိုက်ပွဲကိုရင်ဆိုင်ပါ။", "နောက်ဆုံးဘုရင်ကိုအနိုင်ယူပါ။",
    "နဂါးဘုရင်ကိုအနိုင်ယူပါ။", "နတ်ဆိုးဘုရင်ကိုအနိုင်ယူပါ။",
    "သေမင်းဘုရင်ကိုအနိုင်ယူပါ။", "အမှောင်ဘုရင်ကိုအနိုင်ယူပါ။",
    "မီးဘုရင်ကိုအနိုင်ယူပါ။", "ရေဘုရင်ကိုအနိုင်ယူပါ။",
    "ကြယ်ဘုရင်ကိုအနိုင်ယူပါ။", "အဆုံးစွန်ဘုရင်ကိုအနိုင်ယူပြီး ဂိမ်းကိုအနိုင်ရပါ။"
]

for i in range(1, 91):
    LEVELS[i] = {
        "name": LEVEL_NAMES[i-1],
        "desc": LEVEL_DESCS[i-1],
        "is_boss": i % 10 == 0,  # 每10关Boss
        "is_elite": i % 5 == 0 and i % 10 != 0  # 每5关精英（非Boss）
    }

LEVEL_SCENES = {}

# 随机事件池
RANDOM_EVENTS = [
    "🌟 လမ်းမှာ ရွှေဒင်္ဂါးတစ်လုံးတွေ့တယ်။ +5 ရွှေ",
    "🌿 ပျားရည်အိုးတစ်လုံးတွေ့တယ်။ +10 HP",
    "🍄 မှော်မှိုတစ်ခုတွေ့တယ်။ +5 အတွေ့အကြုံ",
    "🪶 ထူးဆန်းတဲ့ငှက်မွေးတစ်ခုတွေ့တယ်။ +10 ရွှေ",
    "💎 ကျောက်မျက်တစ်လုံးတွေ့တယ်။ +20 ရွှေ",
    "⚔️ သံဓားတစ်ချောင်းတွေ့တယ်။ (အချိန်ခဏတာ +3 တိုက်ခိုက်အား)",
    "🛡️ သားရေဒိုင်းတစ်ခုတွေ့တယ်။ (အချိန်ခဏတာ +3 ကာကွယ်အား)",
]

# 精英事件池
ELITE_EVENTS = [
    "⚔️ ဧရာမဝံပုလွေကိုတွေ့တယ်! အထူးသတိထားပါ!",
    "🔥 မီးလူးသတ္တဝါကိုတွေ့တယ်!",
    "🌪️ လေနတ်သားကိုတွေ့တယ်!",
    "💀 သရဲတစ်ကောင်ကိုတွေ့တယ်!",
]

# 生成90关场景
for level in range(1, 91):
    is_boss = LEVELS[level].get("is_boss", False)
    is_elite = LEVELS[level].get("is_elite", False)
    
    # 起点场景
    start_text = f"📍 *{LEVELS[level]['name']}*\n\n{LEVELS[level]['desc']}\n\n"
    if is_boss:
        start_text += "👑 *BOSS အဆင့်!* အထူးသတိထားပါ!\n\n"
    elif is_elite:
        start_text += "⚔️ *Elite အဆင့်!* အားကောင်းတဲ့ရန်သူကိုရင်ဆိုင်ရမယ်!\n\n"
    start_text += "လမ်းကြောင်းသုံးခုကွဲနေတယ်။ ဘယ်ကိုသွားမလဲ?"
    
    LEVEL_SCENES[f"level_{level}_start"] = {
        "text": start_text,
        "options": {
            f"level_{level}_path1": "🌿 လမ်းကြောင်း ၁",
            f"level_{level}_path2": "🌲 လမ်းကြောင်း ၂",
            f"level_{level}_path3": "🏔️ လမ်းကြောင်း ၃"
        }
    }
    
    # 3条随机路径
    for i in range(1, 4):
        event = random.choice(RANDOM_EVENTS)
        path_text = f"🌿 လမ်းကြောင်း {i} ပေါ်မှာ...\n\n{event}\n\nဆက်သွားမလား?"
        
        # 随机决定是否遇到精英/Boss
        next_scene = f"level_{level}_boss" if is_boss else f"level_{level}_elite" if is_elite else f"level_{level}_fight"
        
        LEVEL_SCENES[f"level_{level}_path{i}"] = {
            "text": path_text,
            "options": {
                next_scene: "⚔️ ရှေ့ဆက်မယ်",
                f"level_{level}_start": "🔙 ပြန်သွားမယ်"
            }
        }
    
    # 普通战斗场景
    if not is_boss and not is_elite:
        LEVEL_SCENES[f"level_{level}_fight"] = {
            "text": f"⚔️ *တိုက်ပွဲအတွက်ပြင်ဆင်ပါ!*\n\n{LEVELS[level]['name']} မှာ ရန်သူတွေကိုရင်ဆိုင်ရမယ်။\n\nအနိုင်ရဖို့ အကောင်းဆုံးဗျူဟာကိုရွေးချယ်ပါ!",
            "options": {
                f"level_{level}_win": "⚔️ တိုက်မယ်",
                f"level_{level}_start": "🔙 ပြန်သွားမယ်"
            }
        }
    
    # 精英战斗场景
    if is_elite:
        elite_event = random.choice(ELITE_EVENTS)
        LEVEL_SCENES[f"level_{level}_elite"] = {
            "text": f"⚔️ *Elite တိုက်ပွဲ!*\n\n{elite_event}\n\nဒီရန်သူက သာမန်ရန်သူတွေထက် ပိုအားကောင်းတယ်!\n\nအနိုင်ရဖို့ အစွမ်းကုန်ကြိုးစားပါ!",
            "options": {
                f"level_{level}_win": "⚔️ တိုက်မယ်",
                f"level_{level}_start": "🔙 ပြန်သွားမယ်"
            }
        }
    
    # Boss战斗场景
    if is_boss:
        boss_name = LEVELS[level]["name"]
        LEVEL_SCENES[f"level_{level}_boss"] = {
            "text": f"👑 *BOSS တိုက်ပွဲ!*\n\n{boss_name} ကိုရင်ဆိုင်ရမယ်!\n\nဒီရန်သူက အလွန်အားကောင်းတယ်။\n\nအနိုင်ရဖို့ အကောင်းဆုံးကြိုးစားပါ!",
            "options": {
                f"level_{level}_win": "⚔️ တိုက်မယ်",
                f"level_{level}_start": "🔙 ပြန်သွားမယ်"
            }
        }
    
    # 通关场景
    LEVEL_SCENES[f"level_{level}_win"] = {
        "text": f"🎉 *{LEVELS[level]['name']} ကိုအောင်မြင်ပြီ!*\n\n",
        "options": {
            f"level_{level+1}_start": f"➡️ နောက်အဆင့် ({level+1}) ကိုသွားမယ်" if level < 90 else "🏆 ဂိမ်းအောင်မြင်ပြီ!"
        } if level < 90 else {}
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
            "current_scene": "level_1_start",
            "hp": MAX_HP,
            "max_hp": MAX_HP,
            "energy": MAX_ENERGY,
            "max_energy": MAX_ENERGY,
            "gold": 5,  # 从20降到5
            "attack": 2,  # 从3降到2
            "defense": 1,
            "exp": 0,
            "exp_to_next": 20,  # 从10升到20
            "weapon": None,
            "armor": None,
            "potions": [],
            "achievements": [],
            "deaths": 0  # 记录死亡次数
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
    states[user_id]["hp"] = states[user_id].get("max_hp", MAX_HP)
    states[user_id]["energy"] = states[user_id].get("max_energy", MAX_ENERGY)
    # 死亡惩罚：重置金币减半
    gold = states[user_id].get("gold", 5)
    states[user_id]["gold"] = max(5, gold // 2)
    states[user_id]["potions"] = []
    # 记录死亡次数
    states[user_id]["deaths"] = states[user_id].get("deaths", 0) + 1
    save_game_states(states)
    return states[user_id]

def add_exp(user_id, exp):
    states = load_game_states()
    if user_id not in states:
        return
    states[user_id]["exp"] += exp
    exp_to_next = states[user_id].get("exp_to_next", 20)
    level = states[user_id].get("level", 1)
    while states[user_id]["exp"] >= exp_to_next:
        states[user_id]["exp"] -= exp_to_next
        states[user_id]["level"] += 1
        level = states[user_id]["level"]
        # 地狱级升级所需经验增长更快
        states[user_id]["exp_to_next"] = int(exp_to_next * 1.8)
        # 升级奖励降低（地狱模式）
        states[user_id]["max_hp"] += 8  # 从10降到8
        states[user_id]["hp"] = min(states[user_id]["hp"] + 8, states[user_id]["max_hp"])
        states[user_id]["attack"] += 1  # 从2降到1
        states[user_id]["defense"] += 1
        for achieve_level, title in ACHIEVEMENTS.items():
            if level >= achieve_level and title not in states[user_id].get("achievements", []):
                states[user_id]["achievements"].append(title)
        exp_to_next = states[user_id]["exp_to_next"]
    save_game_states(states)

def mark_level_complete(user_id, level):
    states = load_game_states()
    if user_id in states:
        if level > states[user_id].get("max_level", 1):
            states[user_id]["max_level"] = level
        if level == 30:
            states[user_id]["is_playing"] = False
        # 地狱级：过关只回复30%血量
        max_hp = states[user_id].get("max_hp", MAX_HP)
        current_hp = states[user_id].get("hp", max_hp)
        states[user_id]["hp"] = min(max_hp, current_hp + int(max_hp * 0.3))
        save_game_states(states)

def get_level_title(level):
    if level >= 85:
        return "🌟 အဆုံးစွန်ဘုရင်"
    elif level >= 75:
        return "👑 ဘုရင်မင်းမြတ်"
    elif level >= 65:
        return "⭐ နတ်ဘုရား"
    elif level >= 55:
        return "🔥 သူရဲကောင်း"
    elif level >= 45:
        return "⚔️ စစ်သည်တော်"
    elif level >= 35:
        return "🌱 ခရီးသည်"
    elif level >= 25:
        return "🌿 လမ်းပျောက်"
    elif level >= 15:
        return "🌱 အစပြုသူ"
    else:
        return "🌱 ခရီးစသူ"

def get_level_emoji(level):
    if level >= 85:
        return "🌟"
    elif level >= 75:
        return "👑"
    elif level >= 65:
        return "⭐"
    elif level >= 55:
        return "🔥"
    elif level >= 45:
        return "⚔️"
    elif level >= 35:
        return "🌱"
    elif level >= 25:
        return "🌿"
    elif level >= 15:
        return "🌱"
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
    """通过 send_message 渲染场景（自动记录消息ID）"""
    scene = LEVEL_SCENES.get(scene_id)
    if not scene:
        await context.bot.send_message(chat_id=chat_id, text="❌ ဇာတ်လမ်းမှားယွင်းနေသည်။ /game ကိုနှိပ်ပါ။")
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
    header += f"{level_emoji} အဆင့် {current_level}/90 | {title}\n"
    header += f"━━━━━━━━━━━━━━━━\n\n"
    
    if not options:
        if scene_id.endswith("_boss"):
            level = int(scene_id.split("_")[1])
            win_scene = f"level_{level}_win"
            states = load_game_states()
            states[user_id]["level"] = level + 1 if level < 90 else 90
            save_game_states(states)
            await render_scene_with_send(context, chat_id, win_scene, user_id)
            return
        
        final_text = f"{header}{text}\n\n✨ ပြန်စချင်ရင် /game ကိုနှိပ်ပါ။"
        msg = await context.bot.send_message(chat_id=chat_id, text=final_text, parse_mode="Markdown")
        save_game_message(user_id, chat_id, msg.message_id)
        return
    
    keyboard = []
    for key, label in options.items():
        callback_data = f"game_{key}_{user_id}"
        keyboard.append([InlineKeyboardButton(label, callback_data=callback_data)])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    full_text = f"{header}{text}"
    msg = await context.bot.send_message(chat_id=chat_id, text=full_text, parse_mode="Markdown", reply_markup=reply_markup)
    # ✅ 保存消息ID
    save_game_message(user_id, chat_id, msg.message_id)

async def game_start(update, context):
    user_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id
    user_id_int, username = get_user_info(update)
    log_action(user_id_int, username, "GAME_START", "开始闯关游戏")
    
    # ✅ 先清理旧消息
    await clear_game_messages(context, user_id, chat_id)
    
    state = get_player_state(user_id)
    
    if state and state.get("is_playing", False):
        keyboard = [
            [InlineKeyboardButton("✅ ဟုတ်ကဲ့၊ ပြန်စမည်", callback_data=f"restart_confirm_{user_id}")],
            [InlineKeyboardButton("❌ မဟုတ်ဘူး၊ ဆက်ကစားမယ်", callback_data=f"restart_cancel_{user_id}")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        msg = await update.message.reply_text(
            "⚠️ သတိပေးချက်\n\nမင်းမှာ ဂိမ်းတစ်ခုရှိနေပြီ။\nပြန်စမယ်ဆိုရင် အဟောင်းအကုန်ပျက်သွားမယ်။\n\nသေချာပြီလား?",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        save_game_message(user_id, chat_id, msg.message_id)
        return
    
    player = get_or_create_player(user_id)
    current_level = player.get("level", 1)
    max_level = player.get("max_level", 1)
    title = get_level_title(max_level)
    player_name = player.get("name", "စွန့်စားသူ")
    
    states = load_game_states()
    states[user_id]["is_playing"] = True
    states[user_id]["current_scene"] = f"level_{current_level}_start"
    states[user_id]["game_messages"] = []
    save_game_states(states)
    
    level_data = LEVELS.get(current_level, LEVELS[1])
    level_emoji = get_level_emoji(current_level)
    
    msg = await update.message.reply_text(
        f"🌟 {player_name} မင်္ဂလာပါ!\n\n"
        f"{level_emoji} အဆင့် {current_level}/90 | {title}\n"
        f"🏆 အမြင့်ဆုံး: {max_level}\n\n"
        f"🎯 *{level_data['name']}*\n"
        f"{level_data['desc']}",
        parse_mode="Markdown"
    )
    save_game_message(user_id, chat_id, msg.message_id)
    await render_scene_with_send(context, chat_id, f"level_{current_level}_start", user_id)

async def game_restart(update, context):
    user_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id
    user_id_int, username = get_user_info(update)
    log_action(user_id_int, username, "GAME_RESTART", "重新开始闯关游戏")
    
    # ✅ 清理所有游戏消息
    await clear_game_messages(context, user_id, chat_id)
    
    reset_player_game(user_id)
    state = get_player_state(user_id)
    player_name = state.get("name", "စွန့်စားသူ")
    
    # 重置消息列表
    states = load_game_states()
    states[user_id]["game_messages"] = []
    save_game_states(states)
    
    msg = await update.message.reply_text(
        f"🔄 {player_name} ဂိမ်းကိုပြန်စပါပြီ။\n\n"
        "🌱 အဆင့် 1/90 | ခရီးစသူ\n\n"
        f"🎯 *{LEVELS[1]['name']}*\n"
        f"{LEVELS[1]['desc']}",
        parse_mode="Markdown"
    )
    save_game_message(user_id, chat_id, msg.message_id)
    await render_scene_with_send(context, chat_id, "level_1_start", user_id)

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

# ===== 状态面板 =====

async def game_status(update, context):
    user_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id
    state = get_player_state(user_id)
    
    if not state:
        await update.message.reply_text("❌ မင်းမှာ ဂိမ်းမရှိပါ။ /game နဲ့စပါ။")
        return
    
    await clear_game_messages(context, user_id, chat_id, keep_last=2)
    
    player_name = state.get("name", "စွန့်စားသူ")
    level = state.get("level", 1)
    max_level = state.get("max_level", 1)
    hp = state.get("hp", MAX_HP)
    max_hp = state.get("max_hp", MAX_HP)
    energy = state.get("energy", MAX_ENERGY)
    max_energy = state.get("max_energy", MAX_ENERGY)
    gold = state.get("gold", 0)
    attack = state.get("attack", 3)
    defense = state.get("defense", 1)
    exp = state.get("exp", 0)
    exp_to_next = state.get("exp_to_next", 10)
    weapon = state.get("weapon")
    armor = state.get("armor")
    potions = state.get("potions", [])
    achievements = state.get("achievements", [])
    deaths = state.get("deaths", 0)
    
    weapon_bonus = weapon.get("attack", 0) if weapon else 0
    armor_bonus = armor.get("defense", 0) if armor else 0
    total_attack = attack + weapon_bonus
    total_defense = defense + armor_bonus
    
    weapon_text = f"{weapon['name']} (+{weapon_bonus})" if weapon else "❌ မရှိ"
    armor_text = f"{armor['name']} (+{armor_bonus})" if armor else "❌ မရှိ"
    potion_text = f"{len(potions)} လုံး" if potions else "❌ မရှိ"
    achievement_text = ", ".join(achievements) if achievements else "❌ မရှိသေး"
    title = get_level_title(max_level)
    level_emoji = get_level_emoji(level)
    
    def progress_bar(current, total, length=12):
        if total <= 0:
            return "█" * length
        filled = int((current / total) * length)
        filled = min(filled, length)
        empty = length - filled
        return "█" * filled + "░" * empty
    
    hp_bar = progress_bar(hp, max_hp, 12)
    hp_percent = int((hp / max_hp) * 100) if max_hp > 0 else 0
    energy_bar = progress_bar(energy, max_energy, 12)
    energy_percent = int((energy / max_energy) * 100) if max_energy > 0 else 0
    exp_bar = progress_bar(exp, exp_to_next, 12)
    exp_percent = int((exp / exp_to_next) * 100) if exp_to_next > 0 else 0
    
    # ✅ 确保 status_text 始终被定义
    status_text = f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    status_text += f"👤 *{player_name}*\n"
    status_text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    status_text += f"{level_emoji} *အဆင့် {level}* | {title}\n"
    status_text += f"🏆 အမြင့်ဆုံး: {max_level}\n"
    status_text += f"💀 သေဆုံးမှု: {deaths}\n"
    status_text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    status_text += f"\n❤️ *HP*    {hp_bar}  {hp}/{max_hp} ({hp_percent}%)\n"
    status_text += f"⚡ *Energy* {energy_bar}  {energy}/{max_energy} ({energy_percent}%)\n"
    status_text += f"⭐ *Exp*   {exp_bar}  {exp}/{exp_to_next} ({exp_percent}%)\n"
    status_text += f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    status_text += f"💰 *ရွှေ:* {gold}\n"
    status_text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    status_text += f"⚔️ *တိုက်ခိုက်အား:* {total_attack} (ကိုယ်ပိုင် {attack} + လက်နက် {weapon_bonus})\n"
    status_text += f"🛡️ *ကာကွယ်အား:* {total_defense} (ကိုယ်ပိုင် {defense} + ဒိုင်း {armor_bonus})\n"
    status_text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    status_text += f"🗡️ *လက်နက်:* {weapon_text}\n"
    status_text += f"🛡️ *ဒိုင်း:* {armor_text}\n"
    status_text += f"🧪 *ဆေး:* {potion_text}\n"
    status_text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    status_text += f"🏅 *အောင်မြင်မှုများ:* {achievement_text}\n"
    status_text += f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    
    keyboard = [
        [InlineKeyboardButton("🏪 ဈေးဆိုင်", callback_data="shop_open")],
        [InlineKeyboardButton("🔙 ဂိမ်းသို့ပြန်ရန်", callback_data="back_to_game")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = await update.message.reply_text(status_text, parse_mode="Markdown", reply_markup=reply_markup)
    save_game_message(user_id, chat_id, msg.message_id)

# ===== 商店系统 =====

async def game_shop(update, context):
    """/shop 指令 - 通过消息打开商店"""
    user_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id
    state = get_player_state(user_id)
    
    if not state:
        await update.message.reply_text("❌ မင်းမှာ ဂိမ်းမရှိပါ။ /game နဲ့စပါ။")
        return
    
    # ✅ 清理旧消息（保留最新2条）
    await clear_game_messages(context, user_id, chat_id, keep_last=2)
    
    level = state.get("level", 1)
    gold = state.get("gold", 0)
    items = generate_shop_items(level)
    
    text = f"🏪 *ဈေးဆိုင်*\n\n"
    text += f"💰 မင်းရဲ့ရွှေ: {gold}\n\n"
    text += f"📦 *ပစ္စည်းများ:*\n"
    
    keyboard = []
    for i, item in enumerate(items[:6]):
        price = item["price"]
        if item["type"] == "weapon":
            text += f"{i+1}. {item['name']} ⚔️+{item['attack']} 💰{price}\n"
        elif item["type"] == "armor":
            text += f"{i+1}. {item['name']} 🛡️+{item['defense']} 💰{price}\n"
        else:
            text += f"{i+1}. {item['name']} ❤️+{item['heal']} 💰{price}\n"
        keyboard.append([InlineKeyboardButton(f"🛒 {item['name']} ({price}💰)", callback_data=f"shop_buy_{i}_{user_id}")])
    
    keyboard.append([InlineKeyboardButton("🔙 ဂိမ်းသို့ပြန်ရန်", callback_data="back_to_game")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.user_data["shop_items"] = items
    msg = await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    save_game_message(user_id, chat_id, msg.message_id)

# ===== 商店回调 =====

async def shop_callback(update, context):
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    data = query.data
    chat_id = query.message.chat.id
    
    # ✅ 记录并删除旧消息
    try:
        await query.delete_message()
    except Exception:
        pass
    
    if data == "shop_open":
        state = get_player_state(user_id)
        if not state:
            await context.bot.send_message(chat_id=chat_id, text="❌ မင်းမှာ ဂိမ်းမရှိပါ။ /game နဲ့စပါ။")
            return
        await show_shop(query, context, user_id, chat_id)
        return
    
    if data == "back_to_game":
        state = get_player_state(user_id)
        if state:
            current_scene = state.get("current_scene", "level_1_start")
            # 清理消息
            await clear_game_messages(context, user_id, chat_id, keep_last=1)
            await render_scene_with_send(context, chat_id, current_scene, user_id)
        return
    
    if data.startswith("shop_buy_"):
        # ... 购买逻辑 ...
        pass


async def show_shop(query, context, user_id, chat_id):
    """显示商店界面"""
    state = get_player_state(user_id)
    if not state:
        await context.bot.send_message(chat_id=chat_id, text="❌ မင်းမှာ ဂိမ်းမရှိပါ။ /game နဲ့စပါ။")
        return
    
    level = state.get("level", 1)
    gold = state.get("gold", 0)
    items = generate_shop_items(level)
    
    text = f"🏪 *ဈေးဆိုင်*\n\n"
    text += f"💰 မင်းရဲ့ရွှေ: {gold}\n\n"
    text += f"📦 *ပစ္စည်းများ:*\n"
    
    keyboard = []
    for i, item in enumerate(items[:6]):
        price = item["price"]
        if item["type"] == "weapon":
            text += f"{i+1}. {item['name']} ⚔️+{item['attack']} 💰{price}\n"
        elif item["type"] == "armor":
            text += f"{i+1}. {item['name']} 🛡️+{item['defense']} 💰{price}\n"
        else:
            text += f"{i+1}. {item['name']} ❤️+{item['heal']} 💰{price}\n"
        keyboard.append([InlineKeyboardButton(f"🛒 {item['name']} ({price}💰)", callback_data=f"shop_buy_{i}_{user_id}")])
    
    keyboard.append([InlineKeyboardButton("🔙 ဂိမ်းသို့ပြန်ရန်", callback_data="back_to_game")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    context.user_data["shop_items"] = items
    msg = await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown", reply_markup=reply_markup)
    save_game_message(user_id, chat_id, msg.message_id)

async def game_callback(update, context):
    query = update.callback_query
    
    user_id = str(query.from_user.id)
    user_id_int, username = get_user_info_from_query(query)
    data = query.data
    chat_id = query.message.chat.id
    message_id = query.message.message_id
    
    log_action(user_id_int, username, "CALLBACK", f"点击按钮: {data}")
    
    # ✅ 先记录要删除的消息ID
    states = load_game_states()
    if user_id in states:
        messages = states[user_id].get("game_messages", [])
        if message_id not in messages:
            messages.append(message_id)
            states[user_id]["game_messages"] = messages[-50:]
            save_game_states(states)
    
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
        
        # ✅ 清理旧消息
        await clear_game_messages(context, user_id, chat_id)
        
        reset_player_game(user_id)
        states = load_game_states()
        states[user_id]["game_messages"] = []
        save_game_states(states)
        
        msg = await context.bot.send_message(
            chat_id=chat_id,
            text=f"✅ ဂိမ်းကိုပြန်စပါပြီ။\n\n🌱 အဆင့် 1/90 | ခရီးစသူ\n\n🎯 *{LEVELS[1]['name']}*\n{LEVELS[1]['desc']}",
            parse_mode="Markdown"
        )
        save_game_message(user_id, chat_id, msg.message_id)
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
def main():
    print("📌 Entering main()...")
    app = Application.builder().token(TOKEN).build()
    
    try:
        app.bot.delete_webhook(drop_pending_updates=True)
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
    app.add_handler(CommandHandler("status", game_status))
    app.add_handler(CommandHandler("shop", game_shop))
    app.add_handler(CommandHandler("announce", announce))
    app.add_handler(CallbackQueryHandler(random_link_callback, pattern="^random_link$"))
    app.add_handler(CallbackQueryHandler(back_to_menu_callback, pattern="^back_to_menu$"))
    app.add_handler(CallbackQueryHandler(game_callback, pattern="^game_"))
    app.add_handler(CallbackQueryHandler(game_callback, pattern="^restart_"))
    app.add_handler(CallbackQueryHandler(game_callback, pattern="^level_"))
    app.add_handler(CallbackQueryHandler(shop_callback, pattern="^shop_"))
    app.add_handler(CallbackQueryHandler(shop_callback, pattern="^back_to_game$"))
    app.add_handler(CallbackQueryHandler(shop_callback, pattern="^shop_open$"))
    app.add_handler(CallbackQueryHandler(announce_callback, pattern="^announce_"))
    app.add_handler(CallbackQueryHandler(announce_callback, pattern="^announce_subscribe_"))
    
    print("📌 All handlers added...")
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(check_schedule(app))
    
    print("🤖 Advanced Bot started.")
    print("📊 Loaded commands. Owner-only functions active.")
    app.run_polling()

if __name__ == "__main__":
    print("🔵 Script started...")
    main()