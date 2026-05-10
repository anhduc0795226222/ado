import os
import sys
import time
import math
import signal
import multiprocessing
import threading

# CONFIG (thay đổi nếu cần)
TARGET_CPU_PERCENT = float(os.getenv("CPU_GUARD_TARGET_PERCENT", "10.0"))  # mục tiêu % CPU cho tiến trình (ví dụ 10.0)
CHECK_INTERVAL = float(os.getenv("CPU_GUARD_CHECK_INTERVAL", "1.0"))      # giãn cách đo CPU (giây)
RESUME_FACTOR = float(os.getenv("CPU_GUARD_RESUME_FACTOR", "0.75"))      # resume khi CPU < TARGET * RESUME_FACTOR
MAX_SUSPEND_SECONDS = float(os.getenv("CPU_GUARD_MAX_SUSPEND", "30"))    # tối đa suspend mỗi lần (giây)
MIN_SUSPEND_SECONDS = float(os.getenv("CPU_GUARD_MIN_SUSPEND", "0.05"))  # suspend tối thiểu mỗi lần (giây)
USE_PSUTIL = True

try:
    import psutil
except Exception:
    psutil = None
    USE_PSUTIL = False

def _get_num_cpus():
    try:
        return os.cpu_count() or 1
    except Exception:
        return 1

NUM_CPUS = _get_num_cpus()
PARENT_PID = os.getpid()

def _measure_process_cpu_percent_fallback(pid, interval):
    """
    Fallback khi không có psutil: đo CPU process dựa trên cpu_time delta.
    Trả về ước lượng % CPU (trên tất cả CPUs) trong khoảng interval giây.
    """
    try:
        # read proc times via time.process_time for current process only (works for current process)
        # but if pid != current pid, fallback fails; we only need fallback for current process.
        if pid != os.getpid():
            # không hỗ trợ đo pid khác nếu không có psutil
            return 0.0
        t0 = time.perf_counter()
        cpu0 = time.process_time()  # user+system CPU time for current process
        time.sleep(interval)
        t1 = time.perf_counter()
        cpu1 = time.process_time()
        wall = t1 - t0
        if wall <= 0:
            return 0.0
        cpu_delta = cpu1 - cpu0
        # process percent across all CPUs:
        percent = (cpu_delta / wall) * 100.0
        # clamp
        if percent < 0.0:
            percent = 0.0
        return percent
    except Exception:
        return 0.0

def _suspend_process_unix(pid):
    try:
        os.kill(pid, signal.SIGSTOP)
        return True
    except Exception:
        return False

def _resume_process_unix(pid):
    try:
        os.kill(pid, signal.SIGCONT)
        return True
    except Exception:
        return False

def _suspend_process_psutil(p_proc):
    try:
        p_proc.suspend()
        return True
    except Exception:
        return False

def _resume_process_psutil(p_proc):
    try:
        p_proc.resume()
        return True
    except Exception:
        return False

