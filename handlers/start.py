# ==========================
# handlers/start.py - 基础指令（升级版 Help）
# ==========================

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from storage import load_data, add_user, add_group
from utils.logger import log_action
from utils.helpers import get_user_info, owner_only
from config import ADMIN_IDS


async def start(update, context):
    uid = update.effective_user.id
    cid = update.effective_chat.id
    add_user(uid)
    if cid != uid:
        add_group(cid)

    user_id, username = get_user_info(update)
    log_action(user_id, username, "START", "用户启动Bot")

    keyboard = [
        [InlineKeyboardButton("👥 ချစ်သူရှာမယ် Gp 1", url="https://t.me/Myanmar_GameFriendss", style="primary")],
        [InlineKeyboardButton("👥 ချစ်သူရှာမယ် Gp 2", url="https://t.me/Myanmar_GameFriends", style="primary")],
        [InlineKeyboardButton("🛒 Game Friend Shop ဆိုင် 1", url="https://t.me/PUBGUCshop_01", style="primary")],
        [InlineKeyboardButton("🎰 စလော့ နဲ့ Lottery ဂိမ်းများ(တီးမယ်)", callback_data="random_link", style="success")],
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
    """显示帮助菜单（升级版）"""
    user_id = update.effective_user.id
    
    is_admin = user_id in ADMIN_IDS
    
    text = "🤖 *Welcome to the Community Bot!*\n"
    text += "━" * 18 + "\n\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "🎮 *GAME COMMANDS*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "`/game`      Start story mode (90 levels)\n"
    text += "`/dungeon`   Enter dungeon exploration\n"
    text += "`/status`    View character stats\n"
    text += "`/shop`      Open the shop\n"
    text += "`/restartgame` Reset game progress\n"
    text += "`/back`      Go back to previous scene\n\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "🏆 *SOCIAL COMMANDS*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "`/leaderboard` View top adventurers ranking\n"
    text += "`/checkin`    Daily check-in to claim rewards\n"
    text += "`/announce_subscribe`   Subscribe to announcements\n"
    text += "`/announce_unsubscribe` Unsubscribe from announcements\n\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "ℹ️ *BASIC COMMANDS*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "`/start`     Start the bot\n"
    text += "`/help`      Show this help menu\n"
    
    if is_admin:
        text += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
        text += "🔐 *ADMIN COMMANDS*\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━\n"
        text += "`/stats`         View bot statistics\n"
        text += "`/broadcast`     Send message to all users\n"
        text += "`/announce`      Send announcement\n"
        text += "`/stop_announce` Stop announcement\n"
        text += "`/blacklist`     Manage blacklist\n"
        text += "`/preset`        Use preset messages\n"
        text += "`/at` / `/in`    Schedule a message\n"
        text += "`/list_schedule` List scheduled messages\n"
        text += "`/cancel_schedule` Cancel scheduled message\n"
    
    text += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "💡 *Tips:*\n"
    text += "• Use `/game` to start your adventure\n"
    text += "• Use `/dungeon` for endless dungeon runs\n"
    text += "• Use `/checkin` daily for bonus rewards\n"
    
    keyboard = [
        [
            InlineKeyboardButton("🎮 Game", callback_data="help_game", style="primary"),
            InlineKeyboardButton("🏆 Leaderboard", callback_data="help_leaderboard", style="primary"),
        ],
        [
            InlineKeyboardButton("📢 Announcements", callback_data="help_announce", style="primary"),
            InlineKeyboardButton("ℹ️ About", callback_data="help_about", style="primary"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)


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


# ============ Help Callbacks ============

async def help_game_callback(update, context):
    """帮助 - 游戏说明"""
    query = update.callback_query
    await query.answer()
    
    text = "🎮 *Game Guide*\n"
    text += "━" * 18 + "\n\n"
    text += "📖 *Story Mode* (`/game`)\n"
    text += "• 90 levels with unique stories\n"
    text += "• Choose your path (3 options per level)\n"
    text += "• Level up with EXP system\n"
    text += "• Equipment system (weapons, armor)\n"
    text += "• Potion system\n"
    text += "• Achievement system\n\n"
    text += "🏰 *Dungeon Mode* (`/dungeon`)\n"
    text += "• Infinite random floors\n"
    text += "• Random events: Combat, Treasure, Trap, Rest, Merchant\n"
    text += "• Boss fights every 5 floors\n"
    text += "• Shared character progression\n\n"
    text += "💪 *Tips:*\n"
    text += "• Save gold for better equipment\n"
    text += "• Use potions wisely in tough battles\n"
    text += "• Check `/status` regularly to track your progress"
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Help", callback_data="help_back", style="danger")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    except Exception:
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)


async def help_leaderboard_callback(update, context):
    """帮助 - 排行榜说明"""
    query = update.callback_query
    await query.answer()
    
    text = "🏆 *Leaderboard*\n"
    text += "━" * 18 + "\n\n"
    text += "📊 *How it works:*\n"
    text += "• Players are ranked by their highest level\n"
    text += "• Tie-breaker: Gold amount\n"
    text += "• Top 20 players are shown\n"
    text += "• Your rank is displayed at the bottom\n\n"
    text += "📈 *Ranking Criteria:*\n"
    text += "🥇 Highest level reached\n"
    text += "🥈 Gold coins collected\n"
    text += "🥉 Total monsters defeated\n\n"
    text += "💡 Use `/leaderboard` anytime to check rankings!"
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Help", callback_data="help_back", style="danger")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    except Exception:
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)


async def help_announce_callback(update, context):
    """帮助 - 公告说明"""
    query = update.callback_query
    await query.answer()
    
    text = "📢 *Announcements*\n"
    text += "━" * 18 + "\n\n"
    text += "📬 *Subscribe:* `/announce_subscribe`\n"
    text += "• Receive important updates\n"
    text += "• Get notified about events\n"
    text += "• Never miss a thing!\n\n"
    text += "📭 *Unsubscribe:* `/announce_unsubscribe`\n"
    text += "• Stop receiving announcements\n\n"
    text += "🔐 *Admin Only:*\n"
    text += "• `/announce` - Send announcement\n"
    text += "• `/stop_announce` - Stop announcement"
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Help", callback_data="help_back", style="danger")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    except Exception:
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)


