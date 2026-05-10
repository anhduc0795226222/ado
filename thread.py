import asyncio, time, os

try:
    os.nice(5)
except Exception:
    pass

class RateLimiter:
    def __init__(self, max_rate_per_sec: float = 6.0):
        self.max_rate = max_rate_per_sec
        self.tokens = max_rate_per_sec
        self.last_time = time.monotonic()

    async def acquire(self, cost: float = 1.0):
        now = time.monotonic()
        elapsed = now - self.last_time
        self.last_time = now
        self.tokens = min(self.max_rate, self.tokens + elapsed * self.max_rate)
        if self.tokens < cost:
            wait = (cost - self.tokens) / self.max_rate
            await asyncio.sleep(wait)
            self.tokens = 0
        else:
            self.tokens -= cost

async def cooperative_sleep(i, every=10, delay=0.02):
    if i % every == 0:
        await asyncio.sleep(delay)

SEMAPHORE = asyncio.Semaphore(3)
GLOBAL_LIMITER = RateLimiter(max_rate_per_sec=8)

# > KẾT THÚC ĐOẠN CODE KÌM HÃM CPU

import aiohttp
import asyncio
import itertools
import sys
import gc
import os
import random
from datetime import datetime

THREADS_LOCK = asyncio.Lock()
user_thread_sessions = {}


def format_time(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    parts = []
    if d:
        parts.append(f"{d}d")
    if h:
        parts.append(f"{h}h")
    if m:
        parts.append(f"{m}m")
    parts.append(f"{s}s")
    return " ".join(parts)


async def show_typing_animation(duration, prefix=""):
    end_time = asyncio.get_event_loop().time() + duration
    for ch in itertools.cycle([".  ", ".. ", "..."]):
        if asyncio.get_event_loop().time() > end_time:
            break
        sys.stdout.write(f"\r{prefix}[Typing] Đang soạn{ch}")
        sys.stdout.flush()
        await asyncio.sleep(0.5)
    sys.stdout.write("\r" + " " * 60 + "\r")
    sys.stdout.flush()


def read_chude_file(path="nhay2.txt"):
    pairs = []
    if not os.path.exists(path):
        print(f"[WARN] Không tìm thấy file {path}")
        return pairs

    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            if "|" in line:
                title, content = line.split("|", 1)
                pairs.append((title.strip(), content.strip()))
            else:
                pairs.append((line, ""))

    if not pairs:
        print(f"[WARN] File {path} rỗng hoặc không có dòng hợp lệ!")
    else:
        print(f"[✅] Đã đọc {len(pairs)} dòng từ {path}")
    return pairs


async def thread_worker(
    token,
    channel_ids,
    delay,
    chude_pairs,
    color_prefix,
    semaphore,
    tag_user_ids=None,
    mode="message",
    threads_per_channel=5,
    messages_per_thread=10,
):
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    tag_user_ids = tag_user_ids or []

    async with aiohttp.ClientSession() as session:

        async def create_thread_and_messages(channel_id, t_index):
            await semaphore.acquire()
            try:
                await show_typing_animation(delay, prefix=color_prefix)

                thread_payload = {
                    "name": f"Thread-{t_index + 1}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
                    "auto_archive_duration": 1440,
                    "type": 11
                }

                async with session.post(
                    f"https://discord.com/api/v10/channels/{channel_id}/threads",
                    json=thread_payload,
                    headers=headers,
                    timeout=20
                ) as resp:
                    text = await resp.text()
                    if resp.status in (200, 201):
                        data = await resp.json()
                        thread_id = data.get("id")
                        print(f"{color_prefix}[✅] Tạo thread {thread_id} thành công trong channel {channel_id}")

                        if thread_id and mode == "message":
                            send_url = f"https://discord.com/api/v10/channels/{thread_id}/messages"
                            for i in range(messages_per_thread):
                                title_c, content_c = random.choice(chude_pairs) if chude_pairs else ("", "")
                                random_content = content_c or title_c or f"Nội dung #{i + 1}"
                                mention_text = " ".join([f"<@{uid}>" for uid in tag_user_ids])
                                final_content = f"{mention_text} {random_content}" if mention_text else random_content

                                async with session.post(
                                    send_url,
                                    json={"content": final_content},
                                    headers=headers,
                                    timeout=20
                                ) as send_resp:
                                    send_text = await send_resp.text()
                                    if send_resp.status in (200, 201):
                                        print(f"{color_prefix}[✅] Gửi tin {i + 1}/{messages_per_thread} vào thread {thread_id}")
                                    else:
                                        print(f"{color_prefix}[❌] Lỗi gửi {send_resp.status}: {send_text}")
                                await asyncio.sleep(delay)
                    else:
                        print(f"{color_prefix}[❌] Lỗi tạo thread {resp.status}: {text}")

            except asyncio.CancelledError:
                print(f"{color_prefix}[🛑] Worker bị hủy ở channel {channel_id}")
                raise
            except Exception as e:
                print(f"{color_prefix}[⚠️] Exception khi tạo thread: {e}")
                await asyncio.sleep(2)
                gc.collect()
            finally:
                semaphore.release()

        try:
            for t_index in range(threads_per_channel):
                tasks = [asyncio.create_task(create_thread_and_messages(cid, t_index)) for cid in channel_ids]
                await asyncio.gather(*tasks)
                await asyncio.sleep(delay)
        except asyncio.CancelledError:
            print(f"{color_prefix}[🛑] Toàn bộ worker bị hủy.")
        except Exception as e:
            print(f"{color_prefix}[⚠️] Exception tổng thể: {e}")
            await asyncio.sleep(2)
            gc.collect()

