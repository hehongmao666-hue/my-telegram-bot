# ==========================
# services/link.py - 随机链接
# ==========================

import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from config import RANDOM_LINKS


async def random_link_callback(update, context):
    """处理随机链接按钮点击"""
    query = update.callback_query
    await query.answer()

    selected_url = random.choice(RANDOM_LINKS)

    keyboard = [
        [InlineKeyboardButton("🔗 နှိပ်ပြီးဝင်ရောက်ရန်(တီးမယ်)", url=selected_url, style="success")],
        [InlineKeyboardButton("🔙 နောက်သို့ပြန်သွားရန်", callback_data="back_to_menu", style="danger")],
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
        [InlineKeyboardButton("👥 ချစ်သူရှာမယ် Gp 1", url="https://t.me/Myanmar_GameFriendss", style="primary")],
        [InlineKeyboardButton("👥 ချစ်သူရှာမယ် Gp 2", url="https://t.me/Myanmar_GameFriends", style="primary")],
        [InlineKeyboardButton("🛒 Game Friend Shop ဆိုင် 1", url="https://t.me/PUBGUCshop_01", style="primary")],
        [InlineKeyboardButton("🎰 စလော့ နဲ့ Lottery ဂိမ်းများ(တီးမယ်)", callback_data="random_link", style="success")],
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