def _watchdog_main(target_percent=TARGET_CPU_PERCENT, check_interval=CHECK_INTERVAL,
                   resume_factor=RESUME_FACTOR, max_suspend=MAX_SUSPEND_SECONDS,
                   min_suspend=MIN_SUSPEND_SECONDS, pid=PARENT_PID):
    """
    Watchdog chạy trong child process: giám sát pid và suspend/resume khi cần.
    """
    use_ps = USE_PSUTIL and (psutil is not None)
    if use_ps:
        try:
            p = psutil.Process(pid)
        except Exception:
            p = None
            use_ps = False
    else:
        p = None

    target = float(target_percent)
    resume_threshold = target * float(resume_factor)
    # vòng lặp vô hạn, watchdog sẽ dừng khi tiến trình chính chết (PID không tồn tại)
    while True:
        try:
            # nếu tiến trình chính không còn tồn tại -> thoát watchdog
            if use_ps:
                if not p.is_running():
                    break
            else:
                # pid may vanish -> check
                try:
                    os.kill(pid, 0)
                except OSError:
                    break

            # đo CPU
            if use_ps:
                # psutil process.cpu_percent(interval) trả về % trong khoảng interval
                try:
                    usage = p.cpu_percent(interval=check_interval)
                except Exception:
                    # fallback: đo toàn bộ hệ thống CPU percent (ít chính xác cho process)
                    try:
                        usage = psutil.cpu_percent(interval=check_interval) / NUM_CPUS
                    except Exception:
                        usage = 0.0
            else:
                # fallback measure for current process only
                usage = _measure_process_cpu_percent_fallback(pid, check_interval)

            # clamp
            if usage is None:
                usage = 0.0
            try:
                usage = float(usage)
            except Exception:
                usage = 0.0

            # Nếu usage vượt target -> suspend tiến trình chính một thời gian ngắn
            if usage > target:
                # tính suspend time tỉ lệ với mức vượt
                # kiểu t_basic = min(max_suspend, check_interval * (usage/target - 1))
                # nhưng đảm bảo >= min_suspend
                try:
                    factor = max(0.1, (usage / target) - 1.0)
                except Exception:
                    factor = 1.0
                suspend_time = check_interval * min(max(1.0, factor), max(10.0))
                # clamp suspend_time trong [min_suspend, max_suspend]
                suspend_time = max(min_suspend, min(suspend_time, max_suspend))

                # suspend
                suspended = False
                if use_ps and p is not None:
                    suspended = _suspend_process_psutil(p)
                else:
                    # unix fallback
                    if hasattr(signal, "SIGSTOP"):
                        suspended = _suspend_process_unix(pid)
                    else:
                        suspended = False

                if suspended:
                    # ngủ ở watchdog — tiến trình chính bị tạm dừng trong thời gian này
                    # Tuy nhiên nếu usage quá lớn, chúng ta sẽ resume sớm hơn khi sleep ngắn
                    time.sleep(suspend_time)
                    # resume
                    resumed = False
                    if use_ps and p is not None:
                        resumed = _resume_process_psutil(p)
                    else:
                        if hasattr(signal, "SIGCONT"):
                            resumed = _resume_process_unix(pid)
                        else:
                            resumed = False
                    # sau resume, chờ một khoảng nhỏ để cho tiến trình chính làm việc rồi tiếp tục loop
                    time.sleep(max(0.01, check_interval * 0.1))
                else:
                    # Nếu không thể suspend (ví dụ Windows không có psutil), ta fallback bằng cách sleep lâu hơn tại watchdog
                    # (không thể tạm dừng tiến trình chính - nên ít hiệu quả)
                    time.sleep(min(suspend_time, max(1.0, check_interval)))
            else:
                # nếu CPU < target, chờ tiếp
                # thêm sleep ngắn để không busy loop
                time.sleep(max(0.01, check_interval * 0.5))
        except Exception:
            # tránh crash watchdog; nếu có lỗi, chờ rồi tiếp tục; nếu lỗi ko hồi phục, break sau vài lần
            try:
                time.sleep(1.0)
            except Exception:
                break

