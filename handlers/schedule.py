# ==========================
# handlers/schedule.py - 定时任务
# ==========================

import time
import re
from datetime import datetime
from storage import load_schedule, save_schedule
from utils.helpers import owner_only


async def at(update, context):
    if not await owner_only(update):
        return
    args = context.args
    if len(args) < 3:
        await update.message.reply_text("📅 အသုံးပြုပုံ: /at [YYYY-MM-DD HH:MM] [စာသား]\nဥပမာ: /at 2026-12-31 23:59 နှစ်သစ်ကူးမင်္ဂလာပါ!")
        return
    try:
        dt_str = f"{args[0]} {args[1]}"
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
        text = ' '.join(args[2:])
        schedule = load_schedule()
        schedule.append({
            "id": int(time.time()),
            "time": dt.timestamp(),
            "text": text,
            "type": "text"
        })
        save_schedule(schedule)
        await update.message.reply_text(f"✅ {dt_str} တွင် ပို့ရန် သိမ်းပြီးပါပြီ။\nစာသား: {text}")
    except Exception as e:
        await update.message.reply_text(f"❌ အမှားရှိသည်: {e}")


async def in_(update, context):
    if not await owner_only(update):
        return
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("⏰ အသုံးပြုပုံ: /in [30s/5m/2h] [စာသား]")
        return
    try:
        delay_str = args[0]
        match = re.match(r"(\d+)(s|m|h)", delay_str)
        if not match:
            await update.message.reply_text("❌ ပုံစံမှားသည်။ ဥပမာ: 30s, 5m, 2h")
            return
        val, unit = int(match.group(1)), match.group(2)
        seconds = val * {"s": 1, "m": 60, "h": 3600}[unit]
        text = ' '.join(args[1:])
        schedule = load_schedule()
        schedule.append({
            "id": int(time.time()),
            "time": time.time() + seconds,
            "text": text,
            "type": "text"
        })
        save_schedule(schedule)
        await update.message.reply_text(f"✅ {delay_str} အတွင်းပို့ရန် သိမ်းပြီးပါပြီ။\nစာသား: {text}")
    except Exception as e:
        await update.message.reply_text(f"❌ အမှားရှိသည်: {e}")


async def list_schedule(update, context):
    if not await owner_only(update):
        return
    sched = load_schedule()
    if not sched:
        await update.message.reply_text("📭 အချိန်မှန်ပို့ရန် သိမ်းထားခြင်းမရှိပါ။")
        return
    lines = []
    for item in sched:
        dt = datetime.fromtimestamp(item["time"]).strftime("%Y-%m-%d %H:%M")
        lines.append(f"ID: {item['id']} | {dt} | {item['text'][:30]}...")
    await update.message.reply_text("\n".join(lines))


async def cancel_schedule(update, context):
    if not await owner_only(update):
        return
    if not context.args:
        await update.message.reply_text("📝 အသုံးပြုပုံ: /cancel_schedule [id]")
        return
    try:
        sid = int(context.args[0])
        sched = load_schedule()
        new_sched = [s for s in sched if s["id"] != sid]
        if len(new_sched) == len(sched):
            await update.message.reply_text("❌ ID မတွေ့ပါ။")
            return
        save_schedule(new_sched)
        await update.message.reply_text(f"✅ Schedule ID {sid} ကိုဖျက်ပြီးပါပြီ။")
    except Exception as e:
        await update.message.reply_text(f"❌ အမှားရှိသည်: {e}")