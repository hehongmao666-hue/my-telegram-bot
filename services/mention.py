# ==========================
# services/mention.py - 公告核心逻辑（V3.2 修复限流）
# ==========================

import asyncio
import random
import re
from typing import List, Dict, Any
from config import ANNOUNCE_DELAY, MENTION_BATCH_SIZE, MENTION_EMOJIS
from utils.logger import logger


def build_announcement_header(text: str) -> str:
    """构建公告头部消息"""
    return f"🔉 {text}"


def split_members(members: list, batch_size: int = MENTION_BATCH_SIZE) -> List[List[Dict]]:
    """将成员列表分批"""
    result = []
    for i in range(0, len(members), batch_size):
        result.append(members[i:i + batch_size])
    return result


def build_html_mentions(members: List[Dict]) -> str:
    """生成 HTML 格式的 @ 列表，每批随机排列 Emoji"""
    if not members:
        return ""

    shuffled_emojis = random.sample(MENTION_EMOJIS, len(MENTION_EMOJIS))
    emojis = shuffled_emojis[:len(members)]

    mentions = []
    for idx, member in enumerate(members):
        uid = member.get("id")
        if not uid:
            continue
        emoji = emojis[idx % len(emojis)]
        mentions.append(f'<a href="tg://user?id={uid}">{emoji}</a>')

    return " ".join(mentions)


def build_batch_message(batch_num: int, total_batches: int, mentions_html: str) -> str:
    """构建每批次的 @ 消息"""
    return f"📌 {batch_num}/{total_batches} {mentions_html}"


def build_finish_message(success: int, total: int, failed: int = 0, skipped: int = 0) -> str:
    """构建完成消息"""
    text = "✅ အကြောင်းကြားချက် ပို့ပြီးပါပြီ\n\n"
    if failed > 0 or skipped > 0:
        text += f"👥 Success : {success} / {total}\n"
        if failed > 0:
            text += f"❌ Failed : {failed}\n"
        if skipped > 0:
            text += f"⏭️ Skipped : {skipped}"
    else:
        text += f"👥 {success} / {total}"
    return text


async def send_mentions(
    context,
    chat_id: int,
    members: List[Dict],
    delay: float = 1.5,  # 改为 1.5 秒
    stop_flag: dict = None
) -> Dict[str, int]:
    """分批发送 @ 消息（支持立即停止）"""
    if not members:
        return {"success": 0, "failed": 0, "skipped": 0}

    batches = split_members(members, MENTION_BATCH_SIZE)
    total_batches = len(batches)

    stats = {"success": 0, "failed": 0, "skipped": 0}
    chat_key = str(chat_id)

    batch_data = []
    for idx, batch in enumerate(batches, 1):
        html = build_html_mentions(batch)
        if html:
            batch_data.append({
                "batch_num": idx,
                "total_batches": total_batches,
                "html": html,
                "count": len(batch)
            })
        else:
            stats["skipped"] += len(batch)

    if not batch_data:
        return stats

    logger.info(f"[Announcement] Total {len(batch_data)} batches, {len(members)} members")

    for data in batch_data:
        # 检查停止标志
        if stop_flag is not None and not stop_flag.get(chat_key, False):
            logger.info(f"[Announcement] Stopped by user at batch {data['batch_num']}")
            break

        msg = build_batch_message(
            data["batch_num"],
            data["total_batches"],
            data["html"]
        )

        # 重试逻辑（最多 3 次）
        max_retries = 3
        for attempt in range(max_retries):
            try:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=msg,
                    parse_mode="HTML",
                    disable_web_page_preview=True
                )
                stats["success"] += data["count"]
                logger.info(f"[Announcement] Batch {data['batch_num']}/{data['total_batches']} ({data['count']})")
                break

            except Exception as e:
                error_msg = str(e)
                if "FloodWait" in error_msg or "Too Many Requests" in error_msg or "RetryAfter" in error_msg:
                    wait_time = 5
                    match = re.search(r"(\d+)", error_msg)
                    if match:
                        wait_time = int(match.group(1)) + 2
                    logger.warning(f"[Announcement] FloodWait: waiting {wait_time}s (attempt {attempt+1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                    if attempt == max_retries - 1:
                        stats["failed"] += data["count"]
                        logger.error(f"[Announcement] Batch {data['batch_num']} failed after {max_retries} retries")
                else:
                    stats["failed"] += data["count"]
                    logger.error(f"[Announcement] Batch {data['batch_num']} failed: {e}")
                    break

        # 可中断的睡眠（每0.2秒检查一次停止标志）
        if delay > 0:
            sleep_steps = int(delay / 0.2)
            for _ in range(sleep_steps):
                if stop_flag is not None and not stop_flag.get(chat_key, False):
                    logger.info(f"[Announcement] Stopped during sleep at batch {data['batch_num']}")
                    return stats
                await asyncio.sleep(0.2)

    return stats