# ==========================
# game/leaderboard.py - 排行榜
# ==========================

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from storage import load_game_states


async def leaderboard(update, context):
    """显示排行榜"""
    user_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id

    states = load_game_states()
    if not states:
        await update.message.reply_text("❌ ကစားသူမရှိသေးပါ။")
        return

    # 构建排行榜数据
    players = []
    for uid, data in states.items():
        if data.get("is_playing", False) or data.get("level", 1) > 1:
            players.append({
                "id": uid,
                "name": data.get("name", "စွန့်စားသူ"),
                "level": data.get("level", 1),
                "max_level": data.get("max_level", 1),
                "gold": data.get("gold", 0),
                "deaths": data.get("deaths", 0)
            })

    if not players:
        await update.message.reply_text("❌ ကစားသူမရှိသေးပါ။")
        return

    # 按等级排序（等级高在前，等级相同按金币）
    players.sort(key=lambda x: (-x["max_level"], -x["gold"]))

    # 限制显示前20名
    top_players = players[:20]

    # 玩家自己的排名
    user_rank = None
    for idx, p in enumerate(players, 1):
        if p["id"] == user_id:
            user_rank = idx
            break

    text = "🏆 *ထိပ်တန်းစွန့်စားသူများ*\n"
    text += "━━━━━━━━━━━━━━━━━━━━\n\n"

    medals = ["🥇", "🥈", "🥉"]

    for idx, p in enumerate(top_players, 1):
        medal = medals[idx-1] if idx <= 3 else f"{idx}."
        level_emoji = "👑" if p["max_level"] >= 90 else "⭐" if p["max_level"] >= 50 else "🌟" if p["max_level"] >= 20 else "🌱"
        text += f"{medal} *{p['name'][:12]}*\n"
        text += f"   {level_emoji} အဆင့် {p['max_level']} | 💰 {p['gold']}\n"
        if p["deaths"] > 0:
            text += f"   💀 သေဆုံး {p['deaths']} ကြိမ်\n"
        text += "\n"

    # 显示玩家自己的排名
    if user_rank:
        user_state = states.get(user_id, {})
        text += "━━━━━━━━━━━━━━━━━━━━\n"
        text += f"📌 မင်းရဲ့အဆင့်: #{user_rank}\n"
        text += f"👤 {user_state.get('name', 'စွန့်စားသူ')}\n"
        text += f"⭐ အဆင့် {user_state.get('level', 1)} | 🏆 အမြင့်ဆုံး {user_state.get('max_level', 1)}\n"
        text += f"💰 {user_state.get('gold', 0)} ရွှေ"

    keyboard = [[InlineKeyboardButton("🔄 ပြန်စမ်းကြည့်မယ်", callback_data="leaderboard_refresh")]]
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))


async def leaderboard_refresh_callback(update, context):
    """刷新排行榜"""
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    chat_id = query.message.chat.id

    # 删除原消息
    try:
        await query.delete_message()
    except:
        pass

    # 重新生成排行榜
    states = load_game_states()
    if not states:
        await context.bot.send_message(chat_id=chat_id, text="❌ ကစားသူမရှိသေးပါ။")
        return

    players = []
    for uid, data in states.items():
        if data.get("is_playing", False) or data.get("level", 1) > 1:
            players.append({
                "id": uid,
                "name": data.get("name", "စွန့်စားသူ"),
                "level": data.get("level", 1),
                "max_level": data.get("max_level", 1),
                "gold": data.get("gold", 0),
                "deaths": data.get("deaths", 0)
            })

    if not players:
        await context.bot.send_message(chat_id=chat_id, text="❌ ကစားသူမရှိသေးပါ။")
        return

    players.sort(key=lambda x: (-x["max_level"], -x["gold"]))
    top_players = players[:20]

    user_rank = None
    for idx, p in enumerate(players, 1):
        if p["id"] == user_id:
            user_rank = idx
            break

    text = "🏆 *ထိပ်တန်းစွန့်စားသူများ*\n"
    text += "━━━━━━━━━━━━━━━━━━━━\n\n"

    medals = ["🥇", "🥈", "🥉"]

    for idx, p in enumerate(top_players, 1):
        medal = medals[idx-1] if idx <= 3 else f"{idx}."
        level_emoji = "👑" if p["max_level"] >= 90 else "⭐" if p["max_level"] >= 50 else "🌟" if p["max_level"] >= 20 else "🌱"
        text += f"{medal} *{p['name'][:12]}*\n"
        text += f"   {level_emoji} အဆင့် {p['max_level']} | 💰 {p['gold']}\n"
        if p["deaths"] > 0:
            text += f"   💀 သေဆုံး {p['deaths']} ကြိမ်\n"
        text += "\n"

    if user_rank:
        user_state = states.get(user_id, {})
        text += "━━━━━━━━━━━━━━━━━━━━\n"
        text += f"📌 မင်းရဲ့အဆင့်: #{user_rank}\n"
        text += f"👤 {user_state.get('name', 'စွန့်စားသူ')}\n"
        text += f"⭐ အဆင့် {user_state.get('level', 1)} | 🏆 အမြင့်ဆုံး {user_state.get('max_level', 1)}\n"
        text += f"💰 {user_state.get('gold', 0)} ရွှေ"

    keyboard = [[InlineKeyboardButton("🔄 ပြန်စမ်းကြည့်မယ်", callback_data="leaderboard_refresh")]]
    await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))