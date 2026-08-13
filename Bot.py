# ==========================
# bot.py - 入口文件（地牢升级版 + 排行榜 + 签到 + Help升级）
# ==========================

import asyncio
import time
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config import TOKEN, OWNER_ID
from storage import load_data, load_schedule, save_schedule, save_data
from utils.logger import logger

# ============ Handlers ============
from handlers.start import (
    start, help, stats, count,
    help_game_callback,
    help_leaderboard_callback,
    help_announce_callback,
    help_about_callback,
    help_back_callback
)
from handlers.broadcast import send, broadcast, broadcast_image, broadcast_group, broadcast_user, forward, forward_all
from handlers.schedule import at, in_, list_schedule, cancel_schedule
from handlers.preset import preset
from handlers.blacklist import blacklist, cancel
from handlers.announce import (
    announce,
    stop_announce,
    announce_callback,
    already_subscribed_callback,
)

# ============ Services ============
from services.link import random_link_callback, back_to_menu_callback
from services.active_member import active_member_listener

# ============ Game ============
from game.main import game_start, game_restart, game_back, dungeon_start, daily_checkin
from game.status import game_status, game_shop
from game.callback import shop_callback, game_callback, dungeon_callback
from game.leaderboard import leaderboard, leaderboard_refresh_callback


# ============ Check Schedule ============
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


# ============ Main ============
def main():
    print("🔵 Script started...")
    print("📌 Entering main()...")

    app = Application.builder().token(TOKEN).build()

    print("📌 Application built successfully...")

    # ============ Commands ============
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

    # ============ RPG ============
    app.add_handler(CommandHandler("game", game_start))
    app.add_handler(CommandHandler("restartgame", game_restart))
    app.add_handler(CommandHandler("back", game_back))
    app.add_handler(CommandHandler("status", game_status))
    app.add_handler(CommandHandler("shop", game_shop))

    # ============ Dungeon Mode ============
    app.add_handler(CommandHandler("dungeon", dungeon_start))

    # ============ Leaderboard & Checkin ============
    app.add_handler(CommandHandler("leaderboard", leaderboard))
    app.add_handler(CommandHandler("checkin", daily_checkin))

    # ============ Announcement ============
    app.add_handler(CommandHandler("announce", announce))
    app.add_handler(CommandHandler("stop_announce", stop_announce))

    # ============ Callback Query ============
    app.add_handler(CallbackQueryHandler(random_link_callback, pattern="^random_link$"))
    app.add_handler(CallbackQueryHandler(back_to_menu_callback, pattern="^back_to_menu$"))
    app.add_handler(CallbackQueryHandler(game_callback, pattern="^game_"))
    app.add_handler(CallbackQueryHandler(game_callback, pattern="^restart_"))
    app.add_handler(CallbackQueryHandler(game_callback, pattern="^level_"))
    app.add_handler(CallbackQueryHandler(shop_callback, pattern="^shop_"))
    app.add_handler(CallbackQueryHandler(shop_callback, pattern="^back_to_game$"))
    app.add_handler(CallbackQueryHandler(shop_callback, pattern="^shop_open$"))
    
    # ============ Dungeon Callbacks ============
    app.add_handler(CallbackQueryHandler(dungeon_callback, pattern="^dungeon_"))
    
    # ============ Leaderboard Callbacks ============
    app.add_handler(CallbackQueryHandler(leaderboard_refresh_callback, pattern="^leaderboard_refresh$"))
    
    # ============ Help Callbacks ============
    app.add_handler(CallbackQueryHandler(help_game_callback, pattern="^help_game$"))
    app.add_handler(CallbackQueryHandler(help_leaderboard_callback, pattern="^help_leaderboard$"))
    app.add_handler(CallbackQueryHandler(help_announce_callback, pattern="^help_announce$"))
    app.add_handler(CallbackQueryHandler(help_about_callback, pattern="^help_about$"))
    app.add_handler(CallbackQueryHandler(help_back_callback, pattern="^help_back$"))
    
    # ============ Announcement Callbacks ============
    app.add_handler(CallbackQueryHandler(announce_callback, pattern="^announce_"))
    app.add_handler(CallbackQueryHandler(announce_callback, pattern="^announce_subscribe_"))
    app.add_handler(CallbackQueryHandler(already_subscribed_callback, pattern="^already_subscribed$"))

    # ============ Active Member System ============
    app.add_handler(
        MessageHandler(
            filters.ALL & ~filters.StatusUpdate.ALL,
            active_member_listener,
        ),
        group=99,
    )

    print("✅ All handlers loaded.")
    print("🚀 Myanmar Community Manager Bot Started")
    print("📊 Loaded commands. Owner-only functions active.")
    print("🎮 /dungeon - 地牢探险模式已加载！")
    print("🏆 /leaderboard - 排行榜已加载！")
    print("✅ /checkin - 每日签到已加载！")
    print("ℹ️ /help - 升级版帮助菜单已加载！")

    # 启动后台任务
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(check_schedule(app))

    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()