# ==========================
# game/callback.py - ဂိမ်းပြန်ခေါ်မှုများ (Dungeon အပါအဝင်)
# ==========================

import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from storage import load_game_states, save_game_states, get_player_state, load_data, save_data
from game.scenes import LEVELS, LEVEL_SCENES
from game.main import get_or_create_player, reset_player_game
from game.status import render_scene_with_send, handle_dungeon_event, calculate_damage
from utils.logger import log_action
from utils.helpers import get_user_info_from_query, is_game_owner
from utils.message import save_game_message, clear_game_messages


async def shop_callback(update, context):
    query = update.callback_query
    await query.answer()

    user_id = str(query.from_user.id)
    data = query.data
    chat_id = query.message.chat.id

    try:
        await query.delete_message()
    except Exception:
        pass

    if data == "shop_open":
        from game.status import game_shop
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
            await clear_game_messages(context, user_id, chat_id, keep_last=1)
            await render_scene_with_send(context, chat_id, current_scene, user_id)
        return

    if data.startswith("shop_buy_"):
        parts = data.split("_")
        if len(parts) >= 3:
            try:
                item_index = int(parts[2])
                owner_id = parts[3] if len(parts) > 3 else user_id

                if not is_game_owner(user_id, owner_id):
                    await query.answer("⛔️ ဒီဂိမ်းက မင်းရဲ့မဟုတ်ဘူး!", show_alert=True)
                    return

                items = context.user_data.get("shop_items", [])
                if item_index >= len(items):
                    await query.answer("❌ ပစ္စည်းမရှိတော့ပါ။", show_alert=True)
                    return

                item = items[item_index]
                price = item["price"]

                states = load_game_states()
                if states is None:
                    states = {}
                if user_id not in states:
                    await query.answer("❌ ဂိမ်းမစရသေးပါ။", show_alert=True)
                    return

                if states[user_id].get("gold", 0) < price:
                    await query.answer("💰 ရွှေမလုံလောက်ပါ!", show_alert=True)
                    return

                states[user_id]["gold"] -= price

                if item["type"] == "weapon":
                    states[user_id]["weapon"] = {"name": item["name"], "attack": item["attack"]}
                    msg = f"✅ {item['name']} ကိုဝယ်ယူပြီးပါပြီ! ⚔️+{item['attack']}"
                elif item["type"] == "armor":
                    states[user_id]["armor"] = {"name": item["name"], "defense": item["defense"]}
                    msg = f"✅ {item['name']} ကိုဝယ်ယူပြီးပါပြီ! 🛡️+{item['defense']}"
                else:
                    potions = states[user_id].get("potions", [])
                    potions.append({"name": item["name"], "heal": item["heal"]})
                    states[user_id]["potions"] = potions
                    msg = f"✅ {item['name']} ကိုဝယ်ယူပြီးပါပြီ! ❤️+{item['heal']}"

                save_game_states(states)
                await query.answer(msg, show_alert=True)
                await show_shop(query, context, user_id, chat_id)
            except Exception as e:
                await query.answer(f"❌ အမှားရှိသည်: {e}", show_alert=True)


async def show_shop(query, context, user_id, chat_id):
    state = get_player_state(user_id)
    if not state:
        await context.bot.send_message(chat_id=chat_id, text="❌ မင်းမှာ ဂိမ်းမရှိပါ။ /game နဲ့စပါ။")
        return

    from game.utils import generate_shop_items
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

    states = load_game_states()
    if states is not None and user_id in states:
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

        await clear_game_messages(context, user_id, chat_id)

        reset_player_game(user_id)
        states = load_game_states()
        if states is None:
            states = {}
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
            if states is None:
                states = {}
            states[user_id]["level"] = level
            states[user_id]["current_scene"] = scene_key
            save_game_states(states)

        states = load_game_states()
        if states is None:
            states = {}
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
            if states is None:
                states = {}
            states[user_id]["level"] = level
            states[user_id]["current_scene"] = scene_key
            states[user_id]["is_playing"] = True
            save_game_states(states)

        await render_scene_with_send(context, chat_id, scene_key, user_id)
        return


