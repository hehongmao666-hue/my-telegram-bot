# ==========================
# game/status.py - ဂိမ်းအခြေအနေ / ဈေးဆိုင် (Dungeon အပါအဝင်)
# ==========================

import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from storage import load_game_states, save_game_states, get_player_state
from game.scenes import LEVEL_SCENES, get_dungeon_monster, get_random_event
from game.config import MAX_HP, MAX_ENERGY
from game.utils import get_level_title, get_level_emoji, generate_shop_items
from utils.message import save_game_message, clear_game_messages


async def render_scene(target, context, scene_id, user_id, is_callback=False):
    scene = LEVEL_SCENES.get(scene_id)
    if not scene:
        if scene_id.endswith("_win"):
            from game.main import mark_level_complete
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
    header += f"{level_emoji} အဆင့် {current_level}/90 | {title}\n"
    header += f"━━━━━━━━━━━━━━━━\n\n"

    if not options:
        if scene_id.endswith("_boss"):
            level = int(scene_id.split("_")[1])
            win_scene = f"level_{level}_win"
            states = load_game_states()
            if states is None:
                states = {}
            states[user_id]["level"] = level + 1 if level < 90 else 90
            save_game_states(states)
            await render_scene(target, context, win_scene, user_id, is_callback)
            return

        final_text = f"{header}{text}\n\n✨ ပြန်စချင်ရင် /game ကိုနှိပ်ပါ။"
        # 即使没有选项也添加地牢按钮
        keyboard = [[InlineKeyboardButton("🏰 မြေအောက်ခန်းသို့", callback_data=f"dungeon_enter_from_game_{user_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        if is_callback:
            await target.edit_message_text(final_text, parse_mode="Markdown", reply_markup=reply_markup)
        else:
            await target.reply_text(final_text, parse_mode="Markdown", reply_markup=reply_markup)
        return

    keyboard = []
    for key, label in options.items():
        callback_data = f"game_{key}_{user_id}"
        keyboard.append([InlineKeyboardButton(label, callback_data=callback_data)])
    # 添加地牢入口按钮
    keyboard.append([InlineKeyboardButton("🏰 မြေအောက်ခန်းသို့", callback_data=f"dungeon_enter_from_game_{user_id}")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    full_text = f"{header}{text}"
    if is_callback:
        await target.edit_message_text(full_text, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await target.reply_text(full_text, parse_mode="Markdown", reply_markup=reply_markup)


async def render_scene_with_send(context, chat_id, scene_id, user_id):
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
            from game.main import mark_level_complete
            level = int(scene_id.split("_")[1])
            win_scene = f"level_{level}_win"
            states = load_game_states()
            if states is None:
                states = {}
            states[user_id]["level"] = level + 1 if level < 90 else 90
            save_game_states(states)
            await render_scene_with_send(context, chat_id, win_scene, user_id)
            return

        final_text = f"{header}{text}\n\n✨ ပြန်စချင်ရင် /game ကိုနှိပ်ပါ။"
        keyboard = [[InlineKeyboardButton("🏰 မြေအောက်ခန်းသို့", callback_data=f"dungeon_enter_from_game_{user_id}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        msg = await context.bot.send_message(chat_id=chat_id, text=final_text, parse_mode="Markdown", reply_markup=reply_markup)
        save_game_message(user_id, chat_id, msg.message_id)
        return

    keyboard = []
    for key, label in options.items():
        callback_data = f"game_{key}_{user_id}"
        keyboard.append([InlineKeyboardButton(label, callback_data=callback_data)])
    # 添加地牢入口按钮
    keyboard.append([InlineKeyboardButton("🏰 မြေအောက်ခန်းသို့", callback_data=f"dungeon_enter_from_game_{user_id}")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    full_text = f"{header}{text}"
    msg = await context.bot.send_message(chat_id=chat_id, text=full_text, parse_mode="Markdown", reply_markup=reply_markup)
    save_game_message(user_id, chat_id, msg.message_id)


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
        [InlineKeyboardButton("🏰 မြေအောက်ခန်းသို့", callback_data=f"dungeon_enter_from_game_{user_id}")],
        [InlineKeyboardButton("🔙 ဂိမ်းသို့ပြန်ရန်", callback_data="back_to_game")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    msg = await update.message.reply_text(status_text, parse_mode="Markdown", reply_markup=reply_markup)
    save_game_message(user_id, chat_id, msg.message_id)


async def game_shop(update, context):
    user_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id
    state = get_player_state(user_id)

    if not state:
        await update.message.reply_text("❌ မင်းမှာ ဂိမ်းမရှိပါ။ /game နဲ့စပါ။")
        return

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


# ============ Dungeon Functions ============

async def dungeon_explore(update, context):
    user_id = str(update.effective_user.id)
    chat_id = update.effective_chat.id
    
    state = get_player_state(user_id)
    if not state:
        await update.message.reply_text("❌ ကျေးဇူးပြု၍ /game ဖြင့် ဇာတ်ကောင်ဖန်တီးပါ။")
        return
    
    floor = context.user_data.get(f"dungeon_floor_{user_id}", 1)
    context.user_data[f"dungeon_floor_{user_id}"] = floor
    
    keyboard = [[InlineKeyboardButton("🚪 မြေအောက်ခန်းထဲဝင်မယ်", callback_data=f"dungeon_explore_{user_id}")]]
    
    hp = state.get("hp", 30)
    max_hp = state.get("max_hp", 30)
    attack = state.get("attack", 3) + (state.get("weapon", {}).get("attack", 0) if state.get("weapon") else 0)
    defense = state.get("defense", 1) + (state.get("armor", {}).get("defense", 0) if state.get("armor") else 0)
    gold = state.get("gold", 0)
    potions = len(state.get("potions", []))
    
    msg = (
        f"🏰 *အရိပ်မြေအောက်ခန်း - အထပ် {floor}*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"❤️ HP: {hp}/{max_hp}  ⚔️ တိုက်: {attack}  🛡️ ကာ: {defense}\n"
        f"💰 ရွှေ: {gold}  🧪 ဆေး: {potions}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⚡ မြေအောက်ခန်းထဲ စူးစမ်းဖို့ အဆင်သင့်လား။\n"
        f"အထပ်တိုင်းမှာ မသိတဲ့စိန်ခေါ်မှုတွေ ရှိတယ်။"
    )
    
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))


async def handle_dungeon_event(chat_id, user_id, context, is_callback=False, target=None):
    state = get_player_state(user_id)
    if not state:
        await context.bot.send_message(chat_id=chat_id, text="❌ ဇာတ်ကောင်မရှိပါ။")
        return
    
    floor = context.user_data.get(f"dungeon_floor_{user_id}", 1)
    event_type = get_random_event()
    hp = state.get("hp", 30)
    max_hp = state.get("max_hp", 30)
    
    if event_type == "combat":
        monster = get_dungeon_monster(floor)
        context.user_data[f"dungeon_monster_{user_id}"] = monster
        
        keyboard = [
            [InlineKeyboardButton("⚔️ တိုက်မယ်", callback_data=f"dungeon_attack_{user_id}")],
            [InlineKeyboardButton("🧪 ဆေးသုံးမယ်", callback_data=f"dungeon_potion_{user_id}")],
            [InlineKeyboardButton("🏃 ထွက်ပြေးမယ်", callback_data=f"dungeon_flee_{user_id}")],
        ]
        
        boss_tag = "👑 BOSS! " if monster.get("is_boss") else ""
        msg = (
            f"⚔️ *{boss_tag}{monster['name']} ကိုတွေ့လိုက်တယ်။*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"❤️ {monster['name']} HP: {monster['hp']}  ⚔️ တိုက်: {monster['attack']}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"❤️ မင်းရဲ့ HP: {hp}/{max_hp}\n\n"
            f"ဘာလုပ်မလဲ။"
        )
        
        if is_callback and target:
            await target.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
            
    elif event_type == "treasure":
        gold_gain = random.randint(5, 15) + floor
        state["gold"] = state.get("gold", 0) + gold_gain
        states = load_game_states()
        if states is None:
            states = {}
        states[user_id] = state
        save_game_states(states)
        
        keyboard = [[InlineKeyboardButton("🚪 ဆက်သွားမယ်", callback_data=f"dungeon_continue_{user_id}")]]
        msg = f"💎 ရတနာသေတ္တာတွေ့တယ်။ ရွှေ {gold_gain} ရတယ်။"
        if is_callback and target:
            await target.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await context.bot.send_message(chat_id=chat_id, text=msg, reply_markup=InlineKeyboardMarkup(keyboard))
            
    elif event_type == "trap":
        damage = random.randint(3, 8) + floor // 2
        state["hp"] = max(0, state.get("hp", 30) - damage)
        states = load_game_states()
        if states is None:
            states = {}
        states[user_id] = state
        save_game_states(states)
        
        if state["hp"] <= 0:
            keyboard = [[InlineKeyboardButton("🔄 ပြန်စမယ်", callback_data=f"dungeon_restart_{user_id}")]]
            msg = f"💥 ထောင်ချောက်ထဲကျသွားတယ်။ အသက် {damage} ဆုံးရှုံးတယ်။\n\n💀 မင်းသေသွားပြီ။ အထပ် {floor} မှာ။"
            if is_callback and target:
                await target.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                await context.bot.send_message(chat_id=chat_id, text=msg, reply_markup=InlineKeyboardMarkup(keyboard))
            return
        else:
            keyboard = [[InlineKeyboardButton("🚪 ဆက်သွားမယ်", callback_data=f"dungeon_continue_{user_id}")]]
            msg = f"💥 ထောင်ချောက်ထဲကျသွားတယ်။ အသက် {damage} ဆုံးရှုံးတယ်။\n❤️ ကျန်တဲ့ HP: {state['hp']}/{state.get('max_hp', 30)}"
            if is_callback and target:
                await target.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
            else:
                await context.bot.send_message(chat_id=chat_id, text=msg, reply_markup=InlineKeyboardMarkup(keyboard))
                
    elif event_type == "rest":
        heal = random.randint(5, 12)
        state["hp"] = min(state.get("max_hp", 30), state.get("hp", 30) + heal)
        states = load_game_states()
        if states is None:
            states = {}
        states[user_id] = state
        save_game_states(states)
        
        keyboard = [[InlineKeyboardButton("🚪 ဆက်သွားမယ်", callback_data=f"dungeon_continue_{user_id}")]]
        msg = f"🛌 အနားယူဖို့နေရာကောင်းတွေ့တယ်။ အသက် {heal} ပြန်ကောင်းလာတယ်။\n❤️ HP: {state['hp']}/{state.get('max_hp', 30)}"
        if is_callback and target:
            await target.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await context.bot.send_message(chat_id=chat_id, text=msg, reply_markup=InlineKeyboardMarkup(keyboard))
            
    elif event_type == "merchant":
        keyboard = [
            [InlineKeyboardButton("🧪 ဆေးဝယ်မယ် (15ရွှေ)", callback_data=f"dungeon_buy_potion_{user_id}")],
            [InlineKeyboardButton("⚔️ တိုက်ခိုက်စာလိပ် (25ရွှေ)", callback_data=f"dungeon_buy_attack_{user_id}")],
            [InlineKeyboardButton("🚪 ဆက်သွားမယ်", callback_data=f"dungeon_continue_{user_id}")],
        ]
        msg = (
            f"🏪 *လှည့်လည်ကုန်သည်*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"💰 မင်းရဲ့ရွှေ: {state.get('gold', 0)}\n\n"
            f"📦 ပစ္စည်းများ:\n"
            f"🧪 အသက်ဆေး - 15ရွှေ (HP 10-20 ပြန်ကောင်း)\n"
            f"⚔️ တိုက်ခိုက်စာလိပ် - 25ရွှေ (တိုက်ခိုက်အား +2 အမြဲတမ်း)\n\n"
            f"🔄 ဝယ်ယူပြီးပါက 'ဆက်သွားမယ်' ကိုနှိပ်ပါ။"
        )
        if is_callback and target:
            await target.edit_message_text(msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))


def calculate_damage(attacker_attack, defender_defense, is_player=False):
    base_damage = max(1, attacker_attack - defender_defense)
    if is_player:
        return max(1, base_damage + random.randint(-2, 3))
    else:
        return max(1, base_damage + random.randint(-1, 2))