def _start_watchdog_subprocess():
    """
    Khởi chạy watchdog như một tiến trình tách biệt (child) để có thể suspend/resume process chính.
    Gọi hàm này khi import module / dán đoạn mã này lên file.
    """
    # Nếu biến môi trường CPU_GUARD_DISABLE đặt =1 thì không khởi watchdog
    if os.getenv("CPU_GUARD_DISABLE", "0") == "1":
        return None

    # Cấu hình từ env (nếu muốn override nhanh)
    try:
        tgt = float(os.getenv("CPU_GUARD_TARGET_PERCENT", str(TARGET_CPU_PERCENT)))
    except Exception:
        tgt = TARGET_CPU_PERCENT
    try:
        chk = float(os.getenv("CPU_GUARD_CHECK_INTERVAL", str(CHECK_INTERVAL)))
    except Exception:
        chk = CHECK_INTERVAL
    try:
        rf = float(os.getenv("CPU_GUARD_RESUME_FACTOR", str(RESUME_FACTOR)))
    except Exception:
        rf = RESUME_FACTOR
    try:
        ms = float(os.getenv("CPU_GUARD_MAX_SUSPEND", str(MAX_SUSPEND_SECONDS)))
    except Exception:
        ms = MAX_SUSPEND_SECONDS
    try:
        mins = float(os.getenv("CPU_GUARD_MIN_SUSPEND", str(MIN_SUSPEND_SECONDS)))
    except Exception:
        mins = MIN_SUSPEND_SECONDS

    # Start a separate process (child) running watchdog. Use multiprocessing.Process to be portable.
    p = multiprocessing.Process(
        target=_watchdog_main,
        args=(tgt, chk, rf, ms, mins, PARENT_PID),
        daemon=False
    )
    p.start()
    # Return process object in case caller wants to keep reference
    return p

# Start watchdog immediately on import
try:
    _cpu_guard_watchdog_process = _start_watchdog_subprocess()
except Exception:
    _cpu_guard_watchdog_process = None

# Optional: provide small API to interact (if user wants)
def cpu_guard_get_watchdog_proc():
    return globals().get("_cpu_guard_watchdog_process")

def cpu_guard_stop_watchdog():
    try:
        p = cpu_guard_get_watchdog_proc()
        if p is not None and p.is_alive():
            p.terminate()
            p.join(timeout=2)
            return True
    except Exception:
        pass
    return False

# ================ end CPU GUARD ================


import aiohttp
import asyncio
import os
import wave
import struct
from datetime import datetime

BASE_API = "https://discord.com/api/v10"
AUDIO_PATH = os.path.join(os.path.dirname(__file__), "BuiTuanManh.mp3")


def create_blank_audio():
    """Tự tạo file Bui Tuan Manh.mp3 (0.5s im lặng) nếu chưa có."""
    if os.path.exists(AUDIO_PATH):
        return
    with wave.open(AUDIO_PATH, "w") as wf:
        wf.setnchannels(1)    
        wf.setsampwidth(2)     
        wf.setframerate(44100)  
        frames = [struct.pack('<h', 0) for _ in range(int(44100 * 0.5))]
        wf.writeframes(b"".join(frames))
    print(f"[🎧] Đã tạo file audio rỗng: {AUDIO_PATH}")


async def send_blank_audio(token: str, channel_id: str, retries: int = 3):
    """Gửi file audio rỗng (Bui Tuan Manh.mp3) vào channel Discord bằng user token."""
    create_blank_audio()
    async with aiohttp.ClientSession() as session:
        for attempt in range(retries):
            with open(AUDIO_PATH, "rb") as f:
                form = aiohttp.FormData()
                form.add_field("file", f, filename="BuiTuanManh.mp3", content_type="audio/mpeg")

                headers = {"Authorization": token}

                async with session.post(
                    f"{BASE_API}/channels/{channel_id}/messages",
                    data=form,
                    headers=headers
                ) as resp:
                    if resp.status in (200, 201):
                        print(f"[✅] Đã gửi audio vào kênh {channel_id} lúc {datetime.now().strftime('%H:%M:%S')}")
                        return await resp.json()

                    elif resp.status == 429:
                        data = await resp.json()
                        retry_after = float(data.get("retry_after", 5))
                        print(f"[⏳] Rate-limit, chờ {retry_after:.2f}s...")
                        await asyncio.sleep(retry_after)

                    else:
                        text = await resp.text()
                        print(f"[❌] Gửi lỗi {resp.status}: {text}")
                        await asyncio.sleep(1.5)

        print("[⚠️] Hết số lần thử, gửi thất bại.")
        return None

if __name__ == "__main__":
    async def _test():
        token = input("Nhập user token: ").strip()
        channel = input("Nhập channel id: ").strip()
        await send_blank_audio(token, channel)

    asyncio.run(_test())