async def help_about_callback(update, context):
    """帮助 - 关于"""
    query = update.callback_query
    await query.answer()
    
    text = "ℹ️ About This Bot\n"
    text += "━" * 18 + "\n\n"
    text += "🤖 Community Manager Bot\n"
    text += "A multi-purpose Telegram bot with:\n"
    text += "• RPG Game System\n"
    text += "• Dungeon Adventure Mode\n"
    text += "• Announcement System\n"
    text += "• User Management\n\n"
    text += "📝 Version: 3.2\n"
    text += "👨‍💻 Developer: @MCLP1_1\n"
    text += "📅 Updated: August 2026"
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Help", callback_data="help_back", style="danger")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(text, parse_mode=None, reply_markup=reply_markup)
    except Exception:
        await query.message.reply_text(text, parse_mode=None, reply_markup=reply_markup)


async def help_back_callback(update, context):
    """返回帮助主菜单"""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    is_admin = user_id in ADMIN_IDS
    
    text = "🤖 *Welcome to the Community Bot!*\n"
    text += "━" * 18 + "\n\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "🎮 *GAME COMMANDS*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "`/game`      Start story mode (90 levels)\n"
    text += "`/dungeon`   Enter dungeon exploration\n"
    text += "`/status`    View character stats\n"
    text += "`/shop`      Open the shop\n"
    text += "`/restartgame` Reset game progress\n"
    text += "`/back`      Go back to previous scene\n\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "🏆 *SOCIAL COMMANDS*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "`/leaderboard` View top adventurers ranking\n"
    text += "`/checkin`    Daily check-in to claim rewards\n"
    text += "`/announce_subscribe`   Subscribe to announcements\n"
    text += "`/announce_unsubscribe` Unsubscribe from announcements\n\n"
    
    text += "━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "ℹ️ *BASIC COMMANDS*\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "`/start`     Start the bot\n"
    text += "`/help`      Show this help menu\n"
    
    if is_admin:
        text += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
        text += "🔐 *ADMIN COMMANDS*\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━\n"
        text += "`/stats`         View bot statistics\n"
        text += "`/broadcast`     Send message to all users\n"
        text += "`/announce`      Send announcement\n"
        text += "`/stop_announce` Stop announcement\n"
        text += "`/blacklist`     Manage blacklist\n"
        text += "`/preset`        Use preset messages\n"
        text += "`/at` / `/in`    Schedule a message\n"
        text += "`/list_schedule` List scheduled messages\n"
        text += "`/cancel_schedule` Cancel scheduled message\n"
    
    text += "\n━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "💡 *Tips:*\n"
    text += "• Use `/game` to start your adventure\n"
    text += "• Use `/dungeon` for endless dungeon runs\n"
    text += "• Use `/checkin` daily for bonus rewards"
    
    keyboard = [
        [
            InlineKeyboardButton("🎮 Game", callback_data="help_game", style="primary"),
            InlineKeyboardButton("🏆 Leaderboard", callback_data="help_leaderboard", style="primary"),
        ],
        [
            InlineKeyboardButton("📢 Announcements", callback_data="help_announce", style="primary"),
            InlineKeyboardButton("ℹ️ About", callback_data="help_about", style="primary"),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    try:
        await query.edit_message_text(text, parse_mode="Markdown", reply_markup=reply_markup)
    except Exception:
        await query.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)