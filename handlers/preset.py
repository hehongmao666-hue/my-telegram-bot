# ==========================
# handlers/preset.py - 预设管理
# ==========================

from storage import load_presets, save_presets
from utils.helpers import owner_only
from handlers.broadcast import do_broadcast


async def preset(update, context):
    if not await owner_only(update):
        return
    args = context.args
    if not args:
        await update.message.reply_text("📝 အသုံးပြုပုံ:\n/preset list\n/preset save [အမည်] [စာသား]\n/preset delete [အမည်]\n/preset send [အမည်]")
        return
    action = args[0].lower()
    presets = load_presets()

    if action == "list":
        if not presets:
            await update.message.reply_text("📭 သိမ်းထားသောစာသားမရှိပါ။")
            return
        await update.message.reply_text("\n".join([f"📌 {k}" for k in presets.keys()]))

    elif action == "save":
        if len(args) < 3:
            await update.message.reply_text("📝 /preset save [အမည်] [စာသား]")
            return
        name = args[1]
        text = ' '.join(args[2:])
        presets[name] = text
        save_presets(presets)
        await update.message.reply_text(f"✅ '{name}' ကိုသိမ်းပြီးပါပြီ။")

    elif action == "delete":
        if len(args) < 2:
            await update.message.reply_text("📝 /preset delete [အမည်]")
            return
        name = args[1]
        if name in presets:
            del presets[name]
            save_presets(presets)
            await update.message.reply_text(f"✅ '{name}' ကိုဖျက်ပြီးပါပြီ။")
        else:
            await update.message.reply_text("❌ မတွေ့ပါ။")

    elif action == "send":
        if len(args) < 2:
            await update.message.reply_text("📝 /preset send [အမည်]")
            return
        name = args[1]
        if name in presets:
            await do_broadcast(update, context, presets[name], "text")
        else:
            await update.message.reply_text("❌ မတွေ့ပါ။")