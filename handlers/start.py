# ==========================
# handlers/start.py - 基础指令
# ==========================

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from storage import load_data, add_user, add_group
from utils.logger import log_action
from utils.helpers import get_user_info, owner_only


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