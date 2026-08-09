# ==========================
# utils/message.py - 消息管理（修复版）
# ==========================

from storage import load_game_states, save_game_states

def save_game_message(user_id, chat_id, message_id):
    """保存游戏消息ID"""
    states = load_game_states()
    if states is None:
        states = {}
    if user_id not in states:
        states[user_id] = {}
    if "game_messages" not in states[user_id]:
        states[user_id]["game_messages"] = []
    if message_id not in states[user_id]["game_messages"]:
        states[user_id]["game_messages"].append(message_id)
        # 只保留最近50条
        states[user_id]["game_messages"] = states[user_id]["game_messages"][-50:]
        save_game_states(states)

async def clear_game_messages(context, user_id, chat_id, keep_last=0):
    """清除游戏消息"""
    states = load_game_states()
    if states is None:
        return
    
    if user_id not in states:
        return
    
    messages = states[user_id].get("game_messages", [])
    if not messages:
        return
    
    # 保留最后几条
    if keep_last > 0:
        to_delete = messages[:-keep_last]
    else:
        to_delete = messages[:]
    
    for msg_id in to_delete:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
        except Exception:
            pass
    
    # 更新消息列表
    if keep_last > 0:
        states[user_id]["game_messages"] = messages[-keep_last:]
    else:
        states[user_id]["game_messages"] = []
    save_game_states(states)