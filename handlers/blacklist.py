# ==========================
# handlers/blacklist.py - 黑名单
# ==========================

from storage import load_data, save_data
from utils.helpers import owner_only


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