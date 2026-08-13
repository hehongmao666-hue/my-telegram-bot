# ==========================
# game/main.py - 游戏主指令（完整修复版）
# ==========================

import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import OWNER_ID
from storage import load_game_states, save_game_states, get_player_state
from game.scenes import LEVELS, LEVEL_SCENES
from game.config import MAX_HP, MAX_ENERGY
from game.utils import get_level_title, get_level_emoji
from utils.logger import log_action
from utils.helpers import get_user_info
from utils.message import save_game_message, clear_game_messages
from game.status import render_scene, render_scene_with_send


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


def get_or_create_player(user_id):
    states = load_game_states()
    if states is None:
        states = {}
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
            "gold": 5,
            "attack": 2,
            "defense": 1,
            "exp": 0,
            "exp_to_next": 20,
            "weapon": None,
            "armor": None,
            "potions": [],
            "achievements": [],
            "deaths": 0
        }
        save_game_states(states)
    return states[user_id]


def reset_player_game(user_id):
    states = load_game_states()
    if states is None:
        states = {}
    if user_id not in states:
        get_or_create_player(user_id)
        states = load_game_states()
        if states is None:
            states = {}

    states[user_id]["level"] = 1
    states[user_id]["is_playing"] = True
    states[user_id]["current_scene"] = "level_1_start"
    states[user_id]["hp"] = states[user_id].get("max_hp", MAX_HP)
    states[user_id]["energy"] = states[user_id].get("max_energy", MAX_ENERGY)
    gold = states[user_id].get("gold", 5)
    states[user_id]["gold"] = max(5, gold // 2)
    states[user_id]["potions"] = []
    states[user_id]["deaths"] = states[user_id].get("deaths", 0) + 1
    save_game_states(states)
    return states[user_id]


def add_exp(user_id, exp):
    states = load_game_states()
    if states is None or user_id not in states:
        return
    states[user_id]["exp"] += exp
    exp_to_next = states[user_id].get("exp_to_next", 20)
    level = states[user_id].get("level", 1)
    while states[user_id]["exp"] >= exp_to_next:
        states[user_id]["exp"] -= exp_to_next
        states[user_id]["level"] += 1
        level = states[user_id]["level"]
        states[user_id]["exp_to_next"] = int(exp_to_next * 1.8)
        states[user_id]["max_hp"] += 8
        states[user_id]["hp"] = min(states[user_id]["hp"] + 8, states[user_id]["max_hp"])
        states[user_id]["attack"] += 1
        states[user_id]["defense"] += 1
        from game.config import ACHIEVEMENTS
        for achieve_level, title in ACHIEVEMENTS.items():
            if level >= achieve_level and title not in states[user_id].get("achievements", []):
                states[user_id]["achievements"].append(title)
        exp_to_next = states[user_id]["exp_to_next"]
    save_game_states(states)


def mark_level_complete(user_id, level):
    states = load_game_states()
    if states is None or user_id not in states:
        return
    if level > states[user_id].get("max_level", 1):
        states[user_id]["max_level"] = level
    if level == 30:
        states[user_id]["is_playing"] = False
    max_hp = states[user_id].get("max_hp", MAX_HP)
    current_hp = states[user_id].get("hp", max_hp)
    states[user_id]["hp"] = min(max_hp, current_hp + int(max_hp * 0.3))
    save_game_states(states)


async def game_start(update, context):
    user_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id
    user_id_int, username = get_user_info(update)
    log_action(user_id_int, username, "GAME_START", "开始闯关游戏")

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
    if states is None:
        states = {}
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
    
    # 发送地牢入口按钮
    dungeon_keyboard = [[InlineKeyboardButton("🏰 မြေအောက်ခန်းသို့", callback_data=f"dungeon_enter_from_game_{user_id}")]]
    await context.bot.send_message(
        chat_id=chat_id,
        text="🏰 မြေအောက်ခန်းကို စူးစမ်းချင်ရင် အောက်ပါခလုတ်ကိုနှိပ်ပါ။",
        reply_markup=InlineKeyboardMarkup(dungeon_keyboard)
    )


async def game_restart(update, context):
    user_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id
    user_id_int, username = get_user_info(update)
    log_action(user_id_int, username, "GAME_RESTART", "重新开始闯关游戏")

    await clear_game_messages(context, user_id, chat_id)

    reset_player_game(user_id)
    state = get_player_state(user_id)
    player_name = state.get("name", "စွန့်စားသူ") if state else "စွန့်စားသူ"

    states = load_game_states()
    if states is None:
        states = {}
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
    if states is None:
        states = {}
    states[user_id]["current_scene"] = start_scene
    save_game_states(states)

    await update.message.reply_text("🔙 နောက်တစ်ဆင့်ကိုပြန်သွားပါပြီ။")
    await render_scene(update.message, context, start_scene, user_id)


# ==========================
# Dungeon Start
# ==========================

async def dungeon_start(update, context):
    user_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id
    
    # 先确保 states 存在
    states = load_game_states()
    if states is None:
        states = {}
        save_game_states(states)
    
    state = get_player_state(user_id)
    if not state:
        await update.message.reply_text("❌ ကျေးဇူးပြု၍ /game ဖြင့် ဇာတ်ကောင်ဖန်တီးပါ။")
        return
    
    # 检查是否有进行中的地牢进度
    current_floor = context.user_data.get(f"dungeon_floor_{user_id}", 1)
    
    # 如果有进度，恢复进度而不是重置
    if current_floor > 1 and state.get("hp", 0) > 0:
        keyboard = [
            [InlineKeyboardButton("🚪 ဆက်လက်စူးစမ်းမယ်", callback_data=f"dungeon_continue_{user_id}")],
            [InlineKeyboardButton("🔄 အစကနေပြန်စမယ်", callback_data=f"dungeon_restart_{user_id}")],
        ]
        attack = state.get("attack", 3) + (state.get("weapon", {}).get("attack", 0) if state.get("weapon") else 0)
        defense = state.get("defense", 1) + (state.get("armor", {}).get("defense", 0) if state.get("armor") else 0)
        gold = state.get("gold", 0)
        potions = len(state.get("potions", []))
        
        msg = (
            f"🏰 *အရိပ်မြေအောက်ခန်း - အထပ် {current_floor}*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"❤️ HP: {state['hp']}/{state.get('max_hp', 30)}\n"
            f"⚔️ တိုက်ခိုက်အား: {attack}  🛡️ ကာကွယ်အား: {defense}\n"
            f"💰 ရွှေ: {gold}  🧪 ဆေး: {potions}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"⚡ မင်းရဲ့ခရီးကို ဆက်လက်ပါ။\n"
            f"အထပ် {current_floor} ကနေ ဆက်သွားမလား ဒါမှမဟုတ် အစကနေပြန်စမလား။"
        )
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    # 新游戏或重置
    context.user_data[f"dungeon_floor_{user_id}"] = 1
    state["hp"] = state.get("max_hp", 30)
    states = load_game_states()
    if states is None:
        states = {}
    states[user_id] = state
    save_game_states(states)
    
    keyboard = [[InlineKeyboardButton("🚪 မြေအောက်ခန်းထဲဝင်မယ်", callback_data=f"dungeon_explore_{user_id}")]]
    
    attack = state.get("attack", 3) + (state.get("weapon", {}).get("attack", 0) if state.get("weapon") else 0)
    defense = state.get("defense", 1) + (state.get("armor", {}).get("defense", 0) if state.get("armor") else 0)
    gold = state.get("gold", 0)
    potions = len(state.get("potions", []))
    
    msg = (
        f"🏰 *အရိပ်မြေအောက်ခန်းကို ကြိုဆိုပါတယ်။*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"❤️ HP: {state['hp']}/{state.get('max_hp', 30)}\n"
        f"⚔️ တိုက်ခိုက်အား: {attack}  🛡️ ကာကွယ်အား: {defense}\n"
        f"💰 ရွှေ: {gold}  🧪 ဆေး: {potions}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⚡ ဒီမြေအောက်ခန်းက အဆုံးမရှိတဲ့ ကျပန်းစိန်ခေါ်မှုတွေရှိတယ်။\n"
        f"• အထပ်တိုင်းမှာ ကျပန်းဖြစ်ရပ် - တိုက်ပွဲ၊ ရတနာ၊ ထောင်ချောက်၊ အနားယူ၊ ကုန်သည်\n"
        f"• ၅ ထပ်တိုင်း Boss တိုက်ပွဲ။\n"
        f"• မင်း ဘယ်အထပ်ထိရောက်နိုင်လဲ စမ်းကြည့်။"
    )
    
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    # ==========================
# 每日签到 - 添加到 game/main.py
# ==========================

import time
from datetime import datetime, timedelta

async def daily_checkin(update, context):
    """每日签到"""
    user_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id

    states = load_game_states()
    if states is None:
        states = {}
    if user_id not in states:
        await update.message.reply_text("❌ ကျေးဇူးပြု၍ /game ဖြင့် ဇာတ်ကောင်ဖန်တီးပါ။")
        return

    now = int(time.time())

    # 获取上次签到时间
    last_checkin = states[user_id].get("last_checkin", 0)
    checkin_streak = states[user_id].get("checkin_streak", 0)

    # 检查是否今天已签到
    last_date = datetime.fromtimestamp(last_checkin).strftime("%Y-%m-%d")
    today = datetime.now().strftime("%Y-%m-%d")

    if last_date == today:
        await update.message.reply_text("✅ ဒီနေ့ သင်ပြီးသွားပြီ။\nမနက်ဖြန်ပြန်လာခဲ့ပါ။")
        return

    # 检查是否连续签到
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    if last_date == yesterday:
        checkin_streak += 1
    else:
        checkin_streak = 1

    # 计算奖励
    base_gold = 20
    streak_bonus = min(checkin_streak // 3, 10) * 5  # 每3天+5金币，最多+10
    bonus_gold = base_gold + streak_bonus

    # 额外奖励：连续7天额外奖励
    extra_bonus = 0
    if checkin_streak % 7 == 0:
        extra_bonus = 30
        bonus_gold += extra_bonus

    # 发放奖励
    states[user_id]["gold"] = states[user_id].get("gold", 0) + bonus_gold
    states[user_id]["last_checkin"] = now
    states[user_id]["checkin_streak"] = checkin_streak
    save_game_states(states)

    # 构建消息
    msg = f"✅ *နေ့စဉ်ဝင်ကစားခြင်း အောင်မြင်ပါပြီ!*\n\n"
    msg += f"💰 ရရှိသောရွှေ: +{bonus_gold}\n"
    msg += f"🔥 ဆက်တိုက်ဝင်ကစားမှု: {checkin_streak} ရက်\n"

    if streak_bonus > 0:
        msg += f"🎁 ဆက်တိုက်ဆုကြေး: +{streak_bonus}\n"
    if extra_bonus > 0:
        msg += f"🎉 ၇ ရက်ပြည့်ဆု: +{extra_bonus} 🎉\n"

    msg += f"\n💰 လက်ရှိရွှေ: {states[user_id]['gold']}"
    await update.message.reply_text(msg, parse_mode="Markdown")

    # 检查成就
    if checkin_streak >= 7:
        achievements = states[user_id].get("achievements", [])
        if "🔥 ၇ ရက်ဆက်တိုက်ဝင်ကစားသူ" not in achievements:
            achievements.append("🔥 ၇ ရက်ဆက်တိုက်ဝင်ကစားသူ")
            states[user_id]["achievements"] = achievements
            save_game_states(states)
            await update.message.reply_text("🏅 *အောင်မြင်မှုရရှိပါပြီ!*\n🔥 ၇ ရက်ဆက်တိုက်ဝင်ကစားသူ")