# ==========================
# Dungeon Callbacks
# ==========================

async def dungeon_callback(update, context):
    query = update.callback_query
    await query.answer()
    
    user_id = str(query.from_user.id)
    chat_id = query.message.chat.id
    data = query.data
    
    try:
        await query.delete_message()
    except Exception:
        pass
    
    state = get_player_state(user_id)
    if not state:
        await context.bot.send_message(chat_id=chat_id, text="❌ ကျေးဇူးပြု၍ /game ဖြင့် ဇာတ်ကောင်ဖန်တီးပါ။")
        return
    
    # dungeon_enter_from_game - 从游戏页面进入地牢
    if data.startswith("dungeon_enter_from_game_"):
        current_floor = context.user_data.get(f"dungeon_floor_{user_id}", 1)
        if current_floor > 1 and state.get("hp", 0) > 0:
            keyboard = [
                [InlineKeyboardButton("🚪 ဆက်လက်စူးစမ်းမယ်", callback_data=f"dungeon_continue_{user_id}")],
                [InlineKeyboardButton("🔄 အစကနေပြန်စမယ်", callback_data=f"dungeon_restart_{user_id}")],
                [InlineKeyboardButton("🔙 ဂိမ်းသို့ပြန်ရန်", callback_data="back_to_game")],
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
                f"⚡ မင်းရဲ့ခရီးကို ဆက်လက်ပါ။"
            )
            await context.bot.send_message(chat_id=chat_id, text=msg, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            context.user_data[f"dungeon_floor_{user_id}"] = 1
            state["hp"] = state.get("max_hp", 30)
            states = load_game_states()
            if states is None:
                states = {}
            states[user_id] = state
            save_game_states(states)
            keyboard = [[InlineKeyboardButton("🚪 မြေအောက်ခန်းထဲဝင်မယ်", callback_data=f"dungeon_explore_{user_id}")]]
            msg = "🏰 မြေအောက်ခန်းထဲ စူးစမ်းဖို့ အဆင်သင့်လား။"
            await context.bot.send_message(chat_id=chat_id, text=msg, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    # dungeon_explore
    if data.startswith("dungeon_explore_"):
        floor = context.user_data.get(f"dungeon_floor_{user_id}", 1)
        context.user_data[f"dungeon_floor_{user_id}"] = floor
        await handle_dungeon_event(chat_id, user_id, context, is_callback=False, target=None)
        return
    
    # dungeon_continue
    if data.startswith("dungeon_continue_"):
        floor = context.user_data.get(f"dungeon_floor_{user_id}", 1)
        context.user_data[f"dungeon_floor_{user_id}"] = floor + 1
        await handle_dungeon_event(chat_id, user_id, context, is_callback=False, target=None)
        return
    
    # dungeon_path - 地牢岔路选择
    if data.startswith("dungeon_path_"):
        parts = data.split("_")
        path_type = parts[2]
        user_id = parts[3]
        
        # 先删除原消息（避免编辑已删除的消息）
        try:
            await query.delete_message()
        except:
            pass
        
        if path_type == "combat":
            await handle_dungeon_event(chat_id, user_id, context, is_callback=False, target=None)
        elif path_type == "treasure":
            await handle_dungeon_event(chat_id, user_id, context, is_callback=False, target=None)
        elif path_type == "rest":
            state = get_player_state(user_id)
            if state:
                state["hp"] = min(state.get("max_hp", 30), state.get("hp", 30) + 15)
                states = load_game_states()
                if states is None:
                    states = {}
                states[user_id] = state
                save_game_states(states)
                keyboard = [[InlineKeyboardButton("🚪 ဆက်သွားမယ်", callback_data=f"dungeon_continue_{user_id}")]]
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"🛌 အနားယူပြီး HP +15 ပြန်ကောင်းလာတယ်!\n❤️ HP: {state['hp']}/{state.get('max_hp', 30)}",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )
        elif path_type == "merchant":
            await handle_dungeon_event(chat_id, user_id, context, is_callback=False, target=None)
        return
        
    # dungeon_attack
    if data.startswith("dungeon_attack_"):
        monster = context.user_data.get(f"dungeon_monster_{user_id}")
        if not monster:
            await context.bot.send_message(chat_id=chat_id, text="❌ ရန်သူမရှိပါ။")
            return
        
        attack = state.get("attack", 3) + (state.get("weapon", {}).get("attack", 0) if state.get("weapon") else 0)
        defense = state.get("defense", 1) + (state.get("armor", {}).get("defense", 0) if state.get("armor") else 0)
        
        player_damage = calculate_damage(attack, monster.get("defense", 1), is_player=True)
        monster["hp"] -= player_damage
        
        msg = f"⚔️ မင်း {monster['name']} ကို {player_damage} ထိခိုက်စေတယ်။\n"
        
        if monster["hp"] <= 0:
            exp_gain = monster.get("exp", 10) + random.randint(0, 3)
            gold_gain = random.randint(monster.get("gold_min", 3), monster.get("gold_max", 8))
            state["gold"] = state.get("gold", 0) + gold_gain
            
            from game.main import add_exp
            add_exp(user_id, exp_gain)
            
            floor = context.user_data.get(f"dungeon_floor_{user_id}", 1)
            context.user_data[f"dungeon_floor_{user_id}"] = floor + 1
            
            states = load_game_states()
            if states is None:
                states = {}
            states[user_id] = state
            save_game_states(states)
            
            keyboard = [[InlineKeyboardButton("🚪 ဆက်သွားမယ်", callback_data=f"dungeon_continue_{user_id}")]]
            
            boss_tag = "👑 BOSS " if monster.get("is_boss") else ""
            msg += (
                f"🎉 {boss_tag}{monster['name']} ကိုအနိုင်ရတယ်။\n"
                f"⭐ အတွေ့အကြုံ {exp_gain} ရတယ်၊ 💰 ရွှေ {gold_gain} ရတယ်။\n"
                f"❤️ ကျန်တဲ့ HP: {state['hp']}/{state.get('max_hp', 30)}"
            )
            await context.bot.send_message(chat_id=chat_id, text=msg, reply_markup=InlineKeyboardMarkup(keyboard))
            return
        
        monster_damage = calculate_damage(monster.get("attack", 5), defense, is_player=False)
        state["hp"] = max(0, state.get("hp", 30) - monster_damage)
        states = load_game_states()
        if states is None:
            states = {}
        states[user_id] = state
        save_game_states(states)
        
        msg += f"💢 {monster['name']} က မင်းကို {monster_damage} ပြန်ထိခိုက်စေတယ်။\n"
        msg += f"❤️ ကျန်တဲ့ HP: {state['hp']}/{state.get('max_hp', 30)}\n"
        msg += f"❤️ {monster['name']} HP: {monster['hp']}"
        
        if state["hp"] <= 0:
            keyboard = [[InlineKeyboardButton("🔄 ပြန်စမယ်", callback_data=f"dungeon_restart_{user_id}")]]
            msg += f"\n\n💀 မင်း {monster['name']} ဆီမှာ သေသွားပြီ။\nအထပ် {context.user_data.get(f'dungeon_floor_{user_id}', 1)} မှာ။"
            await context.bot.send_message(chat_id=chat_id, text=msg, reply_markup=InlineKeyboardMarkup(keyboard))
            return
        
        keyboard = [
            [InlineKeyboardButton("⚔️ တိုက်မယ်", callback_data=f"dungeon_attack_{user_id}")],
            [InlineKeyboardButton("🧪 ဆေးသုံးမယ်", callback_data=f"dungeon_potion_{user_id}")],
            [InlineKeyboardButton("🏃 ထွက်ပြေးမယ်", callback_data=f"dungeon_flee_{user_id}")],
        ]
        await context.bot.send_message(chat_id=chat_id, text=msg, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    # dungeon_potion
    if data.startswith("dungeon_potion_"):
        potions = state.get("potions", [])
        if not potions:
            keyboard = [
                [InlineKeyboardButton("🏃 ထွက်ပြေးမယ်", callback_data=f"dungeon_flee_{user_id}")],
                [InlineKeyboardButton("🔙 ပြန်သွားမယ်", callback_data=f"dungeon_continue_{user_id}")],
            ]
            await context.bot.send_message(chat_id=chat_id, text="❌ မင်းမှာ ဆေးမရှိဘူး။ ဈေးဆိုင်မှာဝယ်ပါ။", reply_markup=InlineKeyboardMarkup(keyboard))
            return
        
        if state.get("hp", 30) >= state.get("max_hp", 30):
            keyboard = [
                [InlineKeyboardButton("⚔️ တိုက်မယ်", callback_data=f"dungeon_attack_{user_id}")],
                [InlineKeyboardButton("🏃 ထွက်ပြေးမယ်", callback_data=f"dungeon_flee_{user_id}")],
            ]
            await context.bot.send_message(chat_id=chat_id, text="❌ မင်းရဲ့ HP ပြည့်နေပြီ။", reply_markup=InlineKeyboardMarkup(keyboard))
            return
        
        potion = potions.pop(0)
        heal = potion.get("heal", random.randint(10, 20))
        state["hp"] = min(state.get("max_hp", 30), state.get("hp", 30) + heal)
        state["potions"] = potions
        states = load_game_states()
        if states is None:
            states = {}
        states[user_id] = state
        save_game_states(states)
        
        monster = context.user_data.get(f"dungeon_monster_{user_id}")
        if monster:
            keyboard = [
                [InlineKeyboardButton("⚔️ တိုက်မယ်", callback_data=f"dungeon_attack_{user_id}")],
                [InlineKeyboardButton("🧪 ဆေးသုံးမယ်", callback_data=f"dungeon_potion_{user_id}")],
                [InlineKeyboardButton("🏃 ထွက်ပြေးမယ်", callback_data=f"dungeon_flee_{user_id}")],
            ]
            msg = f"🧪 {potion.get('name', 'ဆေး')} ကိုသုံးတယ်။ HP {heal} ပြန်ကောင်းလာတယ်။\n❤️ HP: {state['hp']}/{state.get('max_hp', 30)}"
            await context.bot.send_message(chat_id=chat_id, text=msg, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            keyboard = [[InlineKeyboardButton("🚪 ဆက်သွားမယ်", callback_data=f"dungeon_continue_{user_id}")]]
            await context.bot.send_message(chat_id=chat_id, text=f"🧪 HP {heal} ပြန်ကောင်းလာတယ်။", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    # dungeon_flee
    if data.startswith("dungeon_flee_"):
        if random.random() < 0.4:
            monster = context.user_data.get(f"dungeon_monster_{user_id}")
            if monster:
                defense = state.get("defense", 1) + (state.get("armor", {}).get("defense", 0) if state.get("armor") else 0)
                damage = calculate_damage(monster.get("attack", 5), defense, is_player=False)
                state["hp"] = max(0, state.get("hp", 30) - damage)
                states = load_game_states()
                if states is None:
                    states = {}
                states[user_id] = state
                save_game_states(states)
                
                if state["hp"] <= 0:
                    keyboard = [[InlineKeyboardButton("🔄 ပြန်စမယ်", callback_data=f"dungeon_restart_{user_id}")]]
                    msg = f"🏃 ထွက်ပြေးမအောင်မြင်။ {damage} ထိခိုက်တယ်။\n💀 မင်းသေသွားပြီ။"
                    await context.bot.send_message(chat_id=chat_id, text=msg, reply_markup=InlineKeyboardMarkup(keyboard))
                    return
                
                keyboard = [
                    [InlineKeyboardButton("⚔️ တိုက်မယ်", callback_data=f"dungeon_attack_{user_id}")],
                    [InlineKeyboardButton("🏃 ထပ်ပြေးမယ်", callback_data=f"dungeon_flee_{user_id}")],
                ]
                msg = f"🏃 ထွက်ပြေးမအောင်မြင်။ {damage} ထိခိုက်တယ်။\n❤️ HP: {state['hp']}/{state.get('max_hp', 30)}"
                await context.bot.send_message(chat_id=chat_id, text=msg, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            floor = context.user_data.get(f"dungeon_floor_{user_id}", 1)
            context.user_data[f"dungeon_floor_{user_id}"] = floor + 1
            keyboard = [[InlineKeyboardButton("🚪 ဆက်သွားမယ်", callback_data=f"dungeon_continue_{user_id}")]]
            msg = f"🏃 ထွက်ပြေးအောင်မြင်တယ်။\n❤️ HP: {state['hp']}/{state.get('max_hp', 30)}"
            await context.bot.send_message(chat_id=chat_id, text=msg, reply_markup=InlineKeyboardMarkup(keyboard))
        return
    
    # dungeon_restart
    if data.startswith("dungeon_restart_"):
        context.user_data[f"dungeon_floor_{user_id}"] = 1
        state["hp"] = state.get("max_hp", 30)
        states = load_game_states()
        if states is None:
            states = {}
        states[user_id] = state
        save_game_states(states)
        await context.bot.send_message(chat_id=chat_id, text="🔄 ပြန်စပါပြီ။ အထပ် 1 ကနေပြန်စတယ်။")
        await handle_dungeon_event(chat_id, user_id, context, is_callback=False, target=None)
        return
    
    # dungeon_buy_potion
    if data.startswith("dungeon_buy_potion_"):
        if state.get("gold", 0) < 15:
            keyboard = [
                [InlineKeyboardButton("🔙 ပြန်သွားမယ်", callback_data=f"dungeon_continue_{user_id}")],
            ]
            await context.bot.send_message(
                chat_id=chat_id, 
                text="❌ ရွှေမလုံလောက်ပါ။ 15 ရွှေလိုတယ်။\n\n🔄 ဆက်သွားရန် အောက်ပါခလုတ်ကိုနှိပ်ပါ။",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return
        
        state["gold"] = state.get("gold", 0) - 15
        potions = state.get("potions", [])
        potions.append({"name": "အသက်ဆေး", "heal": random.randint(10, 20)})
        state["potions"] = potions
        states = load_game_states()
        if states is None:
            states = {}
        states[user_id] = state
        save_game_states(states)
        
        keyboard = [
            [InlineKeyboardButton("🚪 ဆက်သွားမယ်", callback_data=f"dungeon_continue_{user_id}")],
        ]
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"🧪 ဝယ်ယူအောင်မြင်ပြီ။ အသက်ဆေးတစ်လုံးရတယ်။\n🧪 ဆေးအရေအတွက်: {len(state['potions'])} လုံး\n\n🔄 ဆက်သွားရန် အောက်ပါခလုတ်ကိုနှိပ်ပါ။",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return
    
    # dungeon_buy_attack
    if data.startswith("dungeon_buy_attack_"):
        if state.get("gold", 0) < 25:
            keyboard = [
                [InlineKeyboardButton("🔙 ပြန်သွားမယ်", callback_data=f"dungeon_continue_{user_id}")],
            ]
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ ရွှေမလုံလောက်ပါ။ 25 ရွှေလိုတယ်။\n\n🔄 ဆက်သွားရန် အောက်ပါခလုတ်ကိုနှိပ်ပါ။",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return
        
        state["gold"] = state.get("gold", 0) - 25
        state["attack"] = state.get("attack", 3) + 2
        states = load_game_states()
        if states is None:
            states = {}
        states[user_id] = state
        save_game_states(states)
        
        keyboard = [
            [InlineKeyboardButton("🚪 ဆက်သွားမယ်", callback_data=f"dungeon_continue_{user_id}")],
        ]
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"⚔️ ဝယ်ယူအောင်မြင်ပြီ။ တိုက်ခိုက်အား +2 အမြဲတမ်းတိုးတယ်။\n⚔️ လက်ရှိတိုက်ခိုက်အား: {state['attack']}\n\n🔄 ဆက်သွားရန် အောက်ပါခလုတ်ကိုနှိပ်ပါ။",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return