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

import os
import re
import gc
import sys
import time
import json
import base64
import random
import string
import asyncio
import threading
import itertools
import smtplib
import ssl
import requests
from io import BytesIO
from enum import Enum
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from textwrap import shorten
from typing import Dict, Any

import discord
from discord.ext import commands, tasks
from discord import app_commands
from discord.ui import View, Button

from anhmess import NanhMessenger
from tooldsbox import get_thread_list
from instagrapi import Client
from toolnamebox import dataGetHome, tenbox
from colorama import Fore
from Crypto.Cipher import AES
from spm import *



async def send_msg(bot, channelid, msg):
    """Gửi tin nhắn bằng discord.py thay vì requests"""
    channel = bot.get_channel(int(channelid))
    if channel:
        await channel.send(msg)


async def faketyping_discord(bot, channelid, duration: int = 3):
    """Giả typing trong kênh an toàn với discord.py"""
    channel = bot.get_channel(int(channelid))
    if channel:
        async with channel.typing():
            await asyncio.sleep(duration)


async def safe_send(interaction: discord.Interaction, message: str, ephemeral: bool = True):
    """Gửi tin nhắn an toàn (tránh lỗi Unknown Interaction)"""
    try:
        if not interaction.response.is_done():
            await interaction.response.send_message(message, ephemeral=ephemeral)
        else:
            await interaction.followup.send(message, ephemeral=ephemeral)
    except discord.NotFound:
        print("[WARN] Interaction expired")


def format_time(seconds: int) -> str:
    """Chuyển số giây thành chuỗi dễ đọc: d, h, m, s"""
    try:
        seconds = int(seconds)
    except Exception:
        return "0s"

    days, rem = divmod(seconds, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, secs = divmod(rem, 60)

    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if secs or not parts:
        parts.append(f"{secs}s")
    return " ".join(parts)


def check_task_limit(folder: str = "data") -> int:
    if not os.path.exists(folder):
        os.makedirs(folder)
    return len(os.listdir(folder))

def safe_thread_wrapper(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except Exception as e:
        print(f"[ERROR] Task bị lỗi: {e}")

import random, hashlib, json, time, requests

class facebook:
    def __init__(self, cookie):
        self.cookie = cookie
        self.user_id = re.search(r"c_user=(\d+)", cookie).group(1)
        self.fb_dtsg, self.rev, self.jazoest = self._fetch_tokens()

    def _fetch_tokens(self):
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Cookie": self.cookie
        }
        r = requests.get("https://www.facebook.com/", headers=headers)
        fb_dtsg = re.search(r'name="fb_dtsg" value="(.*?)"', r.text).group(1)
        rev = re.search(r'"client_revision":(\d+),', r.text).group(1)
        jazoest = re.search(r'name="jazoest" value="(\d+)"', r.text).group(1)
        return fb_dtsg, rev, jazoest


def fbTools(config):
    return {
        "FacebookID": config.get("FacebookID"),
        "fb_dtsg": config.get("fb_dtsg"),
        "clientRevision": config.get("clientRevision"),
        "jazoest": config.get("jazoest"),
        "cookieFacebook": config.get("cookieFacebook")
    }


def generate_offline_threading_id():
    ret = int(random.random() * 2**31)
    time_sec = int(time.time())
    return str((ret << 32) | time_sec)


class MessageSender:
    def __init__(self, fbTools, config, fb):
        self.fbTools = fbTools
        self.config = config
        self.fb = fb
        self.ws_req_number = 1
        self.ws_task_number = 1
        self.mqtt = None  # sẽ connect sau

    def get_last_seq_id(self):
        return 0

    def connect_mqtt(self):
        # trong botv21 dùng lib paho-mqtt để connect
        try:
            import paho.mqtt.client as mqtt
        except ImportError:
            print("[ERROR] Thiếu thư viện paho-mqtt, hãy cài: pip install paho-mqtt")
            return False

        def on_connect(client, userdata, flags, rc):
            print("[MQTT] Connected with result code", rc)

        client = mqtt.Client()
        client.on_connect = on_connect
        try:
            client.connect("edge-mqtt.facebook.com", 443)
            client.loop_start()
            self.mqtt = client
            return True
        except Exception as e:
            print("[MQTT] Không connect được:", e)
            return False

    def stop(self):
        if self.mqtt:
            self.mqtt.loop_stop()
            self.mqtt.disconnect()

# ================= HÀM CHẠY TASK SPAM POLL MESSENGER =================
def start_nhay_poll_func(cookie, idbox, delay, folder_id):
    while True:
        if os.path.exists(f"data/{folder_id}/stop.txt"):
            print(f"[STOP] Task {folder_id} đã dừng.")
            break

        try:
            payload = {
                "av": cookie.split("c_user=")[1].split(";")[0],
                "fb_api_caller_class": "RelayModern",
                "fb_api_req_friendly_name": "MessengerGroupPollCreateMutation",
                "variables": json.dumps({
                    "input": {
                        "source": "chat_poll",
                        "question_text": "Bạn thích gì?",
                        "options": [{"text": "Có"}, {"text": "Không"}],
                        "target_id": idbox,
                        "actor_id": cookie.split("c_user=")[1].split(";")[0],
                        "client_mutation_id": str(random.randint(100000, 999999))
                    }
                }),
                "doc_id": "5066134243453369"
            }

            headers = {
                "User-Agent": "Mozilla/5.0",
                "Content-Type": "application/x-www-form-urlencoded",
                "Cookie": cookie
            }

            res = requests.post("https://www.facebook.com/api/graphql/", data=payload, headers=headers)
            if res.status_code == 200:
                print(f"[✓] Gửi poll vào box {idbox}")
            else:
                print(f"[×] Lỗi gửi poll ({res.status_code}): {res.text[:100]}")

        except Exception as e:
            print(f"[!] Lỗi khi gửi poll: {e}")

        time.sleep(int(delay))



functions = [
    send_otp_via_sapo, send_otp_via_viettel, send_otp_via_medicare, send_otp_via_tv360,
    send_otp_via_dienmayxanh, send_otp_via_kingfoodmart, send_otp_via_mocha, send_otp_via_fptdk,
    send_otp_via_fptmk, send_otp_via_VIEON, send_otp_via_ghn, send_otp_via_lottemart,
    send_otp_via_DONGCRE, send_otp_via_shopee, send_otp_via_TGDD, send_otp_via_fptshop,
    send_otp_via_WinMart, send_otp_via_vietloan, send_otp_via_lozi, send_otp_via_F88,
    send_otp_via_spacet, send_otp_via_vinpearl, send_otp_via_traveloka, send_otp_via_dongplus,
    send_otp_via_longchau, send_otp_via_longchau1, send_otp_via_galaxyplay, send_otp_via_emartmall,
    send_otp_via_ahamove, send_otp_via_ViettelMoney, send_otp_via_xanhsmsms, send_otp_via_xanhsmzalo,
    send_otp_via_popeyes, send_otp_via_ACHECKIN, send_otp_via_APPOTA, send_otp_via_Watsons,
    send_otp_via_hoangphuc, send_otp_via_fmcomvn, send_otp_via_Reebokvn, send_otp_via_thefaceshop,
    send_otp_via_BEAUTYBOX, send_otp_via_winmart, send_otp_via_medicare, send_otp_via_futabus,
    send_otp_via_ViettelPost, send_otp_via_myviettel2, send_otp_via_myviettel3, send_otp_via_TOKYOLIFE,
    send_otp_via_30shine, send_otp_via_Cathaylife, send_otp_via_dominos, send_otp_via_vinamilk,
    send_otp_via_vietloan2, send_otp_via_batdongsan, send_otp_via_GUMAC, send_otp_via_mutosi,
    send_otp_via_mutosi1, send_otp_via_vietair, send_otp_via_FAHASA, send_otp_via_hopiness,
    send_otp_via_modcha35, send_otp_via_Bibabo, send_otp_via_MOCA, send_otp_via_pantio,
    send_otp_via_Routine, send_otp_via_vayvnd, send_otp_via_tima, send_otp_via_moneygo,
    send_otp_via_takomo, send_otp_via_paynet, send_otp_via_pico, send_otp_via_PNJ, send_otp_via_TINIWORLD
]

            
print("N G U Y Ễ N M I N H Q U Â N 𝐨𝐧 𝐭𝐨𝐩 𝐰𝐚𝐫\n điều anh muốn là luôn thấy em cười nhưng cười với anh chứ em cười với thằng khác thì anh chôn em cùng thằng đó xuống diêm la âm phủ mà hú hí với nhau\n\n MUSIC:\n anh yêu em nhiều lắm nhưng em đâu nào hay\n trong cơn say triền miên em gọi nhầm anh với ai\n nhường em đi cho người khác cũng là cách anh hạnh phúc\n kết thúc thôi ! \n anh ổn mà \n\n anh đã rất mạnh mẽ để cố gắng quên em rồi\n anh thực sự yêu em nhưng chỉ là quá khứ thôi\n từng van xin em đừng đi vậy giờ thì anh khước từ !\n giá như đời làm gì có giá như !!!")            
TOKEN = input("        Token bot của bạn: ").strip()
ADMIN_IDS = input("        ID Admin chính: ").split(",")
ADMIN_IDS = [aid.strip() for aid in ADMIN_IDS]


INTENTS = discord.Intents.default()
INTENTS.members = True

bot = commands.Bot(command_prefix="/", intents=INTENTS)
tree = bot.tree

DATA_FILE = "users.json"
NGONMESS_DIR = "ngonmess_data"
os.makedirs(NGONMESS_DIR, exist_ok=True)
user_tabs = {}
user_nhay_tabs = {}
nhaynameboxzl_tabs = {}
user_zalo_tabs = {}
user_sticker_tabs = {}
TREOSTICKER_LOCK = threading.Lock()
ZALO_LOCK = threading.Lock()
NHAYTAGZALO_LOCK = threading.Lock()
user_nhaytagzalo_tabs = {}
TAB_LOCK = threading.Lock()
user_poll_tabs = {}
POLL_LOCK = threading.Lock()
user_image_tabs = {}
IMAGE_TAB_LOCK = threading.Lock()
user_nhaymess_tabs = {}
NHAY_LOCK = threading.Lock()
user_discord_tabs = {}
DIS_LOCK = asyncio.Lock()
user_nhaydis_tabs = {}  
NHAYDIS_LOCK = asyncio.Lock()
user_treotele_tabs = {}   
TREOTELE_LOCK = threading.Lock()
SPAM_TASKS = {}  
TREOSMS_TASKS = {}
TREOSMS_LOCK = threading.Lock()
IG_LOCK = threading.Lock()
user_treogmail_tabs = {}
user_nhaynamebox_tabs = {}
NHAYNAMEBOX_LOCK = threading.Lock()
TREOSMS_TASKS = {}
user_reostr_tabs = {}
TREOSMS_LOCK = threading.Lock()
TREOGMAIL_LOCK = threading.Lock()
user_nhaytag_tabs = {}
NHAYTAG_LOCK = threading.Lock()


if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def load_users():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_users(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def is_admin(interaction: discord.Interaction):
    return str(interaction.user.id) in ADMIN_IDS

def is_authorized(interaction: discord.Interaction):
    users = load_users()
    uid = str(interaction.user.id)
    if uid in users:
        exp = users[uid]
        if exp is None:
            return True
        elif datetime.fromisoformat(exp) > datetime.now():
            return True
        else:            
            _remove_user_and_kill_tabs(uid)
    return False

def _add_user(uid: str, days: int = None):
    users = load_users()
    if days:
        expire_time = (datetime.now() + timedelta(days=days)).isoformat()
        users[uid] = expire_time
    else:
        users[uid] = None
    save_users(users)

def _remove_user_and_kill_tabs(uid: str):
    users = load_users()
    if uid in users:
        del users[uid]
        save_users(users)
    with TAB_LOCK:
        if uid in user_tabs:
            for tab in user_tabs[uid]:
                tab["stop_event"].set()
            del user_tabs[uid]

def _get_user_list():
    users = load_users()
    result = []
    for uid, exp in users.items():
        if exp:
            remaining = datetime.fromisoformat(exp) - datetime.now()
            if remaining.total_seconds() <= 0:
                continue  
            days = remaining.days
            hours, rem = divmod(remaining.seconds, 3600)
            minutes, _ = divmod(rem, 60)
            time_str = f"{days} ngày, {hours} giờ, {minutes} phút"
            result.append((uid, time_str))
        else:
            result.append((uid, "vĩnh viễn"))
    return result
    
def extract_facebook_post_id(link):
    match = re.search(r"fbid=(\d+)", link)
    if not match:
        match = re.search(r"/posts/(\d+)", link)
    if not match:
        match = re.search(r"/videos/(\d+)", link)
    if not match:
        match = re.search(r"/permalink/(\d+)", link)
    return match.group(1) if match else None

def get_token(cookie):
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'cache-control': 'max-age=0',
        'cookie': cookie,
        'dpr': '1',
        'priority': 'u=0, i',
        'sec-ch-prefers-color-scheme': 'light',
        'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'sec-ch-ua-full-version-list': '"Google Chrome";v="125.0.6422.78", "Chromium";v="125.0.6422.78", "Not.A/Brand";v="24.0.0.0"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-model': '""',
        'sec-ch-ua-platform': '"Windows"',
        'sec-ch-ua-platform-version': '"10.0.0"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'viewport-width': '868',
    }

    try:
        response = requests.get('https://business.facebook.com/content_management', headers=headers).text
        token = response.split('[{"accessToken":"')[1].split('","')[0]
        return token
    except Exception as e:
        print(f'\033[1;31mLấy Token Thất Bại')
        return None

def check_login_facebook(cookie):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Cookie": cookie
        }
        res = requests.get("https://mbasic.facebook.com/profile.php", headers=headers)
        name_match = re.search(r'<title>(.*?)</title>', res.text)
        uid_match = re.search(r'c_user=(\d+)', cookie)
        fb_dtsg = re.search(r'name="fb_dtsg" value="(.*?)"', res.text)
        jazoest = re.search(r'name="jazoest" value="(.*?)"', res.text)

        if "login" in res.url or not uid_match:
            return None
        return (
            name_match.group(1) if name_match else "No Name",
            fb_dtsg.group(1) if fb_dtsg else "",
            jazoest.group(1) if jazoest else "",
            uid_match.group(1)
        )
    except:
        return None

def auto_cmt_moi_ne(token, idpost, noidung, image_url, cookie):
    try:
        url = f"https://graph.facebook.com/v19.0/{idpost}/comments"
        payload = {
            "message": noidung,
            "attachment_url": image_url,
            "access_token": token
        }
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Cookie": cookie
        }
        res = requests.post(url, headers=headers, data=payload)
        if res.status_code != 200:
            return {"error": True, "msg": res.text}
        return res.json()
    except Exception as e:
        return {"error": True, "msg": str(e)}

def visual_delay(seconds):
    for remaining in range(int(seconds), 0, -1):
        print(f"\r{COLORS['vang']}   → Delay: {remaining}s ", end="", flush=True)
        time.sleep(1)
    print()
        
def image_tab_worker(
    post_id: str,
    cookies_raw: str,
    message: str,
    images: list[str],
    tag_id: str,
    delay_min: float,
    delay_max: float,
    stop_event: threading.Event,
    start_time: datetime,
    discord_user_id: str
):
    cookies = [ck.strip() for ck in cookies_raw.split(",") if ck.strip()]
    if not cookies:
        print(f"Không có cookie hợp lệ.")
        return

    cookie = cookies[0]  # chỉ lấy cookie đầu tiên, không chuyển cookie khác
    success_count = 0

    while not stop_event.is_set():
        try:
            login_info = check_login_facebook(cookie)
            if not login_info:
                print("Login thất bại, vẫn tiếp tục...")
            else:
                name, _, _, uid = login_info
                print(f"Dùng cookie: {name} | UID: {uid}")

                token = get_token(cookie)
                if not token:
                    print("Không lấy được token, vẫn tiếp tục...")
                else:
                    image_url = random.choice(images)
                    noidung = message
                    if tag_id:
                        noidung += f' @[{tag_id}:0]'

                    response = auto_cmt_moi_ne(token, post_id, noidung, image_url, cookie)

                    if isinstance(response, dict) and "error" in response:
                        print(f"Lỗi gửi comment: {response['msg']}")
                    else:
                        success_count += 1
                        print(f"Gửi thành công {success_count} lần | ID comment: {response.get('id')}")

        except Exception as e:
            print(f"Lỗi ngoại lệ: {e}")

        # Delay luôn được thực hiện dù có lỗi
        delay = random.uniform(delay_min, delay_max)
        for remaining in range(int(delay), 0, -1):
            if stop_event.is_set():
                break
            print(f"Delay: {remaining}s ", end="\r")
            time.sleep(1)
        if not stop_event.is_set():
            time.sleep(delay - int(delay))

    print(f"Tab ANHTOP user {discord_user_id} đã dừng.")
    
def _remove_user_and_kill_tabs(uid: str):
    users = load_users()
    if uid in users:
        del users[uid]
        save_users(users)
    with TAB_LOCK:
        if uid in user_tabs:
            for tab in user_tabs[uid]:
                tab["stop_event"].set()
            del user_tabs[uid]

    with IMAGE_TAB_LOCK:
        if uid in user_image_tabs:
            for tab in user_image_tabs[uid]:
                tab["stop_event"].set()
            del user_image_tabs[uid]
            


HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://chat.zalo.me",
    "Referer": "https://chat.zalo.me/",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
}

def now():
    return int(time.time() * 1000)

def zalo_encode(params, key):
    key = base64.b64decode(key)
    iv = bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = json.dumps(params).encode()
    pad_len = AES.block_size - len(plaintext) % AES.block_size
    padded = plaintext + bytes([pad_len] * pad_len)
    return base64.b64encode(cipher.encrypt(padded)).decode()

def zalo_decode(encrypted_data, key):
    key = base64.b64decode(key)
    iv = bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(base64.b64decode(encrypted_data))
    pad_len = decrypted[-1]
    return decrypted[:-pad_len].decode('utf-8', errors='ignore')

class ThreadType(Enum):
    USER = 1
    GROUP = 2

class ZaloAPI:
    def __init__(self, imei, cookies):
        self.session = requests.Session()
        self.imei = imei
        self.secret_key = None
        self.uid = None
        self.session.headers.update(HEADERS)
        self.session.cookies.update(cookies)
        self.login()

    def login(self):
        url = "https://wpa.chat.zalo.me/api/login/getLoginInfo"
        params = {"imei": self.imei, "type": 30, "client_version": 645, "ts": now()}
        response = self.session.get(url, params=params)
        try:
            data = response.json()
        except Exception:
            raise Exception("❌ Không thể phân tích JSON từ phản hồi!")

        user_data = data.get("data")
        if not isinstance(user_data, dict):
            print("⚠️ Phản hồi không hợp lệ hoặc sai IMEI/Cookie:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            raise Exception("❌ Không nhận được thông tin người dùng (user_data)")

        self.uid = user_data.get("send2me_id")
        self.secret_key = user_data.get("zpw_enk")
        if not self.secret_key:
            raise Exception("❌ Không lấy được secret_key")

    def fetch_groups(self):
        url = "https://tt-group-wpa.chat.zalo.me/api/group/getlg/v4"
        params = {"zpw_ver": 645, "zpw_type": 30}
        response = self.session.get(url, params=params)
        data = response.json()
        decoded = zalo_decode(data["data"], self.secret_key)
        parsed = json.loads(decoded)
        grid_map = parsed.get("data", {}).get("gridVerMap", {})
        groups = []
        for group_id in sorted(grid_map.keys(), key=lambda x: int(x)):
            info = self.fetch_group_info(group_id)
            groups.append({
                "id": group_id,
                "name": info["name"],
                "members": info["totalMember"]
            })
        return groups

    def fetch_group_info(self, group_id):
        url = "https://tt-group-wpa.chat.zalo.me/api/group/getmg-v2"
        params = {"zpw_ver": 645, "zpw_type": 30}
        encoded = zalo_encode({"gridVerMap": json.dumps({str(group_id): 0})}, self.secret_key)
        response = self.session.post(url, params=params, data={"params": encoded})
        result = response.json()
        decoded = zalo_decode(result["data"], self.secret_key)
        parsed = json.loads(decoded)
        info = parsed.get("data", {}).get("gridInfoMap", {}).get(str(group_id), {})
        return {
            "name": info.get("name", "(Không rõ tên)"),
            "totalMember": info.get("totalMember", "?")
        }

    def fetch_friends(self):
        url = "https://profile-wpa.chat.zalo.me/api/social/friend/getfriends"
        params = {"zpw_ver": 645, "zpw_type": 30}
        encoded = zalo_encode({"offset": 0, "count": 1000}, self.secret_key)
        response = self.session.post(url, params=params, data={"params": encoded})
        result = response.json()
        decrypted = zalo_decode(result["data"], self.secret_key)
        parsed = json.loads(decrypted)
        data_section = parsed.get("data", [])
        if isinstance(data_section, list):
            users = data_section
        else:
            users = data_section.get("users", [])
        return [{"id": u.get("userId"), "name": u.get("zaloName", "(Không rõ tên)")} for u in users]

    def send_message(self, message, thread_id, thread_type):
        url = "https://tt-group-wpa.chat.zalo.me/api/group/sendmsg" if thread_type == ThreadType.GROUP else "https://tt-chat2-wpa.chat.zalo.me/api/message/sms"
        payload = {
            "message": message,
            "clientId": str(now()),
            "imei": self.imei
        }
        if thread_type == ThreadType.GROUP:
            payload["visibility"] = 0
            payload["grid"] = str(thread_id)
        else:
            payload["toid"] = str(thread_id)
        encoded = zalo_encode(payload, self.secret_key)
        response = self.session.post(url, params={"zpw_ver": 645, "zpw_type": 30}, data={"params": encoded})
        return response.json()

    def set_typing_real(self, thread_id, thread_type):
        params = {"zpw_ver": 645, "zpw_type": 30}
        payload = {
            "params": {
                "imei": self.imei
            }
        }
        if thread_type == ThreadType.USER:
            url = "https://tt-chat1-wpa.chat.zalo.me/api/message/typing"
            payload["params"]["toid"] = str(thread_id)
            payload["params"]["destType"] = 3
        elif thread_type == ThreadType.GROUP:
            url = "https://tt-group-wpa.chat.zalo.me/api/group/typing"
            payload["params"]["grid"] = str(thread_id)
        else:
            raise Exception("Invalid thread type")
        encoded = zalo_encode(payload["params"], self.secret_key)
        self.session.post(url, params=params, data={"params": encoded})


class SpamTool(ZaloAPI):
    def __init__(self, name, imei, cookies, thread_ids, thread_type, use_typing=False):
        super().__init__(imei, cookies)
        self.name = name
        self.thread_ids = thread_ids
        self.thread_type = thread_type
        self.use_typing = use_typing
        self.running = False  # Mặc định là chưa chạy

    def send_spam(self, messages, delay):
        self.running = True  # Bắt đầu chạy

        while self.running:
            for thread_id in self.thread_ids:
                for message in messages:
                    if not self.running:
                        break  # Dừng ngay nếu có yêu cầu

                    try:
                        if self.use_typing:
                            print(f"[ZALO#{thread_id}] ✍️ Đang soạn tin...")
                            self.set_typing_real(thread_id, self.thread_type)
                            time.sleep(1.5)  # delay ngắn để giả lập soạn

                        result = self.send_message(message, thread_id, self.thread_type)

                        short_msg = (message[:50] + "...") if len(message) > 50 else message
                        print(f"[ZALO#{thread_id}] ✅ Thành công → {thread_id} | Nội dung: {short_msg}")
                    except Exception as e:
                        print(f"[ZALO#{thread_id}] ❌ Lỗi: {e}")

                    time.sleep(delay)

        print(f"[{self.name}] ⛔ Đã dừng spam.")


class ProductButtonView(discord.ui.View):
    def __init__(self, buy_url: str, admin_url: str):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="Mua Hàng", style=discord.ButtonStyle.link, url=buy_url))
        self.add_item(discord.ui.Button(label="Admin", style=discord.ButtonStyle.link, url=admin_url))


class ProductSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Quản lí", value="Quản lí", description="All lệnh chính", emoji="<:400377tools:1430542012062371841>"),
            discord.SelectOption(label="Messenger", value="messenger", description="Các lệnh spam/dừng trên Messenger", emoji="<:475210330_598195142840489_917248:1443295624219988189>"),
            discord.SelectOption(label="Facebook", value="facebook", description="Các lệnh spam/dừng trên Facebook", emoji="<:Facebook_Logo_2019png:1443295776938791064>"),
            discord.SelectOption(label="Discord", value="discord", description="Các lệnh spam/dừng trên Discord", emoji="<:1435530637418299433:1443303067800961189>"),
            discord.SelectOption(label="Zalo", value="zalo", description="Các lệnh spam/dừng trên Zalo", emoji="<:Icon_of_Zalosvg:1443814800470573198>"),
            discord.SelectOption(label="Telegram", value="telegram", description="Các lệnh spam/dừng trên Telegram", emoji="<:Telegram_2019_Logosvg:1443295041157206138>"),
            discord.SelectOption(label="Gmail", value="gmail", description="Các lệnh spam/dừng trên Gmail", emoji="<:1436376371680116957:1443303090014126100>"),
            discord.SelectOption(label="SMS", value="sms", description="Các lệnh spam/dừng SMS", emoji="<:IMessage_logosvg:1443817233976659998>"),
            discord.SelectOption(label="Wechat", value="wechat", description="Các lệnh spam/dừng Wechat", emoji="<:3938123:1443815374721388685>"),
            discord.SelectOption(label="Instagram", value="instagram", description="Các lệnh spam/dừng IG", emoji="<:Instagram_logo_2022svg:1443295089748086978>"),
        ]

        super().__init__(placeholder="Chọn danh mục để xem lệnh của Bot...", min_values=1, max_values=1, options=options,
                         custom_id="product_select_menu")

    async def callback(self, interaction: discord.Interaction):

        value = self.values[0]

        buy_url = "https://discord.gg/uTPvpsAF"
        admin_url = "https://discord.com/users/931053947060375623"


        if value == "messenger":
            embed = discord.Embed(
                title="Messenger",
                description=(
                    "`/treoanhmess` - treo ảnh mess\n"
                    "`/treomess` - treo 1 ndung mess\n"
                    "`/nhaymess` - nhây mess\n"
                    "`/nhaytagmess` - nhây đa tag mess\n"
                    "`/nhaynamebox` - nhây name box\n"
                    "`/tabnhaymess` - dừng nhây mess\n"
                    "`/tabnhaytagmess` - dừng nhây tag mess\n"
                    "`/tabnhaynamebox` - dừng nhây name box\n"
                    "`/setnenmess` - set nền mess liên tục\n"
                    "`/tabsetnenmess` - dừng set nền mess\n"
                    "`/treopollmess` - treo poll mess bất tử\n"
                    "`/tabtreopollmess` - dừng treo poll mess\n"
                    "`/combomess` - combo mess treo cực bá\n"
                    "`/raidbox` - thêm pr5 vào box"
                ),
                color=discord.Color.pink()
            )
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1443845682254581921/1443848336871526450/40a4592d0e7f4dc067ec0cdc24e038b9.jpg?ex=692a900c&is=69293e8c&hm=5ea5d2d1c1cd9cd337535065081305812c83a74ae041418b154afd46894d8074&=&format=webp")
            embed.set_image(url="https://media.discordapp.net/attachments/1443845682254581921/1443852912278376458/standard_1.gif?ex=692a944f&is=692942cf&hm=42f735b7619314e151c6b735621538271fabb0562bcb3e778d4aa7acbb2c59d5&=")

        elif value == "facebook":
            embed = discord.Embed(
                title="Facebook",
                description=(
                    "`/nhaytop` - nhây bài viết\n"
                    "`/anhtop` - treo ảnh bài viết\n"
                    "`/tabnhaytop` - dừng nhây bài top\n"
                    "`/tabanhtop` - dừng nhây ảnh top"
                ),
                color=discord.Color.pink()
            )
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1443845682254581921/1443848336871526450/40a4592d0e7f4dc067ec0cdc24e038b9.jpg?ex=692a900c&is=69293e8c&hm=5ea5d2d1c1cd9cd337535065081305812c83a74ae041418b154afd46894d8074&=&format=webp")
            embed.set_image(url="https://media.discordapp.net/attachments/1443845682254581921/1443852912278376458/standard_1.gif?ex=692a944f&is=692942cf&hm=42f735b7619314e151c6b735621538271fabb0562bcb3e778d4aa7acbb2c59d5&=")

        elif value == "discord":
            embed = discord.Embed(
                title="Discord",
                description=(
                    "`/alltreodis` - all các lệnh treo discord\n"
                    "`/allnhaydis` - all lệnh nhây dis\n"
                    "`/taballtreodis` - dừng treo discord\n"
                    "`/taballnhaydis` - dừng all nhây discord\n"
                    "`/raidtaokenh` - tạo kênh sever discord nhanh\n"
                    "`/thread` - spam tạo chủ đề discord độc quyền\n"
                    "`/tabthread` - dừng tạo chủ đề\n"
                    "`/polldis` - tạo thăm dò ý kiến discord độc quyền\n"
                    "`/tabpolldis` dừng cuộc thăm dò ý kiến discord"
                ),
                color=discord.Color.purple()
            )
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1443845682254581921/1443848336871526450/40a4592d0e7f4dc067ec0cdc24e038b9.jpg?ex=692a900c&is=69293e8c&hm=5ea5d2d1c1cd9cd337535065081305812c83a74ae041418b154afd46894d8074&=&format=webp")
            embed.set_image(url="https://media.discordapp.net/attachments/1443845682254581921/1443852912278376458/standard_1.gif?ex=692a944f&is=692942cf&hm=42f735b7619314e151c6b735621538271fabb0562bcb3e778d4aa7acbb2c59d5&=")

        elif value == "telegram":
            embed = discord.Embed(
                title="Telegram",
                description=(
                    "`/treotele` - treo ngôn telegram\n"
                    "`/tabtreotele` - dừng treo ngôn telegram"
                ),
                color=discord.Color.red()
            )
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1443845682254581921/1443848336871526450/40a4592d0e7f4dc067ec0cdc24e038b9.jpg?ex=692a900c&is=69293e8c&hm=5ea5d2d1c1cd9cd337535065081305812c83a74ae041418b154afd46894d8074&=&format=webp")
            embed.set_image(url="https://media.discordapp.net/attachments/1443845682254581921/1443852912278376458/standard_1.gif?ex=692a944f&is=692942cf&hm=42f735b7619314e151c6b735621538271fabb0562bcb3e778d4aa7acbb2c59d5&=")

        elif value == "zalo":
            embed = discord.Embed(
                title="Zalo",
                description=(
                    "`/treozalo` - treo zalo\n"
                    "`/nhaytagzalo` - nhây tag zalo\n"
                    "`/treopollzl` - treo bình chọn zalo\n"
                    "`/nhaynameboxzl` - nhây name box zalo\n"
                    "`/treosticker` - treo sờ tích cơ zalo\n"
                    "`/tabtreozalo` - dừng treo zalo\n"
                    "`/tabnhaynameboxzl` - dừng nhây name box zalo\n"
                    "`/tabtreosticker` - dừng treo sticker zalo"
                ),
                color=discord.Color.green()
            )
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1443845682254581921/1443848336871526450/40a4592d0e7f4dc067ec0cdc24e038b9.jpg?ex=692a900c&is=69293e8c&hm=5ea5d2d1c1cd9cd337535065081305812c83a74ae041418b154afd46894d8074&=&format=webp")
            embed.set_image(url="https://media.discordapp.net/attachments/1443845682254581921/1443852912278376458/standard_1.gif?ex=692a944f&is=692942cf&hm=42f735b7619314e151c6b735621538271fabb0562bcb3e778d4aa7acbb2c59d5&=")

        elif value == "gmail":
            embed = discord.Embed(
                title="Gmail",
                description=(
                    "`/treogmail` - treo gmail\n"
                    "`/tabtreogmail` - dừng treo gmail"
                ),
                color=discord.Color.red()
            )
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1443845682254581921/1443848336871526450/40a4592d0e7f4dc067ec0cdc24e038b9.jpg?ex=692a900c&is=69293e8c&hm=5ea5d2d1c1cd9cd337535065081305812c83a74ae041418b154afd46894d8074&=&format=webp")
            embed.set_image(url="https://media.discordapp.net/attachments/1443845682254581921/1443852912278376458/standard_1.gif?ex=692a944f&is=692942cf&hm=42f735b7619314e151c6b735621538271fabb0562bcb3e778d4aa7acbb2c59d5&=")

        elif value == "sms":
            embed = discord.Embed(
                title="SMS",
                description=(
                    "`/treosms` - treo sms\n"
                    "`/tabtreosms` - dừng treo sms"
                ),
                color=discord.Color.orange()
            )
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1443845682254581921/1443848336871526450/40a4592d0e7f4dc067ec0cdc24e038b9.jpg?ex=692a900c&is=69293e8c&hm=5ea5d2d1c1cd9cd337535065081305812c83a74ae041418b154afd46894d8074&=&format=webp")
            embed.set_image(url="https://media.discordapp.net/attachments/1443845682254581921/1443852912278376458/standard_1.gif?ex=692a944f&is=692942cf&hm=42f735b7619314e151c6b735621538271fabb0562bcb3e778d4aa7acbb2c59d5&=")

        elif value == "wechat":
            embed = discord.Embed(
                title="Wechat",
                description=(
                    "`/treowechat` - treo wechat\n"
                    "`/tabtreowechat` - dừng treo wechat"
                ),
                color=discord.Color.orange()
            )
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1443845682254581921/1443848336871526450/40a4592d0e7f4dc067ec0cdc24e038b9.jpg?ex=692a900c&is=69293e8c&hm=5ea5d2d1c1cd9cd337535065081305812c83a74ae041418b154afd46894d8074&=&format=webp")
            embed.set_image(url="https://media.discordapp.net/attachments/1443845682254581921/1443852912278376458/standard_1.gif?ex=692a944f&is=692942cf&hm=42f735b7619314e151c6b735621538271fabb0562bcb3e778d4aa7acbb2c59d5&=")

        elif value == "instagram":
            embed = discord.Embed(
                title="Instagram",
                description=(
                    "`/treoig` - treo ig\n"
                    "`/tabtreoig` - dừng treo ig"
                ),
                color=discord.Color.magenta()
            )
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1443845682254581921/1443848336871526450/40a4592d0e7f4dc067ec0cdc24e038b9.jpg?ex=692a900c&is=69293e8c&hm=5ea5d2d1c1cd9cd337535065081305812c83a74ae041418b154afd46894d8074&=&format=webp")
            embed.set_image(url="https://media.discordapp.net/attachments/1443845682254581921/1443852912278376458/standard_1.gif?ex=692a944f&is=692942cf&hm=42f735b7619314e151c6b735621538271fabb0562bcb3e778d4aa7acbb2c59d5&=")

        elif value == "Quản lí":
            embed = discord.Embed(
                title="Quản lí",
                description=(
                    "`/menu` - hiển thị menu bot\n"
                    "`/addadmin` - thêm admin phụ có quyền dùng bot\n"
                    "`/xoaadmin` - xóa admin phụ có quyền dùng bot\n"
                    "`/listadmin` - list admin phụ có quyền dùng bot\n"
                    "`/checkcookie` - check cookie fb\n"
                    "`/checkuid` - check uid discord\n"
                    "`/checktask` - check task đang chạy\n"
                    "`/idkenh` - lấy id kênh discord\n"
                    "`/setstatus` - Thay đổi trạng thái của Bot\n"
                    "`/ping` - Xem tình trạng hệ thống Bot\n"
                    "`/say1` - nhại tin nhắn admin bằng bảng discord\n"
                    "`/say2` - nhại tin nhắn admin bằng text thường"
                ),
                color=discord.Color.yellow()
            )
            embed.set_thumbnail(url="https://media.discordapp.net/attachments/1443845682254581921/1443848336871526450/40a4592d0e7f4dc067ec0cdc24e038b9.jpg?ex=692a900c&is=69293e8c&hm=5ea5d2d1c1cd9cd337535065081305812c83a74ae041418b154afd46894d8074&=&format=webp")
            embed.set_image(url="https://media.discordapp.net/attachments/1443845682254581921/1443852912278376458/standard_1.gif?ex=692a944f&is=692942cf&hm=42f735b7619314e151c6b735621538271fabb0562bcb3e778d4aa7acbb2c59d5&=")



        # … thêm các sản phẩm khác y như mẫu …

        else:
            embed = discord.Embed(
                title="Không tìm thấy sản phẩm!",
                description="Vui lòng chọn lại.",
                color=discord.Color.red()
            )

        view = ProductButtonView(buy_url, admin_url)

        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class ProductMenuView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(ProductSelect())


bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
tree = bot.tree


@tree.command(name="menu", description="Hiển thị danh sách chức năng của bot")
async def menu(interaction: discord.Interaction):
    embed = discord.Embed(
        title="**tran van trong**",
        description=(
            "**Click vào ô bên dưới sau đó chọn dịch vụ bạn cần tham khảo bot sẽ hiện thị hướng dẫn cụ thể !**\n\n"
           "**Mua Hàng/Support 24/7: [Click here](https://discord.gg/HyJtANhBfE)**\n"
            "**Discord Admin: [Click here](https://discord.com/users/931053947060375623)**\n"
        ),
        color=discord.Color(0x8000FF)
    )

    embed.set_thumbnail(url="https://media.discordapp.net/attachments/1443845682254581921/1443848336871526450/40a4592d0e7f4dc067ec0cdc24e038b9.jpg?ex=692a900c&is=69293e8c&hm=5ea5d2d1c1cd9cd337535065081305812c83a74ae041418b154afd46894d8074&=&format=webp")
    embed.set_image(url="https://media.discordapp.net/attachments/1473270356314685473/1473656964281008201/standard_6.gif?ex=6997017f&is=6995afff&hm=23b999dba964462878314c5dd5afe1412bccf97195a6f07a7cdc63d572b7b2ee&=&width=550&height=194")

    await interaction.response.send_message(embed=embed, view=ProductMenuView())


@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot đã online với tên: {bot.user}")
    print("✅ Slash command đã được sync thành công!")
        
@tree.command(
    name="nhaytop",
    description="Treo nhây top"
)
@app_commands.describe(
    cookies="Cookie",
    post_link="Link bài viết",
    delay="Delay",
    tag_id="ID cần tag"
)
async def nhaytop(
    interaction: discord.Interaction,
    cookies: str,
    post_link: str,
    delay: float,
    tag_id: str = None
):
    if not is_authorized(interaction) and not is_admin(interaction):
        return await interaction.response.send_message("Bạn không có quyền sử dụng bot", ephemeral=True)

    cookie_list = [normalize_cookie(c.strip()) for c in cookies.split(",") if c.strip()]
    if not cookie_list:
        return await interaction.response.send_message("Cookie không hợp lệ", ephemeral=True)

    if delay < 0.5:
        return await interaction.response.send_message("Delay phải trên 0.5s", ephemeral=True)

    post_id, group_id = extract_post_group_id(post_link)
    if not post_id or not group_id:
        return await interaction.response.send_message("Link không đúng định dạng group/post", ephemeral=True)

    stop_event = threading.Event()
    start_time = datetime.now()
    discord_user_id = str(interaction.user.id)

    th = threading.Thread(
        target=nhaytop_worker,
        args=(cookie_list, delay, post_id, group_id, tag_id, stop_event, start_time, discord_user_id),
        daemon=True
    )
    th.start()

    with NHAY_LOCK:
        if discord_user_id not in user_nhay_tabs:
            user_nhay_tabs[discord_user_id] = []
        user_nhay_tabs[discord_user_id].append({
            "thread": th,
            "stop_event": stop_event,
            "start": start_time,
            "post_id": post_id,
            "group_id": group_id,
            "delay": delay,
            "tag_id": tag_id
        })

    await interaction.response.send_message(
        f"Đã tạo tab nhây top cho <@{discord_user_id}>:\n"
        f"• GroupID: `{group_id}` | PostID: `{post_id}`\n"
        f"• Delay: `{delay}` giây\n"
        f"{'• Tag UID: '+tag_id if tag_id else ''}\n"
        f"• Bắt đầu: `{start_time.strftime('%Y-%m-%d %H:%M:%S')}`",
        ephemeral=True
    )
         

raw_spam_list = [
    "ccho sua lofi de {chon_name}",
    "sua di {chon_name} em😏🤞",
    "lofi di {chon_name} cu😝",
    "tk ngu lon {chon_name} eyy🤣🤣",
    "nhanh ti em {chon_name}🤪👌",
    "cam a {chon_name} mo coi😏🤞",
    "hang hai len ti {chon_name} de👉🤣",
    "cn tat nguyen {chon_name}😏??",
    "cn 2 lai mat mam {chon_name}🤪👎",
    "anh cho may sua a {chon_name}😏🤞",
    "ah ba meta 2025 ma {chon_name}😋👎",
    "bi anh da na tho cmnr dk {chon_name}🤣",
    "thieu oxi a {chon_name}🤣🤣",
    "anh cko may oxi hoa ne {chon_name}😏👉🤣",
    "may cay cha qua a cn ngu {chon_name}🤪",
    "may phe nhu con me may bi tao hiep ma {chon_name}🤣",
    "dung ngam dang nuot cay tao nha coan {chon_name}👉🤣",
    "con cho {chon_name} cay tao ro👉🌶",
    "oc cho ngoi do nhay voi tao a {chon_name}🤣",
    "me may bi tao cho len dinh r {chon_name}=))",
    "ui cn ngu {chon_name} oc cac=))",
    "cn gai me may khog bt day nay a {chon_name} cn oc cac😝",
    "cn cho {chon_name} may cam a:))?",
    "cam lang that r a cn ngu {chon_name}🤣",
    "ui tk cac dam cha chem chu ak {chon_name}😝🤞",
    "cn cho dot so tao run cam cap me roi ha em {chon_name} =))",
    "ui cai con hoi {chon_name}👉🤣",
    "cn me may chet duoi ao roi kia {chon_name}😆",
    "djt con {chon_name} cu cn lon tham:))",
    "ui con bem {chon_name} nha la nhin phen v:))",
    "con cho cay gan nha sua di {chon_name}😏",
    "con bem {chon_name} co me khog😏🤞",
    "a quen may mo coi tu nho ma {chon_name}🤣",
    "sua chill de {chon_name} oc🤣",
    "hay cam nhan noi dau di em {chon_name}:))))",
    "hinh anh con bem {chon_name} gie rach bi anh cha dap:))))))",
    "ti anh chup dang tbg la may hot nha {chon_name}🤣",
    "a may muon hot cx dau co de cn ngu {chon_name}👉🤣🤣",
    "oi may bi cha suc pham kia {chon_name}-))",
    "tao co noti con boai {chon_name} so tao:)) ti tao cap dang profile 1m theo doi:))",
    "{chon_name} con o moi khong bame bi tao khinh thuong=)))",
    "may con gi khac hon khong con bem du ngu {chon_name}🤣",
    "cam canh cdy ngu bi cha chui khong giam phan khang a {chon_name}:))",
    "bi tao chui ma toi so a {chon_name}🤞",
    "nhin ga {chon_name} muon ia chay🤣",
    "con culi lua thay phan ban bi phan boi a {chon_name}:))",
    "may bi tao chui cho om han dk {chon_name}👉🤣🤣🤞",
    "bi tao chui cho so queo cac dung khong {chon_name}:))))",
    "dung cam han tao nua {chon_name}:))",
    "con dog {chon_name} bi tao chui ghi thu a:))",
    "su dung ngon sat thuong xiu de bem anh di mo {chon_name}=)))",
    "co sat thuong chi mang ko ay {chon_name}😝",
    "con ngheo nha la {chon_name} bi bo si va👉🤣🤣",
    "nao may co biet thu nhu anh vay {chon_name}🤪👌",
    "thang nghich tu {chon_name} sao may giet cha may the:))",
    "khong ngo thang phan nghich {chon_name} lua cha doi me=))",
    "tk ngu {chon_name} bi anh co lap ma-))",
    "phan khang di con cali {chon_name} mat map:))",
    "may con gi khac ngoai sua khong ay {chon_name}👉😏🤞",
    "{chon_name} mo coi=))",
    "bi cha chui phat nao ghi han phat do {chon_name} dk em:))",
    "may toi day de chi bi tao chui thoi ha {chon_name}:))",
    "bo la ac quy fefe ne {chon_name}🤣🤣",
    "nen bo lay cay ak ban nat so may luon😏🤞",
    "keo lu ban an hai may ra lmj dc anh khong vay {chon_name}🤣🤞",
    "ui ui dung thang an hai mang ten {chon_name}:))",
    "dung la con can ba mxh chi biet nhin anh chui cha mang me no ma {chon_name}=))",
    "may co phan khang duoc khong vay:)) {chon_name}",
    "may khong phan khang duoc a {chon_name}=))",
    "may yeu kem den vay a con cali {chon_name}😋👎",
    "con cali {chon_name} mat mam cay ah roi🌶",
    "cu anh lam dk em {chon_name}:))",
    "may co biet gi ngoai sua kiki dau ma {chon_name}👉🤣🤣",
    "may la chi qua qua ban may la chi gau gau ha {chon_name}=))",
    "mua skill di em {chon_name}🤪🤞",
    "anh mua skill duoc ma em {chon_name}😏🤞",
    "anh mua skill vo cai lon me may ay em {chon_name}:))",
    "con culi {chon_name} said : sap win duoc anh roi mung vai a🤣",
    "con cali {chon_name} nghi vay nen mung lam dk:)) {chon_name}",
    "win duoc anh dau de dau em {chon_name}🤪🤞",
    "con cho dien {chon_name} sua dien cuong nao🤣",
    "ui ui con kiki {chon_name} cay anh da man a🌶",
    "tk mo coi {chon_name} sua belike a🤣",
    "chill ti di em {chon_name}🤣🤣",
    "m còn trò gì thể hiện nhanh lên ơ kìa {chon_name}",
    "óc chó không trình lên đây sủa mạnh mẽ lên anh chơi mày cả ngày mà 😹 {chon_name}",
    "ơ hay óc chó ơi m sủa mạnh mẽ lên sao lại bị dập rồi {chon_name}",
    "lêu lêu thằng ngu không làm gì được cay anh kìa {chon_name}",
    "haha óc chó gà bị chửi cay cú ớt mẹ rồi =))) {chon_name}",
    "óc chó ngu nghèo cay cha bán mạng đi chửi cha má kìa =)))) {chon_name}",
    "m chạy đâu vậy con chó ngu ơi không được chạy mà :((( {chon_name}",
    "ai đụng gì óc chó để nó sợ rồi chạy thục mạng kìa {chon_name}",
    "culi ngu bị anh chửi té tát nước vô mặt m kìa =))) {chon_name}",
    "em bé khóc kìa ai cứu nó đi 😹😹 {chon_name}",
    "culi bị chửi mất xác kìa 😹😹😹 {chon_name}",
    "cha bá sàn mà {chon_name}",
    "cha bá all sàn mà bọn óc 🤪 {chon_name}",
    "thằng ngu giết cha bóp cổ má để cầu win anh à 😏👉 {chon_name}",
    "hi vọng làm dân war của con ngu bị tao dập tắt từ khi nó sủa điên trước mặt tao ae =))) {chon_name}",
    "bà nội m loạn luân với bố m còn ông ngoại loạn luân với mẹ m mà thằng não cún =)) 🤪 {chon_name}",
    "con thú mại dâm bán dâm mà như bán trinh hoa hậu vậy 🤣 {chon_name}",
    "con ngu nứng quá đến cả con mẹ nó gần u60 rồi nó vẫn không tha =)) {chon_name}",
    "mẹ mày làm con chó canh cửa cho nhà tao mà 🤣 {chon_name}",
    "đáp ngôn nhanh hơn tý được không thằng ngu xuẩn {chon_name}",
    "bắt quả tang con chó chạy bố nè {chon_name}",
    "não cún chỉ biết âm thầm seen và ôm gối khóc mà huhuh 👈😜 {chon_name}",
    "con cave này adr 16gb đang kiếm tiền mua iPhone được 🤣🤣 {chon_name}",
    "vào một hôm bỗng con đĩ mẹ mày die thì lúc đó cha làm bá chủ sàn mẹ rồi :)) {chon_name}",
    "con đĩ mẹ mày bất lực vì bị tao chửi mà chỉ biết câm lặng :)) {chon_name}",
    "mẹ mày bị tao đụ đột quỵ ngoài nhà nghỉ kìa đem hòm ra nha {chon_name}",
    "đem hai cái mày với con mẹ m luôn nha {chon_name}",
    "thời gian trôi qua để cảm nhận nỗi đau đi ửa à {chon_name}",
    "nhai tao chặt đầu con đĩ má mày ra đó {chon_name}",
    "thằng ngu LGBT da đen sủa lẹ ai cho mày câm {chon_name}",
    "thằng sex thú đang cố làm cha cay hả thằng bại não {chon_name}",
    "tao miễn nhiễm mà thằng ngu {chon_name}",
    "mẹ mày bị cha đụ từ Nam vào đến Bắc mà 🤪👊 {chon_name}",
    "mẹ mày banh háng cho khách đụ kìa thằng óc {chon_name}",
    "tao lỡ cho mẹ mày bú cu tao rồi sướng vãi cặc 🧐🤙 {chon_name}",
    "lêu lêu nhìn cha đụ mẹ mày không làm được gì à đừng có cay cha nha 😝👎 {chon_name}",
    "bị tao khủng bố quá nát mẹ cái hộp sọ với não luôn rồi à =)) {chon_name}",
    "mày là con đĩ đầu đinh giết má để loạn luân với bố mà con khốn {chon_name}",
    "văn thơ anh lai láng để con mẹ m dạng háng mỗi đêm =))) {chon_name}",
    "qua sông thì phải bắc cầu kiều con mẹ mày muốn làm đĩ thì phải yêu chiều các anh mà 🤣👈 {chon_name}",
    "con lồn ngu này hay đạp xe đạp ngang nhà tao bị tao chọi đá về méc mẹ mà 🤣 {chon_name}",
    "thằng ngu này đang đi bộ bị t đánh úp nó về mách mẹ mà ae 🤣🤣 {chon_name}",
    "thằng đầu đinh ở nhà lá mà ae nó mơ ước được ở biệt thự như tui =)) {chon_name}",
    "cả họ nhà mày phải xếp hàng lần lượt bú dái t mà 🤣🤣 {chon_name}",
    "thằng ảo war bị tao chửi cố gắng phản kháng nhưng nút home không cho phép mày cay quá đập cmn máy 🤣👈 {chon_name}"
    "sống như 1 con chó ngu dốt như lũ phèn ói chợ búa cầm dao múa kiếm {chon_name}",
    "cha mày hóa thân thành hắc bạch vô thường cha mày bắt hồn đĩ mẹ mày xuống chầu diêm vương {chon_name}",
    "nghèo bần hèn bị cha mày đứng trên đạp đầu lũ đú chúng mày cha đi lên {chon_name}",
    "đú má mày tới tháng xịt nước máu kinh cho thk cha mày uống {chon_name}",
    "mày đi học bị bạn bè chê xài nút home mày cay quá về đánh đập bà già kêu bả làm đĩ để có tiền mua điện thoại mới đi sĩ với bạn bè =)) {chon_name}",
    "con điếm phò mã bị cha mày cầm cái cây chà bồn cầu cha chà nát lồn mày nè {chon_name}",
    "đừng có lên mạng xã hội tạo nét mà bị anh hành là mếu máo đi cầu cứu ngay {chon_name}",
    "mày thấy anh chửi thấm quá và nghĩ trong đầu là anh này bá vcl đéo chửi lại nó đâu :))) {chon_name}",
    "thằng này đang ăn bị t đứng trên nóc nhà nó t ỉa trúng bát cơm nó luôn mà ae {chon_name}",
    "mày bí ngôn tới nỗi phải lên google ghi : những câu chửi nhau hay nhất để phản kháng tao mà 🤣👈 {chon_name}",
    "mày thấy a chửi hay quá nên xin làm đệ của a để được kéo làm hw à :))) {chon_name}",
    "mày bị chửi tới nỗi tăng huyết áp phải cầu xin anh tha thứ :))) {chon_name}",
    "người yêu nó bị t đụ rên ư ử khen ku a trung to và dài thế :)))) {chon_name}",
    "mẹ nó khen cặc t to chấp nhận bỏ ba nó vì ông ấy yếu sinh lý :))) {chon_name}",
    "cha nó ôm hận t lắm chỉ biết đứng ôm cặc khóc trong vô vọng :))) {chon_name}",
    "mẹ nó bị t đụ chán chê xong bị t trap t yêu người mẫu mà 🤣👈 {chon_name}",
    "con bướm trâu bị gái có cu yêu qua mạng trap =))) {chon_name}",
    "trăng kia ai vẽ mà tròn loz con mẹ m bị ai địt mà mòn 1 bên 🤣 {chon_name}",
    "mẹ m có phải còn búp bê tình dục để a lục đục mỗi đêm không 😏? {chon_name}",
    "mẹ m thì xóc lọ cho t còn người ta thì kính lão đắc thọ {chon_name}",
    "m tin bố lấy yamaha bố đề số 3 bố tông vào loz con đĩ mẹ m không {chon_name}",
    "m gặp các anh đây toàn đấng tối cao a cầm con dao a đâm a thọc a chọc vào cái lỗ loz con mẹ m mà 🤣👈 {chon_name}",
    "cha m lấy gạch ống chọi nát cái đầu mu lồn mẹ mày giờ con bẻm đú {chon_name}",
    "con mồ côi mày mà rớt là tao lấy chiếc xe rùa t cán lòi mu lồn mẹ m đó gán trụ nha {chon_name}",
    "cú đấm sấm sét của anh đấm nát cái lồn mẹ thằng chó đú nhây như mày🤣👈 {chon_name}",
    "cú đá cuồng phong đá bung cái lồn mẹ mày nè thằng não cặc🤣👈 {chon_name}",
    "anh lấy cái ô tô anh đâm thẳng dô cái lồn con gái mẹ thằng súc vật như m {chon_name}",
    "hôm nay anh sẽ thay trời hành đạo anh cạo nát cái lông lồn con gái mẹ mày đó nghe chưa {chon_name}",
    "con đĩ eo di bi ti bị mẹ mày hành cho tới đột quỵ k có tiền lo t//ang lễ phải quỳ qua háng tao van xin tao cho tiền đúng kh {chon_name}",
    "thằng cặc chứng kiến cái cảnh mẹ nó bị t cầm bật lửa đốt từng cộng lông bướm:))) {chon_name}",
    "anh gõ chết con đĩ mẹ mày giờ mày sủa ngôn có sthuong tý coi em nhìn em phèn dạ anh mày chửi luôn ông bà mày đái lên mặt mày nè con sút vật yếu kém {chon_name}",
    "thằng óc cặc bị tao ném xuống ao nhưng béo quá bị chết chìm🐕 {chon_name}",
    "mày bị tao hành hung cho sắp đột tử rồi kìa kêu con đĩ mẹ mày qua cứu vãn mày lẹ đi không là tao cho mày nằm quan tài gào khóc thảm thiết trong đó liền ngay 3s nè con đĩ phế {chon_name}",
    "nhanh lên con chó lồn khai khắm=)) {chon_name}",
    "con gái mẹ mày die dưới tay bọn anh kìa {chon_name}",
    "thằng bẻm bị t thọc cặc lên ổ cứng phát não rớt ra ngoài=))) {chon_name}",
    "cạn bã của xã hội mà tưởng mình hay hã con thú🤣💨 {chon_name}",
    "thằng óc dái khi nghe tin cha nó chết kiểu: úi úi thằng già này cuối cùng cũng chết r vui vl=)) {chon_name}",
    "thằng lồn ảo anime bật gear 5 lên địt con già nó trước bàn thờ tổ tiên=)) {chon_name}",
    "anh là cha dượng của bọn mày mà tụi bú cứt 🤣 {chon_name}",
    "đây là suy nghĩ của con ngu sau khi nó bị tao sỉ nhục trong đầu nó bây giờ kiểu: quân tử trả thù 10 năm chưa muộn :))))) {chon_name}",
    "thằng ngu bị tao áp đảo từ phút 1 tới giờ nó k có cơ hội để sủa luôn ae=))) {chon_name}",
    "thằng đú bot mời ae nó sang nhà đụ bà già nó free vì hôm nay là ngày vui vì cha nó mới qua đời=)) {chon_name}",
    "thằng cặc bị tao hạ đo ván sau 1 cú sút ngoạn mục đến từ vị trí anh mà=))) {chon_name}",
    "thằng óc cặc đòi va anh và cái kết bị anh chửi chạy khắp nơi=)) {chon_name}",
    "mẹ mày bị tao địt rách màn trinh mà🤪 {chon_name}",
    "🤭🤭Mày bê đê ngũ sắc dell công khai bị tao chọc quá máu cặc mày dồn lên não choa mày chết hả {chon_name}",
    "nhà thằng đú này nghèo không có tiền chơi gái nên phải loạn luân luôn với mẹ nó để giải khát cơn thèm thuồng {chon_name}",
    "thằng cầm thú loạn luân some với mẹ ruột và ba ruột còn quay clip {chon_name}",
    "m bị óc cứt hay sao z hả mà t nói m dell hiểu hay bố phải nhét cứt vào đầu m thì m mới thông hả con óc lồn ơi {chon_name}",
    "Một lũ xam cu lên đây đú ửa ngôn thì nhạt như cái nước lồn của con đỉ mẹ cm v hăng lên đi con mẹ mày bị t xé rách mu sao chối ???? {chon_name}",
    "bà già mày bị tao treo cổ lên trên trần nhà mà? {chon_name}",
    "thằng bất tài vô dụng sủa mạnh lên đi {chon_name}",
    "cố gắng để win tao nhá {chon_name}",
    "tao bất bại mà thằng ngu? {chon_name}",
    "mẹ mày bị t đầu độc đến chết mà {chon_name}",
    "mày đàn ông hay đàn bà yếu đuối vậy {chon_name}",
    "con chó đầu đinh bị anh cầm cái đinh ba a thọc vào lỗ nhị nó mà ae =)) {chon_name}",
    "thằng như mày xứng đáng ăn cứt tao á {chon_name}",
    "Nghe Cha Chửi Chết Con Gái Mẹ Mày Nè Con Ngu {chon_name}",
    "Mẹ Mày Bị Tao Lấy Phóng Lợn Chọt Dô Mu Lồn Khi Đang Đi Làm Gái Ở Ngã 3 Trần Duy Hưng🤣👈 {chon_name}",
    "con mẹ m nghe tin m loạn luân vs bố m nên lấy dao cắt cổ tự tử r kìa con ngu :)) {chon_name}",
    "m tìm câu nào sát thương tí được k thằng nghịch tử đâm bố đụ mẹ :)) 🤣 {chon_name}",
    "óc chó bị anh chửi nhớ cha nhớ mẹ nhớ kiếp trước kìa😹😹😹 {chon_name}",
    "Khẩu phần ăn của mẹ m là cứt mà😜 {chon_name}",
    "Mẹ m bị anh treo cổ mà😜 {chon_name}"    
]

def nhaytop_worker(
    cookie_list: list[str],
    delay: float,
    post_id: str,
    group_id: str,
    tag_id: str,
    stop_event: threading.Event,
    start_time: datetime,
    discord_user_id: str
):
    index_ck = 0
    line_index = 0

    while not stop_event.is_set():
        cookie = cookie_list[index_ck % len(cookie_list)]
        user_id, fb_dtsg, rev, req, a, jazoest = get_uid_fbdtsg(cookie)
        if not (user_id and fb_dtsg and jazoest):
            index_ck += 1
            continue

        chon_name = ""
        if tag_id:
            info = get_info(tag_id, cookie, fb_dtsg, a, req, rev)
            if "name" in info:
                chon_name = info["name"]
        
        raw = raw_spam_list[line_index % len(raw_spam_list)]
        line_index += 1
        content = raw.replace("{chon_name}", chon_name).strip()

        ok = cmt_gr_pst(
            cookie, group_id, post_id, content,
            user_id, fb_dtsg, rev, req, a, jazoest,
            uidtag=tag_id, nametag=chon_name if tag_id else None
        )
        status = "OK" if ok else "FAIL"
        uptime = get_uptime(start_time)
        print(f"[NHAY][{discord_user_id}] → {group_id}/{post_id} | {status} | Uptime:{uptime}".ljust(120), end="\r")

        for _ in range(int(delay)):
            if stop_event.is_set(): break
            time.sleep(1)
        if stop_event.is_set(): break
        time.sleep(delay - int(delay))

        if not ok:
            index_ck += 1

    print(f"\\nTab NHAYTOP của user {discord_user_id} đã dừng.")
    
def get_guid():
    section_length = int(time.time() * 1000)
    
    def replace_func(c):
        nonlocal section_length
        r = (section_length + random.randint(0, 15)) % 16
        section_length //= 16
        return hex(r if c == "x" else (r & 7) | 8)[2:]

    return "".join(replace_func(c) if c in "xy" else c for c in "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx")

def normalize_cookie(cookie, domain='www.facebook.com'):
    headers = {
        'Cookie': cookie,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (like Gecko) Chrome/122.0.0.0 Safari/537.36'
    }
    try:
        response = requests.get(f'https://{domain}/', headers=headers, timeout=10)
        if response.status_code == 200:
            set_cookie = response.headers.get('Set-Cookie', '')
            new_tokens = re.findall(r'([a-zA-Z0-9_-]+)=[^;]+', set_cookie)
            cookie_dict = dict(re.findall(r'([a-zA-Z0-9_-]+)=([^;]+)', cookie))
            for token in new_tokens:
                if token not in cookie_dict:
                    cookie_dict[token] = ''
            return ';'.join(f'{k}={v}' for k, v in cookie_dict.items() if v)
    except:
        pass
    return cookie

def get_uid_fbdtsg(ck):
    try:
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
            'Connection': 'keep-alive',
            'Cookie': ck,
            'Host': 'www.facebook.com',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        
        try:
            response = requests.get('https://www.facebook.com/', headers=headers)
            
            if response.status_code != 200:
                print(f"Status Code >> {response.status_code}")
                return None, None, None, None, None, None
                
            html_content = response.text
            
            user_id = None
            fb_dtsg = None
            jazoest = None
            
            script_tags = re.findall(r'<script id="__eqmc" type="application/json[^>]*>(.*?)</script>', html_content)
            for script in script_tags:
                try:
                    json_data = json.loads(script)
                    if 'u' in json_data:
                        user_param = re.search(r'__user=(\d+)', json_data['u'])
                        if user_param:
                            user_id = user_param.group(1)
                            break
                except:
                    continue
            
            fb_dtsg_match = re.search(r'"f":"([^"]+)"', html_content)
            if fb_dtsg_match:
                fb_dtsg = fb_dtsg_match.group(1)
            
            jazoest_match = re.search(r'jazoest=(\d+)', html_content)
            if jazoest_match:
                jazoest = jazoest_match.group(1)
            
            revision_match = re.search(r'"server_revision":(\d+),"client_revision":(\d+)', html_content)
            rev = revision_match.group(1) if revision_match else ""
            
            a_match = re.search(r'__a=(\d+)', html_content)
            a = a_match.group(1) if a_match else "1"
            
            req = "1b"
                
            return user_id, fb_dtsg, rev, req, a, jazoest
                
        except requests.exceptions.RequestException as e:
            print(f"Lỗi Kết Nối Khi Lấy UID/FB_DTSG: {e}")
            return get_uid_fbdtsg(ck)
            
    except Exception as e:
        print(f"Lỗi: {e}")
        return None, None, None, None, None, None

def get_info(uid: str, cookie: str, fb_dtsg: str, a: str, req: str, rev: str) -> Dict[str, Any]:
    try:
        form = {
            "ids[0]": uid,
            "fb_dtsg": fb_dtsg,
            "__a": a,
            "__req": req,
            "__rev": rev
        }
        
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': cookie,
            'Origin': 'https://www.facebook.com',
            'Referer': 'https://www.facebook.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        
        response = requests.post(
            "https://www.facebook.com/chat/user_info/",
            headers=headers,
            data=form
        )
        
        if response.status_code != 200:
            return {"error": f"Lỗi Kết Nối: {response.status_code}"}
        
        try:
            text_response = response.text
            if text_response.startswith("for (;;);"):
                text_response = text_response[9:]
            
            res_data = json.loads(text_response)
            
            if "error" in res_data:
                return {"error": res_data.get("error")}
            
            if "payload" in res_data and "profiles" in res_data["payload"]:
                return format_data(res_data["payload"]["profiles"])
            else:
                return {"error": f"Không Tìm Thấy Thông Tin Của {uid}"}
                
        except json.JSONDecodeError:
            return {"error": "Lỗi Khi Phân Tích JSON"}
            
    except Exception as e:
        print(f"Lỗi Khi Get Info: {e}")
        return {"error": str(e)}

def format_data(profiles):
    if not profiles:
        return {"error": "Không Có Data"}
    
    first_profile_id = next(iter(profiles))
    profile = profiles[first_profile_id]
    
    return {
        "id": first_profile_id,
        "name": profile.get("name", ""),
        "url": profile.get("url", ""),
        "thumbSrc": profile.get("thumbSrc", ""),
        "gender": profile.get("gender", "")
    }

def cmt_gr_pst(cookie, grid, postIDD, ctn, user_id, fb_dtsg, rev, req, a, jazoest, uidtag=None, nametag=None):
    try:
        if not all([user_id, fb_dtsg, jazoest]):
            print("Thiếu user_id, fb_dtsg hoặc jazoest")
            return False
            
        pstid_enc = base64.b64encode(f"feedback:{postIDD}".encode()).decode()
        
        client_mutation_id = str(round(random.random() * 19))
        session_id = get_guid()  
        crt_time = int(time.time() * 1000)
        
        variables = {
            "feedLocation": "DEDICATED_COMMENTING_SURFACE",
            "feedbackSource": 110,
            "groupID": grid,
            "input": {
                "client_mutation_id": client_mutation_id,
                "actor_id": user_id,
                "attachments": None,
                "feedback_id": pstid_enc,
                "formatting_style": None,
                "message": {
                    "ranges": [],
                    "text": ctn
                },
                "attribution_id_v2": f"SearchCometGlobalSearchDefaultTabRoot.react,comet.search_results.default_tab,tap_search_bar,{crt_time},775647,391724414624676,,",
                "vod_video_timestamp": None,
                "is_tracking_encrypted": True,
                "tracking": [],
                "feedback_source": "DEDICATED_COMMENTING_SURFACE",
                "session_id": session_id
            },
            "inviteShortLinkKey": None,
            "renderLocation": None,
            "scale": 3,
            "useDefaultActor": False,
            "focusCommentID": None,
            "__relay_internal__pv__IsWorkUserrelayprovider": False
        }
        
        if uidtag and nametag:
            name_position = ctn.find(nametag)
            if name_position != -1:
                variables["input"]["message"]["ranges"] = [
                    {
                        "entity": {
                            "id": uidtag
                        },
                        "length": len(nametag),
                        "offset": name_position
                    }
                ]
            
        payload = {
            'av': user_id,
            '__crn': 'comet.fbweb.CometGroupDiscussionRoute',
            'fb_dtsg': fb_dtsg,
            'jazoest': jazoest,
            'fb_api_caller_class': 'RelayModern',
            'fb_api_req_friendly_name': 'useCometUFICreateCommentMutation',
            'variables': json.dumps(variables),
            'server_timestamps': 'true',
            'doc_id': '24323081780615819'
        }
        
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'identity',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': cookie,
            'Origin': 'https://www.facebook.com',
            'Referer': f'https://www.facebook.com/groups/{grid}',
            'User-Agent': 'python-http/0.27.0'
        }
        
        response = requests.post('https://www.facebook.com/api/graphql', data=payload, headers=headers)
        print(f"Mã trạng thái cho bài {postIDD}: {response.status_code}")
        print(f"Phản hồi: {response.text[:500]}...")  
        
        if response.status_code == 200:
            try:
                json_response = response.json()
                if 'errors' in json_response:
                    print(f"Lỗi GraphQL: {json_response['errors']}")
                    return False
                if 'data' in json_response and 'comment_create' in json_response['data']:
                    print("Bình luận đã được đăng")
                    return True
                print("Không tìm thấy comment_create trong phản hồi")
                return False
            except ValueError:
                print("Phản hồi JSON không hợp lệ")
                return False
        else:
            return False
    except Exception as e:
        print(f"Lỗi khi gửi bình luận: {e}")
        return False

def extract_post_group_id(post_link):
    post_match = re.search(r'facebook\.com/.+/permalink/(\d+)', post_link)
    group_match = re.search(r'facebook\.com/groups/(\d+)', post_link)
    if not post_match or not group_match:
        return None, None
    return post_match.group(1), group_match.group(1)
 
@tree.command(name="nhaynamebox", description="Treo đổi tên box Messenger theo file nhay.txt")
@app_commands.describe(
    cookie="Cookie Facebook",
    box_id="ID hộp chat (thread ID)",
    delay="Delay giữa mỗi lần đổi tên (giây)"
)
async def nhaynamebox(
    interaction: discord.Interaction,
    cookie: str,
    box_id: str,
    delay: float
):
    if not is_authorized(interaction) and not is_admin(interaction):
        return await safe_send(interaction, "Bạn không có quyền dùng lệnh này", ephemeral=True)

    # Defer ngay để tránh lỗi interaction timeout
    await interaction.response.defer(thinking=True, ephemeral=True)

    # Đọc file nhay.txt
    try:
        with open("nhay.txt", "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return await interaction.followup.send("❌ Không tìm thấy file `nhay.txt`!", ephemeral=True)

    if not lines:
        return await interaction.followup.send("❌ File `nhay.txt` không có nội dung!", ephemeral=True)

    try:
        from toolnamebox import dataGetHome, tenbox
    except ImportError:
        return await interaction.followup.send("❌ Không thể import module `toolnamebox`!", ephemeral=True)

    dataFB = dataGetHome(cookie)
    stop_event = threading.Event()
    discord_user_id = str(interaction.user.id)
    start_time = datetime.now()

    # Worker spam đổi tên liên tục
    def nhayname_worker():
        index = 0
        while not stop_event.is_set():
            new_title = lines[index % len(lines)]
            index += 1

            success, log = tenbox(new_title, box_id, dataFB)
            print(log)

            for _ in range(int(delay)):
                if stop_event.is_set():
                    return
                time.sleep(1)
            if stop_event.is_set():
                return
            time.sleep(delay - int(delay))

    # Tạo thread riêng cho mỗi user
    th = threading.Thread(target=nhayname_worker, daemon=True)

    with NHAYNAMEBOX_LOCK:
        if discord_user_id not in user_nhaynamebox_tabs:
            user_nhaynamebox_tabs[discord_user_id] = []
        user_nhaynamebox_tabs[discord_user_id].append({
            "thread": th,
            "stop_event": stop_event,
            "start": start_time,
            "box_id": box_id,
            "delay": delay
        })

    th.start()

    await interaction.followup.send(
        f"✅ Đã bắt đầu spam đổi tên box Messenger cho <@{discord_user_id}>:\n"
        f"• BoxID: `{box_id}`\n"
        f"• Delay: `{delay}` giây\n"
        f"• Số dòng tên: `{len(lines)}`\n"
        f"• Bắt đầu: `{start_time.strftime('%Y-%m-%d %H:%M:%S')}`",
        ephemeral=True
    )
    
@tree.command(name="tabnhaynamebox", description="Quản lý/dừng tab đổi tên box Messenger")
async def tabnhaynamebox(interaction: discord.Interaction):
    if not is_authorized(interaction) and not is_admin(interaction):
        return await safe_send(interaction, "Bạn không có quyền dùng lệnh này", ephemeral=True)

    discord_user_id = str(interaction.user.id)
    with NHAYNAMEBOX_LOCK:
        tabs = user_nhaynamebox_tabs.get(discord_user_id, [])

    if not tabs:
        return await safe_send(interaction, "❌ Bạn không có tab đổi tên nào đang hoạt động.", ephemeral=True)

    msg = "**Danh sách tab đổi tên box của bạn:**\n"
    for idx, tab in enumerate(tabs, 1):
        uptime = get_uptime(tab["start"])
        msg += f"{idx}. BoxID: `{tab['box_id']}` | Delay: `{tab['delay']}`s | Uptime: `{uptime}`\n"
    msg += "\n➡️ Nhập số thứ tự của tab bạn muốn **dừng**."

    await interaction.response.send_message(msg, ephemeral=True)

    def check(m: discord.Message):
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

    try:
        reply = await bot.wait_for("message", check=check, timeout=30.0)
    except asyncio.TimeoutError:
        return await interaction.followup.send("⏱️ Hết thời gian. Không dừng tab nào.", ephemeral=True)

    c = reply.content.strip()
    if not c.isdigit():
        return await interaction.followup.send("⚠️ Không hợp lệ. Không dừng tab nào.", ephemeral=True)
    i = int(c)
    if not (1 <= i <= len(tabs)):
        return await interaction.followup.send("⚠️ Số không hợp lệ.", ephemeral=True)

    with NHAYNAMEBOX_LOCK:
        chosen = tabs.pop(i - 1)
        chosen["stop_event"].set()
        if not tabs:
            del user_nhaynamebox_tabs[discord_user_id]

    await interaction.followup.send(f"⛔ Đã dừng tab đổi tên số `{i}`", ephemeral=True)

class Mention:
    thread_id = None
    offset = None
    length = None

    def __init__(self, thread_id, offset, length):
        self.thread_id = thread_id
        self.offset = offset
        self.length = length

    @classmethod
    def _from_range(cls, data):
        return cls(
            thread_id=data["entity"].get("id"),
            offset=data["offset"],
            length=data["length"],
        )

    @classmethod
    def _from_prng(cls, data):
        return cls(thread_id=data["i"], offset=data["o"], length=data["l"])

    def _to_send_data(self, i):
        return {
            f"profile_xmd[{i}][id]": self.thread_id,
            f"profile_xmd[{i}][offset]": self.offset,
            f"profile_xmd[{i}][length]": self.length,
            f"profile_xmd[{i}][type]": "p",
        }

def get_auth_tokens(ck):
    try:
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
            'Connection': 'keep-alive',
            'Cookie': ck,
            'Host': 'www.facebook.com',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }

        response = requests.get('https://www.facebook.com/', headers=headers)

        if response.status_code != 200:
            return None, None, None, None, None, None

        html = response.text

        user_id = re.search(r'"USER_ID":"(\d+)"', html)
        user_id = user_id.group(1) if user_id else None

        fb_dtsg = re.search(r'\["DTSGInitData",\[],{"token":"(.*?)"}', html)
        fb_dtsg = fb_dtsg.group(1) if fb_dtsg else None

        rev = re.search(r'"client_revision":(\d+),', html)
        rev = rev.group(1) if rev else None

        a = "1"
        req = "1b"
        jazoest = re.search(r'name="jazoest" value="(\d+)"', html)
        jazoest = jazoest.group(1) if jazoest else "265817"

        return user_id, fb_dtsg, rev, req, a, jazoest
    except Exception as e:
        print(f"Lỗi get_auth_tokens: {e}")
        return None, None, None, None, None, None

def fetch_user_info(uid: str, cookie: str) -> Dict[str, Any]:
    try:
        user_id, fb_dtsg, rev, req, a, jazoest = get_auth_tokens(cookie)
        
        if not all([user_id, fb_dtsg]):
            return {"error": "Không thể lấy thông tin xác thực. Cookie có thể đã hết hạn."}
        
        form = {
            "ids[0]": uid,
            "fb_dtsg": fb_dtsg,
            "__a": a,
            "__req": req,
            "__rev": rev
        }
        
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9,vi;q=0.8',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': cookie,
            'Origin': 'https://www.facebook.com',
            'Referer': 'https://www.facebook.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }
        
        response = requests.post(
            "https://www.facebook.com/chat/user_info/",
            headers=headers,
            data=form
        )
        
        if response.status_code != 200:
            return {"error": f"Lỗi kết nối: {response.status_code}"}
        
        try:
            text_response = response.text
            if text_response.startswith("for (;;);"):
                text_response = text_response[9:]
            
            res_data = json.loads(text_response)
            
            if "error" in res_data:
                return {"error": res_data.get("error")}
            
            if "payload" in res_data and "profiles" in res_data["payload"]:
                return format_data(res_data["payload"]["profiles"])
            else:
                return {"error": "Không tìm thấy thông tin người dùng"}
                
        except json.JSONDecodeError:
            return {"error": "Lỗi khi phân tích dữ liệu JSON"}
            
    except Exception as e:
        print(f"Lỗi fetch_user_info: {e}")
        return {"error": str(e)}

def format_data(profiles):
    if not profiles:
        return {"error": "Không Có Data"}
    
    first_profile_id = next(iter(profiles))
    profile = profiles[first_profile_id]
    
    return {
        "id": first_profile_id,
        "name": profile.get("name", ""),
        "url": profile.get("url", ""),
        "thumbSrc": profile.get("thumbSrc", ""),
        "gender": profile.get("gender", "")
    }

def send_messages(user_id, fb_dtsg, rev, req, a, ck, idbox, uid, name, delay):
    if not os.path.exists("nhay.txt"):
        print("❌ Không tìm thấy file nhay.txt")
        return

    with open("nhay.txt", "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Cookie': ck,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': 'https://www.facebook.com',
        'Referer': f'https://www.facebook.com/messages/t/{idbox}'
    }

    count = 0
    while True:
        for line in lines:
            tag_name = f"@{name}"
            if random.choice([True, False]):
                body = f"{tag_name} {line}"
                offset = 0
            else:
                body = f"{line} {tag_name}"
                offset = len(line) + 1

            mention = Mention(thread_id=uid, offset=offset, length=len(tag_name))
            ts = str(int(time.time() * 1000))

            payload = {
                "thread_fbid": idbox,
                "action_type": "ma-type:user-generated-message",
                "body": body,
                "client": "mercury",
                "author": f"fbid:{user_id}",
                "timestamp": ts,
                "offline_threading_id": ts,
                "message_id": ts,
                "source": "source:chat:web",
                "ephemeral_ttl_mode": "0",
                "__user": user_id,
                "__a": a,
                "__req": req,
                "__rev": rev,
                "fb_dtsg": fb_dtsg,
                "source_tags[0]": "source:chat"
            }

            payload.update(mention._to_send_data(0))

            try:
                response = requests.post("https://www.facebook.com/messaging/send/", headers=headers, data=payload)
                if response.status_code == 200:
                    count += 1
                    print(f"[✔] Đã gửi ({count}): {body}")
                else:
                    print(f"[✘] Lỗi ({response.status_code}): {response.text}")
            except Exception as e:
                print(f"Lỗi gửi tin nhắn: {e}")

            time.sleep(delay)
                        
class NhayTagModal(discord.ui.Modal, title="Điền thông tin"):
    cookie = discord.ui.TextInput(
        label="Cookie Facebook",
        style=discord.TextStyle.paragraph,
        required=True
    )
    idbox = discord.ui.TextInput(
        label="ID Box / Chat 1-1",
        required=True
    )
    uidtag = discord.ui.TextInput(
        label="UID tag",
        placeholder="Nhập nhiều UID, cách nhau bằng dấu phẩy (tùy chọn)",
        required=False
    )
    delay = discord.ui.TextInput(
        label="Delay (giây)",
        required=True,
        placeholder="Ví dụ: 2"
    )

    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        cookie = self.cookie.value
        idbox = self.idbox.value
        uidtag = self.uidtag.value
        delay = float(self.delay.value)

        if not is_authorized(interaction) and not is_admin(interaction):
            embed_no_perm = discord.Embed(
                title="❌ Không có quyền",
                description="Bạn không có quyền dùng lệnh này",
                color=discord.Color.red()
            )
            return await interaction.followup.send(embed=embed_no_perm)

        try:
            with open("nhay1.txt", "r", encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            embed_file_err = discord.Embed(
                title="❌ File không tìm thấy",
                description="Không tìm thấy file `nhay1.txt`",
                color=discord.Color.red()
            )
            return await interaction.followup.send(embed=embed_file_err)

        if not lines:
            embed_empty = discord.Embed(
                title="❌ File rỗng",
                description="File `nhay1.txt` không có nội dung!",
                color=discord.Color.red()
            )
            return await interaction.followup.send(embed=embed_empty)

        try:
            user_id, fb_dtsg, rev, req, a, jazoest = get_auth_tokens(cookie)
        except Exception as e:
            embed_auth_err = discord.Embed(
                title="❌ Lỗi lấy token Facebook",
                description=str(e),
                color=discord.Color.red()
            )
            return await interaction.followup.send(embed=embed_auth_err)

        if not all([user_id, fb_dtsg]):
            embed_invalid_cookie = discord.Embed(
                title="❌ Cookie không hợp lệ",
                description="Cookie không hợp lệ hoặc đã hết hạn.",
                color=discord.Color.red()
            )
            return await interaction.followup.send(embed=embed_invalid_cookie)

        uid_list = [u.strip() for u in uidtag.split(",") if u.strip()]
        user_infos = {}
        for u in uid_list:
            info = fetch_user_info(u, cookie)
            if "error" in info:
                embed_fetch_err = discord.Embed(
                    title="❌ Lỗi fetch UID",
                    description=info["error"],
                    color=discord.Color.red()
                )
                return await interaction.followup.send(embed=embed_fetch_err)
            user_infos[u] = info.get("name", "Người dùng")

        stop_event = threading.Event()
        discord_user_id = str(interaction.user.id)
        start_time = datetime.now()

        def nhaytag_worker():
            count = 0
            while not stop_event.is_set():
                for line in lines:
                    if stop_event.is_set():
                        break

                    body = line
                    mentions = {}
                    offset = len(body)

                    for uid in uid_list:
                        tag_name = user_infos[uid]
                        body += f" @{tag_name}"
                        mentions[uid] = (offset, len(tag_name))
                        offset += len(tag_name) + 2

                    ts = str(int(time.time() * 1000))
                    payload = {
                        "thread_fbid": idbox,
                        "action_type": "ma-type:user-generated-message",
                        "body": body,
                        "client": "mercury",
                        "author": f"fbid:{user_id}",
                        "timestamp": ts,
                        "offline_threading_id": ts,
                        "message_id": ts,
                        "source": "source:chat:web",
                        "ephemeral_ttl_mode": "0",
                        "__user": user_id,
                        "__a": a,
                        "__req": req,
                        "__rev": rev,
                        "fb_dtsg": fb_dtsg,
                        "source_tags[0]": "source:chat"
                    }

                    idx = 0
                    for uid, (start, length) in mentions.items():
                        mention = Mention(thread_id=uid, offset=start, length=length)
                        payload.update(mention._to_send_data(idx))
                        idx += 1

                    headers = {
                        "User-Agent": "Mozilla/5.0",
                        "Cookie": cookie,
                        "Content-Type": "application/x-www-form-urlencoded",
                        "Origin": "https://www.facebook.com",
                        "Referer": f"https://www.facebook.com/messages/t/{idbox}"
                    }

                    try:
                        res = requests.post("https://www.facebook.com/messaging/send/", headers=headers, data=payload)
                        if res.status_code == 200:
                            count += 1
                            print(f"[✓] Gửi #{count}: {body}")
                        else:
                            print(f"[×] Lỗi ({res.status_code})")
                    except Exception as e:
                        print(f"[!] Lỗi gửi: {e}")

                    for _ in range(int(delay)):
                        if stop_event.is_set():
                            return
                        time.sleep(1)
                    if stop_event.is_set():
                        return
                    time.sleep(delay - int(delay))

        th = threading.Thread(target=nhaytag_worker, daemon=True)

        with NHAYTAG_LOCK:
            if discord_user_id not in user_nhaytag_tabs:
                user_nhaytag_tabs[discord_user_id] = []
            user_nhaytag_tabs[discord_user_id].append({
                "thread": th,
                "stop_event": stop_event,
                "start": start_time,
                "idbox": idbox,
                "uid": uid_list,
                "delay": delay
            })

        th.start()

        embed = discord.Embed(
            title="✅ Đã bắt đầu spam mess",
            description=f"Task spam của <@{discord_user_id}> đã được khởi tạo.",
            color=discord.Color.green(),
            timestamp=start_time
        )
        embed.add_field(name="• Box/Chat", value=idbox, inline=True)
        embed.add_field(name="• Số UID tag", value=len(uid_list), inline=True)
        embed.add_field(name="• Delay", value=f"{delay} giây", inline=True)
        embed.set_footer(text="Bắt đầu lúc")

        await interaction.followup.send(embed=embed)




class NhayTagView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Start", style=discord.ButtonStyle.secondary, emoji="🚀")
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(NhayTagModal(interaction))


@tree.command(name="nhaytagmess", description="Spam Messenger có thể tag nhiều UID hoặc chat riêng 1-1")
async def nhaytagmess(interaction: discord.Interaction):
    if not is_authorized(interaction) and not is_admin(interaction):
        embed = discord.Embed(
            title="🚫 Không có quyền",
            description=f"Bạn không có quyền sử dụng lệnh này, vui lòng liên hệ <@{admin_id}>.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    embed = discord.Embed(
        title="📢 Nhây Tag Messenger VIP",
        description=(
            "Ấn vào nút để bắt đầu điền thông tin"
        ),
        color=discord.Color.green()
    )
    embed.set_footer(text="Nhây Messenger đa tag độc quyền by Minh Quân")

    view = NhayTagView()
    await interaction.response.send_message(embed=embed, view=view)
    

@tree.command(name="tabnhaytagmess", description="Quản lý/dừng tab spam tag Messenger")
async def tabnhaytagmess(interaction: discord.Interaction):
    if not is_authorized(interaction) and not is_admin(interaction):
        return await safe_send(interaction, "Bạn không có quyền dùng lệnh này")

    discord_user_id = str(interaction.user.id)
    with NHAYTAG_LOCK:
        tabs = user_nhaytag_tabs.get(discord_user_id, [])

    if not tabs:
        embed = discord.Embed(
            title="❌ Không có tab nhây tag mess nào đang chạy",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    # Embed danh sách tab
    embed = discord.Embed(
        title="📋 Danh sách tab spam tag đang chạy",
        description="Nhập **số thứ tự** để dừng tab.\nNhập `All` để **dừng tất cả tab**.",
        color=discord.Color.blurple()
    )

    for idx, tab in enumerate(tabs, 1):
        uptime = get_uptime(tab["start"])
        embed.add_field(
            name=f"Tab #{idx}",
            value=(
                f"**Box:** `{tab['idbox']}`\n"
                f"**UID tag:** `{tab['uid']}`\n"
                f"**Delay:** `{tab['delay']}s`\n"
                f"**Uptime:** `{uptime}`"
            ),
            inline=False
        )

    await interaction.response.send_message(embed=embed)

    def check(m: discord.Message):
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

    try:
        reply = await bot.wait_for("message", check=check, timeout=30.0)
    except asyncio.TimeoutError:
        timeout_embed = discord.Embed(
            title="⏱️ Hết thời gian",
            description="Không dừng tab nào.",
            color=discord.Color.orange()
        )
        return await interaction.followup.send(embed=timeout_embed)

    c = reply.content.strip()

    # Trường hợp dừng tất cả
    if c.lower() == "all":
        with NHAYTAG_LOCK:
            for tab in list(tabs):
                tab["stop_event"].set()
            user_nhaytag_tabs.pop(discord_user_id, None)

        done_embed = discord.Embed(
            title="⛔ Đã dừng tất cả tab nhây tag",
            color=discord.Color.red()
        )
        return await interaction.followup.send(embed=done_embed)

    # Trường hợp dừng 1 tab
    if not c.isdigit():
        invalid_embed = discord.Embed(
            title="⚠️ Không hợp lệ",
            description="Bạn cần nhập số thứ tự hoặc `All`.",
            color=discord.Color.orange()
        )
        return await interaction.followup.send(embed=invalid_embed)

    i = int(c)
    if not (1 <= i <= len(tabs)):
        invalid_num_embed = discord.Embed(
            title="⚠️ Số không hợp lệ",
            description="Vui lòng nhập đúng số thứ tự trong danh sách.",
            color=discord.Color.orange()
        )
        return await interaction.followup.send(embed=invalid_num_embed)

    with NHAYTAG_LOCK:
        chosen = tabs.pop(i - 1)
        chosen["stop_event"].set()
        if not tabs:
            del user_nhaytag_tabs[discord_user_id]

    done_one_embed = discord.Embed(
        title="⛔ Đã dừng tab spam tag",
        description=f"Đã dừng tab số `{i}` thành công.",
        color=discord.Color.red()
    )
    await interaction.followup.send(embed=done_one_embed)                                                                                                                                    
@tree.command(
    name="tabnhaytop",
    description="Quản lý/dừng tab nhây top"
)
async def tabnhaytop(interaction: discord.Interaction):
    if not is_authorized(interaction) and not is_admin(interaction):
        return await interaction.response.send_message("Bạn không có quyền sử dụng bot", ephemeral=True)

    discord_user_id = str(interaction.user.id)
    with NHAY_LOCK:
        tabs = user_nhay_tabs.get(discord_user_id, [])

    if not tabs:
        return await interaction.response.send_message("Bạn không có tab nhây top nào đang hoạt động", ephemeral=True)

    msg = "**Danh sách tab nhây top của bạn:**\n"
    for idx, tab in enumerate(tabs, 1):
        uptime = get_uptime(tab["start"])
        msg += (
            f"{idx}. Group:`{tab['group_id']}` Post:`{tab['post_id']}` | "
            f"Delay:`{tab['delay']}`s | Uptime:`{uptime}`\n"
        )
    msg += "\nNhập số tab để dừng tab".format(len(tabs))
    await interaction.response.send_message(msg, ephemeral=True)

    def check(m: discord.Message):
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

    try:
        reply = await bot.wait_for("message", check=check, timeout=30.0)
    except asyncio.TimeoutError:
        return await interaction.followup.send("Hết thời gian. Không dừng tab nào", ephemeral=True)

    c = reply.content.strip()
    if not c.isdigit():
        return await interaction.followup.send("Không dừng tab nào", ephemeral=True)
    i = int(c)
    if not (1 <= i <= len(tabs)):
        return await interaction.followup.send("Số không hợp lệ", ephemeral=True)

    with NHAY_LOCK:
        chosen = tabs.pop(i-1)
        chosen["stop_event"].set()
        if not tabs:
            del user_nhay_tabs[discord_user_id]

    await interaction.followup.send(f"Đã dừng tab nhây số {i}", ephemeral=True)   
    
def telegram_send_loop(token, chat_ids, caption, photo, delay, stop_event, discord_user_id):
    while not stop_event.is_set():
        for chat_id in chat_ids:
            if stop_event.is_set():
                break
            try:
                if photo:
                    if photo.startswith("http"):
                        url = f"https://api.telegram.org/bot{token}/sendPhoto"
                        data = {"chat_id": chat_id, "caption": caption, "photo": photo}
                        resp = requests.post(url, data=data, timeout=10)
                    else:
                        url = f"https://api.telegram.org/bot{token}/sendPhoto"
                        with open(photo, "rb") as f:
                            files = {"photo": f}
                            data = {"chat_id": chat_id, "caption": caption}
                            resp = requests.post(url, data=data, files=files, timeout=10)
                else:
                    url = f"https://api.telegram.org/bot{token}/sendMessage"
                    data = {"chat_id": chat_id, "text": caption}
                    resp = requests.post(url, data=data, timeout=10)

                if resp.status_code == 200:
                    print(f"[TELE][{discord_user_id}] {token[:10]}... → {chat_id}")
                elif resp.status_code == 429:
                    retry = resp.json().get("parameters", {}).get("retry_after", 10)
                    print(f"[TELE][{discord_user_id}] Rate limit {retry}s")
                    time.sleep(retry)
                else:
                    print(f"[TELE][{discord_user_id}] Err {resp.status_code}: {resp.text[:100]}")
            except Exception as e:
                print(f"[TELE][{discord_user_id}] Conn Err: {e}")
            time.sleep(0.2)
        time.sleep(delay)           

def _ig_spam_loop(task_id, discord_user_id):
    with IG_LOCK:
        task = next((t for t in SPAM_TASKS[discord_user_id] if t["id"] == task_id), None)
    if not task:
        return

    cl       = task["client"]
    targets  = task["targets"]
    message  = task["message"]
    delay    = task["delay"]
    stop_set = task["stop_targets"]

    while True:
        for target in targets:
            if target in stop_set:
                continue
            try:
                if target.isdigit():
                    cl.direct_send(message, thread_ids=[target])
                else:
                    uid = cl.user_id_from_username(target)
                    cl.direct_send(message, thread_ids=[uid])
                print(f"[IG][{discord_user_id}] Gửi tới {target}")
            except Exception as e:
                print(f"[IG][{discord_user_id}] Lỗi {target}: {e}")
        time.sleep(delay)           

def parse_gmail_accounts(input_str: str):
    accounts = []
    for entry in re.split(r"[,/]", input_str):
        if "|" in entry:
            email, pwd = entry.split("|",1)
            accounts.append({
                "server": "smtp.gmail.com",
                "port": 465,
                "email": email.strip(),
                "password": pwd.strip(),
                "active": True
            })
    return accounts

def send_mail(smtp_info, to_email, content):
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_info["server"], smtp_info["port"], context=context) as server:
        server.login(smtp_info["email"], smtp_info["password"])
        msg = MIMEText(content)
        msg["From"] = smtp_info["email"]
        msg["To"] = to_email
        msg["Subject"] = " "
        server.sendmail(smtp_info["email"], to_email, msg.as_string())

def gmail_spam_loop(tab, discord_user_id):
    smtp_list = tab["smtp_list"]
    to_email  = tab["to_email"]
    content   = tab["content"]
    delay     = tab["delay"]
    stop_evt  = tab["stop_event"]
    idx = 0
    while not stop_evt.is_set():
        active = [acc for acc in smtp_list if acc["active"]]
        if not active:
            for acc in smtp_list: acc["active"] = True
            active = smtp_list
        smtp = active[idx % len(active)]
        try:
            send_mail(smtp, to_email, content)
            print(f"[GMAIL][{discord_user_id}] ✓ {smtp['email']} → {to_email}")
        except smtplib.SMTPAuthenticationError:
            smtp["active"] = False
            print(f"[GMAIL][{discord_user_id}] ✗ Auth failed {smtp['email']}")
        except smtplib.SMTPDataError as e:
            txt = str(e)
            if "Quota" in txt or "limit" in txt:
                smtp["active"] = False
                print(f"[GMAIL][{discord_user_id}] Quota limit {smtp['email']}")
            else:
                print(f"[GMAIL][{discord_user_id}] DataErr {smtp['email']}: {e}")
        except Exception as e:
            print(f"[GMAIL][{discord_user_id}] Err {smtp['email']}: {e}")
        idx += 1
        for _ in range(int(delay)):
            if stop_evt.is_set(): break
            time.sleep(1)
        if stop_evt.is_set(): break
        time.sleep(delay - int(delay))      
                   
def get_uptime(start_time: datetime) -> str:
    elapsed = (datetime.now() - start_time).total_seconds()
    hours, rem = divmod(int(elapsed), 3600)
    minutes, seconds = divmod(rem, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

@tasks.loop(minutes=60)
async def cleanup_expired_users():
    users = load_users()
    to_remove = []
    for uid, exp in users.items():
        if exp and datetime.fromisoformat(exp) <= datetime.now():
            to_remove.append(uid)
    if to_remove:
        for uid in to_remove:
            _remove_user_and_kill_tabs(uid)

class Kem:
    def __init__(self, cookie):
        self.cookie = cookie
        self.user_id = self.id_user()
        self.fb_dtsg = None
        self.init_params()

    def id_user(self):
        try:
            c_user = re.search(r"c_user=(\d+)", self.cookie).group(1)
            return c_user
        except:
            raise Exception("Cookie không hợp lệ")

    def init_params(self):
        headers = {
            'Cookie': self.cookie,
            'User-Agent': 'Mozilla/5.0',
            'Accept': '*/*',
        }
        try:
            response = requests.get('https://www.facebook.com', headers=headers)
            fb_dtsg_match = re.search(r'"token":"(.*?)"', response.text)
            if not fb_dtsg_match:
                response = requests.get('https://mbasic.facebook.com', headers=headers)
                fb_dtsg_match = re.search(r'name="fb_dtsg" value="(.*?)"', response.text)
                if not fb_dtsg_match:
                    response = requests.get('https://m.facebook.com', headers=headers)
                    fb_dtsg_match = re.search(r'name="fb_dtsg" value="(.*?)"', response.text)
            if fb_dtsg_match:
                self.fb_dtsg = fb_dtsg_match.group(1)
            else:
                raise Exception("Không thể lấy được fb_dtsg")
        except Exception as e:
            raise Exception(f"Lỗi khi khởi tạo tham số: {str(e)}")

    def gui_tn(self, recipient_id, message):
        if not message or not recipient_id:
            raise ValueError("ID Box và Nội Dung không được để trống")
        timestamp = int(time.time() * 1000)
        data = {
            'thread_fbid': recipient_id,
            'action_type': 'ma-type:user-generated-message',
            'body': message,
            'client': 'mercury',
            'author': f'fbid:{self.user_id}',
            'timestamp': timestamp,
            'source': 'source:chat:web',
            'offline_threading_id': str(timestamp),
            'message_id': str(timestamp),
            'ephemeral_ttl_mode': '',
            '__user': self.user_id,
            '__a': '1',
            '__req': '1b',
            '__rev': '1015919737',
            'fb_dtsg': self.fb_dtsg
        }
        headers = {
            'Cookie': self.cookie,
            'User-Agent': 'python-http/0.27.0',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        try:
            response = requests.post('https://www.facebook.com/messaging/send/', data=data, headers=headers)
            if response.status_code != 200:
                return {'success': False, 'error_description': f'Status: {response.status_code}'}
            if 'for (;;);' in response.text:
                clean = response.text.replace('for (;;);', '')
                result = json.loads(clean)
                if 'error' in result:
                    return {'success': False, 'error_description': result.get('errorDescription', 'Unknown error')}
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error_description': str(e)}

def spam_tab_worker(messenger: Kem, box_id: str, get_message_func, delay: float, stop_event: threading.Event, start_time: datetime, discord_user_id: str):
    success = 0
    fail = 0

    while not stop_event.is_set():
        message = get_message_func()
        result = messenger.gui_tn(box_id, message)
        ok = result.get("success", False)
        if ok:
            success += 1
            status = "OK"
        else:
            fail += 1
            status = f"FAIL: {result.get('error_description', 'Unknown error')}"

        uptime = (datetime.now() - start_time).total_seconds()
        h, rem = divmod(int(uptime), 3600)
        m, s = divmod(rem, 60)
        print(f"[{messenger.user_id}] → {box_id} | {status} | Up: {h:02}:{m:02}:{s:02} | OK: {success} | FAIL: {fail}".ljust(120), end='\r')

        time.sleep(delay)
        gc.collect()

    print(f"\nTab của user {discord_user_id} với cookie {messenger.user_id} đã dừng.")

class TreoMessModal(discord.ui.Modal, title="🚀Treo Messenger"):
    cookie = discord.ui.TextInput(label="🍪 Cookie Facebook", style=discord.TextStyle.paragraph, required=True)
    idbox = discord.ui.TextInput(label="💬 ID Box", style=discord.TextStyle.short, required=True)
    noidung = discord.ui.TextInput(label="📝 Nội dung cần gửi", style=discord.TextStyle.paragraph, required=True)
    delay = discord.ui.TextInput(label="⏳ Delay (giây)", style=discord.TextStyle.short, required=True)

    def __init__(self, interaction: discord.Interaction):
        super().__init__()
        self.interaction = interaction

    async def on_submit(self, interaction: discord.Interaction):
        cookie = self.cookie.value
        idbox = self.idbox.value
        noidung = self.noidung.value

        try:
            delay = float(self.delay.value)
        except:
            embed = discord.Embed(
                title="⚠️ Lỗi nhập dữ liệu",
                description="`Delay` phải là một **số hợp lệ**!",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed)

        discord_user_id = str(interaction.user.id)

        try:
            messenger = Kem(cookie)
        except Exception as e:
            embed = discord.Embed(
                title="❌ Cookie không hợp lệ",
                description=f"Lỗi: `{e}`",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed)

        stop_event = threading.Event()
        start_time = datetime.now()

        th = threading.Thread(
            target=spam_tab_worker,
            args=(messenger, idbox, noidung, delay, stop_event, start_time, discord_user_id),
            daemon=True
        )
        th.start()

        with TAB_LOCK:
            if discord_user_id not in user_tabs:
                user_tabs[discord_user_id] = []
            user_tabs[discord_user_id].append({
                "box_id": idbox,
                "delay": delay,
                "start": start_time,
                "stop_event": stop_event
            })

        short_content = shorten(noidung, width=1900, placeholder="...")

        embed = discord.Embed(
            title="✅ Tạo Tab Thành Công",
            color=discord.Color.green()
        )
        embed.add_field(name="👤 Người thực hiện", value=f"<@{discord_user_id}>", inline=False)
        embed.add_field(name="💬 ID Box", value=f"`{idbox}`", inline=True)
        embed.add_field(name="⏳ Delay", value=f"`{delay}` giây", inline=True)
        embed.add_field(name="📝 Nội dung", value=f"```{short_content}```", inline=False)
        embed.add_field(name="🕒 Bắt đầu", value=f"`{start_time.strftime('%Y-%m-%d %H:%M:%S')}`", inline=False)
        embed.set_footer(text="Hệ thống treo tin nhắn • Thế Giới Ảo", icon_url="https://cdn-icons-png.flaticon.com/512/565/565547.png")

        await interaction.response.send_message(embed=embed)

class TreoMessButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🚀 Bắt đầu treo", style=discord.ButtonStyle.primary)
    async def start_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(TreoMessModal(interaction))


@tree.command(name="treomess", description="Treo tin nhắn Messenger")
async def treomess(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🌐 Treo Messenger",
        description="Bấm nút bên dưới để bắt đầu nhập thông tin treo tin nhắn Messenger.",
        color=discord.Color.blurple()
    )
    embed.set_footer(text="Hệ thống treo tin nhắn • Thế Giới Ảo", icon_url="https://cdn-icons-png.flaticon.com/512/6062/6062645.png")
    await interaction.response.send_message(embed=embed, view=TreoMessButton())



@tree.command(name="tabtreomess", description="📊 Quản lý/Dừng tab treo messenger")
async def tabtreomess(interaction: discord.Interaction):
    if not is_authorized(interaction) and not is_admin(interaction):
        embed = discord.Embed(
            title="❌ Không có quyền",
            description="Bạn không có quyền sử dụng lệnh này.",
            color=0xe74c3c
        )
        return await interaction.response.send_message(embed=embed)

    discord_user_id = str(interaction.user.id)
    with TAB_LOCK:
        tabs = user_tabs.get(discord_user_id, [])

    if not tabs:
        embed = discord.Embed(
            title="📭 Không có tab treo",
            description="Bạn chưa có tab treo Messenger nào đang hoạt động.",
            color=0xf1c40f
        )
        return await interaction.response.send_message(embed=embed)

    embed = discord.Embed(
        title="📊 Danh sách tab treo Messenger của bạn",
        color=0x3498db
    )
    for idx, tab in enumerate(tabs, start=1):
        uptime = get_uptime(tab["start"])
        embed.add_field(
            name=f"▶️ Tab {idx}",
            value=f"🆔 Box: `{tab['box_id']}`\n"
                  f"⏱ Delay: `{tab['delay']} giây`\n"
                  f"🕒 Uptime: `{uptime}`",
            inline=False
        )
    embed.set_footer(text="🔥 Minh Quân | Pro bot by nmqn8w_")

    view = View(timeout=60)
    for idx, tab in enumerate(tabs, start=1):
        async def stop_callback(inter2: discord.Interaction, i=idx):
            if inter2.user.id != interaction.user.id:
                return await inter2.response.send_message("❌ Không phải tab của bạn.", ephemeral=True)

            with TAB_LOCK:
                chosen = tabs[i-1]
                chosen["stop_event"].set()
                tabs.pop(i-1)
                if not tabs:
                    del user_tabs[discord_user_id]

            stop_embed = discord.Embed(
                title="🛑 Tab đã dừng",
                description=f"Bạn đã dừng **Tab {i}** thành công!",
                color=0xe74c3c
            )
            await inter2.response.edit_message(embed=stop_embed, view=None)

        btn = Button(label=f"Dừng Tab {idx}", style=discord.ButtonStyle.red, emoji="🛑")
        btn.callback = stop_callback
        view.add_item(btn)

    await interaction.response.send_message(embed=embed, view=view)

@tree.command(name="addadmin", description="Thêm user vào danh sách admin phụ")
@app_commands.describe(user="Tag hoặc ID user", thoihan="Thời hạn (ví dụ: 7d , bỏ trống = vĩnh viễn)")
async def addadmin(interaction: discord.Interaction, user: str, thoihan: str = None):
    if not is_admin(interaction):  
        embed = discord.Embed(
            title="🚫 Không có quyền",
            description="Chỉ admin chính mới được dùng lệnh này!",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    user_id = str(user).replace("<@", "").replace(">", "").replace("!", "").strip()

    users = load_users()
    if user_id in users:
        embed = discord.Embed(
            title="⚠️ Lỗi",
            description=f"<@{user_id}> đã có là admin phụ được add.",
            color=discord.Color.orange()
        )
        return await interaction.response.send_message(embed=embed)

    days = None
    if thoihan and thoihan.endswith("d"):
        try:
            days = int(thoihan[:-1])
        except:
            embed = discord.Embed(
                title="⚠️ Thời hạn không hợp lệ",
                description="Phải là số + 'd' (ví dụ: 7d).",
                color=discord.Color.yellow()
            )
            return await interaction.response.send_message(embed=embed)

    _add_user(user_id, days)
    embed = discord.Embed(
        title="✅ Đã thêm admin phụ",
        description=f"Đã thêm <@{user_id}> với quyền sử dụng bot "
                    f"{'vĩnh viễn' if not days else f'{days} ngày'}.",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)


@tree.command(name="xoaadmin", description="Xóa user khỏi danh sách admin phụ")
@app_commands.describe(user="Tag hoặc ID user")
async def xoaadmin(interaction: discord.Interaction, user: str):
    if not is_admin(interaction):  
        embed = discord.Embed(
            title="🚫 Không có quyền",
            description="Chỉ admin chính mới được dùng lệnh này!",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    user_id = str(user).replace("<@", "").replace(">", "").replace("!", "").strip()

    users = load_users()
    if user_id not in users:
        embed = discord.Embed(
            title="⚠️ Lỗi ",
            description=f"<@{user_id}> không phải admin phụ.",
            color=discord.Color.orange()
        )
        return await interaction.response.send_message(embed=embed)

    _remove_user_and_kill_tabs(user_id)

    embed = discord.Embed(
        title="⛔ Đã xóa admin phụ",
        description=f"Đã xóa quyền sử dụng bot và dừng mọi tab của <@{user_id}>.",
        color=discord.Color.red()
    )
    await interaction.response.send_message(embed=embed)



@tree.command(name="listadmin", description="Hiển thị danh sách admin phụ hiện tại")
async def listadmin_cmd(interaction: discord.Interaction):
    if not is_admin(interaction):
        embed = discord.Embed(
            title="🚫 Không có quyền",
            description="Bạn không có quyền sử dụng lệnh này.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    user_list = _get_user_list()
    if not user_list:
        embed = discord.Embed(
            title="📋 Danh sách admin phụ",
            description="Danh sách hiện đang rỗng.",
            color=discord.Color.orange()
        )
        return await interaction.response.send_message(embed=embed)

    await interaction.response.defer(thinking=True)

    embed = discord.Embed(
        title="📋 Danh sách admin phụ",
        color=discord.Color.blurple()
    )
    embed.set_thumbnail(
        url="https://media.discordapp.net/attachments/1443845682254581921/1443852912278376458/standard_1.gif?ex=692a944f&is=692942cf&hm=42f735b7619314e151c6b735621538271fabb0562bcb3e778d4aa7acbb2c59d5&="
    )

    for index, (uid, time_str) in enumerate(user_list, start=1):
        try:
            user_obj = await bot.fetch_user(int(uid))
            name = f"{user_obj.name}#{user_obj.discriminator}"
            mention = user_obj.mention
        except Exception:
            name = f"Unknown User ({uid})"
            mention = f"<@{uid}>"

        embed.add_field(
            name=f"[{index}] 👤 {name}",
            value=f"🔗 {mention}\n⏳ Thời hạn: `{time_str}`",
            inline=False
        )

    await interaction.followup.send(embed=embed)

        

@tree.command(
    name="anhtop",
    description="Treo top ảnh kèm tag"
)
@app_commands.describe(
    link_post="Link bài viết",
    cookie="Cookie",
    message="Nội dung",
    images="Link ảnh",
    delay_min="Delay tối thiểu",
    delay_max="Delay tối đa",
    tag_id="ID cần tag"
)
async def anhtop(
    interaction: discord.Interaction,
    link_post: str,
    cookie: str,
    message: str,
    images: str,
    delay_min: float,
    delay_max: float,
    tag_id: str = None
):
    if not is_authorized(interaction) and not is_admin(interaction):
        return await interaction.response.send_message("Bạn không có quyền sử dụng lệnh này", ephemeral=True)

    post_id = extract_facebook_post_id(link_post)
    if not post_id:
        return await interaction.response.send_message("Không thể lấy ID bài viết từ link", ephemeral=True)

    if not message.strip():
        return await interaction.response.send_message("Nội dung không được để trống", ephemeral=True)

    image_list = [img.strip() for img in images.split(",") if img.strip()]
    if not image_list:
        return await interaction.response.send_message("Phải có ít nhất 1 link ảnh", ephemeral=True)

    if delay_min <= 0 or delay_max <= 0 or delay_min > delay_max:
        return await interaction.response.send_message("Delay không hợp lệ (phải trên 0)", ephemeral=True)

    login = check_login_facebook(cookie)
    if not login:
        return await interaction.response.send_message("Cookie không hợp lệ", ephemeral=True)

    discord_user_id = str(interaction.user.id)
    stop_event = threading.Event()
    start_time = datetime.now()

    th = threading.Thread(
        target=image_tab_worker,
        args=(post_id, cookie, message, image_list, tag_id, delay_min, delay_max, stop_event, start_time, discord_user_id),
        daemon=True
    )
    th.start()

    with IMAGE_TAB_LOCK:
        if discord_user_id not in user_image_tabs:
            user_image_tabs[discord_user_id] = []
        user_image_tabs[discord_user_id].append({
            "post_id": post_id,
            "cookie": cookie,
            "message": message,
            "images": image_list,
            "tag_id": tag_id,
            "delay_min": delay_min,
            "delay_max": delay_max,
            "thread": th,
            "stop_event": stop_event,
            "start": start_time
        })

    await interaction.response.send_message(
        f"Đã khởi tạo tab ảnh top cho <@{discord_user_id}>:\n"
        f"• Post ID: `{post_id}`\n"
        f"• Delay: `{delay_min}–{delay_max}` giây\n"
        f"• Nội dung comment: `{message}`\n"
        f"• Số ảnh: `{len(image_list)}`\n"
        f"{'• Tag ID: ' + tag_id if tag_id else ''}\n"
        f"Thời gian bắt đầu: `{start_time.strftime('%Y-%m-%d %H:%M:%S')}`"
    )
    
@tree.command(name="treoanhmess", description="Spam ảnh + tin nhắn Messenger liên tục")
@app_commands.describe(
    cookie="Cookie Facebook",
    box_id="ID hộp chat (thread ID)",
    image_link="Link ảnh jpg/png",
    message="Nội dung tin nhắn cần gửi (giữ nguyên dòng trắng, khoảng cách)",
    delay="Delay giữa các lần gửi (giây)"
)
async def treoanhmess(
    interaction: discord.Interaction,
    cookie: str,
    box_id: str,
    image_link: str,
    message: str,
    delay: float
):
    if not is_authorized(interaction) and not is_admin(interaction):
        return await safe_send(interaction, "Bạn không có quyền dùng lệnh này", ephemeral=True)

    if delay < 1:
        return await safe_send(interaction, "Delay phải từ 1 giây trở lên.", ephemeral=True)

    stop_event = threading.Event()
    discord_user_id = str(interaction.user.id)
    start_time = datetime.now()

    def treoanhmess_worker():
        try:
            from anhmess import NanhMessenger
            messenger = NanhMessenger(cookie)

            while not stop_event.is_set():
                image_id = messenger.up(image_link)
                if not image_id:
                    print("[×] Upload ảnh thất bại.")
                    continue

                result = messenger.gui_tn(box_id, message, image_id)
                if result.get("success"):
                    print("[✓] Gửi thành công.")
                else:
                    print("[×] Gửi thất bại.")

                for _ in range(int(delay)):
                    if stop_event.is_set(): break
                    time.sleep(1)
                if stop_event.is_set(): break
                time.sleep(delay - int(delay))
        except Exception as e:
            print(f"[LỖI] {e}")

    with IMAGE_TAB_LOCK:
        if discord_user_id not in user_image_tabs:
            user_image_tabs[discord_user_id] = []

        th = threading.Thread(target=treoanhmess_worker, daemon=True)
        user_image_tabs[discord_user_id].append({
            "thread": th,
            "stop_event": stop_event,
            "start": start_time,
            "box_id": box_id,
            "delay": delay,
            "message": message
        })
        th.start()

    await interaction.response.send_message(
        f"Đã tạo tab ảnh Messenger cho <@{discord_user_id}>:\n"
        f"• BoxID: `{box_id}`\n"
        f"• Delay: `{delay}` giây\n"
        f"• Bắt đầu: `{start_time.strftime('%Y-%m-%d %H:%M:%S')}`",
        ephemeral=True
    )
    
@tree.command(name="tabanhmess", description="Quản lý/dừng tab ảnh Messenger đang chạy")
async def tabanhmess(interaction: discord.Interaction):
    if not is_authorized(interaction) and not is_admin(interaction):
        return await safe_send(interaction, "Bạn không có quyền dùng lệnh này", ephemeral=True)

    discord_user_id = str(interaction.user.id)
    with IMAGE_TAB_LOCK:
        tabs = user_image_tabs.get(discord_user_id, [])

    if not tabs:
        return await safe_send(interaction, "Bạn không có tab ảnh Messenger nào đang hoạt động", ephemeral=True)

    msg = "**Danh sách tab ảnh Messenger của bạn:**\n"
    for idx, tab in enumerate(tabs, 1):
        uptime = get_uptime(tab["start"])
        msg += (
            f"{idx}. BoxID: `{tab['box_id']}` | "
            f"Delay: `{tab['delay']}`s | Uptime: `{uptime}`\n"
        )
    msg += "\n➡️ Nhập số thứ tự của tab bạn muốn **dừng** (1 - {})".format(len(tabs))

    await interaction.response.send_message(msg, ephemeral=True)

    def check(m: discord.Message):
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

    try:
        reply = await bot.wait_for("message", check=check, timeout=30.0)
    except asyncio.TimeoutError:
        return await interaction.followup.send("⏱️ Hết thời gian. Không dừng tab nào.", ephemeral=True)

    c = reply.content.strip()
    if not c.isdigit():
        return await interaction.followup.send("⚠️ Không hợp lệ. Không dừng tab nào.", ephemeral=True)
    i = int(c)
    if not (1 <= i <= len(tabs)):
        return await interaction.followup.send("⚠️ Số không hợp lệ.", ephemeral=True)

    with IMAGE_TAB_LOCK:
        chosen = tabs.pop(i - 1)
        chosen["stop_event"].set()
        if not tabs:
            del user_image_tabs[discord_user_id]

    await interaction.followup.send(f"⛔ Đã dừng tab ảnh số `{i}`", ephemeral=True)            
@tree.command(name="listbox", description="Liệt kê toàn bộ box Messenger từ cookie")
@app_commands.describe(
    cookie="Cookie Facebook cần kiểm tra"
)
async def listbox(interaction: discord.Interaction, cookie: str):
    if not is_authorized(interaction) and not is_admin(interaction):
        return await safe_send(interaction, "Bạn không có quyền dùng lệnh này", ephemeral=True)

    await interaction.response.send_message("🔍 Đang lấy danh sách box Messenger...", ephemeral=True)

    result = get_thread_list(cookie)

    if isinstance(result, dict) and "error" in result:
        return await interaction.followup.send(f"❌ {result['error']}", ephemeral=True)

    if not result:
        return await interaction.followup.send("❌ Không tìm thấy box nào.", ephemeral=True)

    CHUNK_SIZE = 30  # tối đa 30 box mỗi lần gửi
    chunks = [result[i:i + CHUNK_SIZE] for i in range(0, len(result), CHUNK_SIZE)]

    for idx, chunk in enumerate(chunks, 1):
        msg = f"📦 **Danh sách box ({(idx - 1) * CHUNK_SIZE + 1} - {min(idx * CHUNK_SIZE, len(result))})**\n"
        for i, thread in enumerate(chunk, start=(idx - 1) * CHUNK_SIZE + 1):
            name = thread['thread_name']
            tid = thread['thread_id']
            msg += f"{i}. {name} — `{tid}`\n"
        await interaction.followup.send(msg[:2000], ephemeral=True)
            
@tree.command(name="nhayzalo", description="Nhây zalo fake soạn")
@app_commands.describe(
    imei="IMEI Zalo",
    cookie="Cookie Zalo",
    delay="Delay giây",
    kieu="1=group, 2=1-1"
)
async def nhayzalo(interaction: discord.Interaction, imei: str, cookie: str, delay: float, kieu: int):
    if not is_authorized(interaction) and not is_admin(interaction):
        return await safe_send(interaction, "❌ Bạn không có quyền", ephemeral=True)

    if delay < 0.5:
        return await safe_send(interaction, "❌ Delay phải >= 0.5 giây", ephemeral=True)

    await interaction.response.send_message("⏳ Đang lấy danh sách...", ephemeral=True)

    try:
        cookies = json.loads(cookie)
        api = ZaloAPI(imei, cookies)
    except Exception as e:
        return await interaction.followup.send(f"❌ Lỗi khi khởi tạo API: {e}", ephemeral=True)

    if kieu == 1:
        danh_sach = api.fetch_groups()
        chon = "nhóm"
    elif kieu == 2:
        danh_sach = api.fetch_friends()
        chon = "người"
    else:
        return await interaction.followup.send("❌ Kiểu phải là 1 hoặc 2", ephemeral=True)

    if not danh_sach:
        return await interaction.followup.send(f"⚠️ Không tìm thấy {chon} nào.", ephemeral=True)

    msg = f"**Danh sách {chon}:**\n"
    for i, item in enumerate(danh_sach):
        msg += f"{i+1}. {item['name']} | ID: `{item['id']}`\n"
    msg += f"\nNhập STT các {chon} muốn spam (cách nhau bởi dấu phẩy):"

    chunks = [msg[i:i+1900] for i in range(0, len(msg), 1900)]
    await interaction.followup.send(chunks[0], ephemeral=True)
    for chunk in chunks[1:]:
        await interaction.followup.send(chunk, ephemeral=True)

    def check(m: discord.Message):
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

    try:
        reply = await bot.wait_for("message", check=check, timeout=60.0)
    except asyncio.TimeoutError:
        return await interaction.followup.send("❌ Hết thời gian chọn", ephemeral=True)

    try:
        pick = [int(x.strip())-1 for x in reply.content.strip().split(",")]
        ids = [danh_sach[i]['id'] for i in pick if 0 <= i < len(danh_sach)]
    except:
        return await interaction.followup.send("❌ STT không hợp lệ!", ephemeral=True)

    try:
        with open("nhay.txt", "r", encoding="utf-8") as f:
            messages = [line.strip() for line in f if line.strip()]
    except:
        return await interaction.followup.send("❌ Không tìm thấy file nhay.txt", ephemeral=True)

    if not messages:
        return await interaction.followup.send("❌ File nhay.txt trống", ephemeral=True)

    discord_user_id = str(interaction.user.id)
    start_time = datetime.now()

    tool = SpamTool(
        name="ZaloBot",
        imei=imei,
        cookies=cookies,
        thread_ids=ids,
        thread_type=ThreadType.GROUP if kieu == 1 else ThreadType.USER,
        use_typing=True  # ✅ fake soạn
    )

    th = threading.Thread(target=tool.send_spam, args=(messages, delay), daemon=True)
    th.start()

    with NHAY_LOCK:
        if discord_user_id not in user_nhay_tabs:
            user_nhay_tabs[discord_user_id] = []
        user_nhay_tabs[discord_user_id].append({
            "tool": tool,
            "thread": th,
            "ids": ids,
            "kieu": kieu,
            "start": start_time,
            "delay": delay
        })

    await interaction.followup.send(
        f"✅ Đã bắt đầu tab nhayzalo | Kế: {'Nhóm' if kieu==1 else '1-1'}\n"
        f"Delay: `{delay}`s | ID: {', '.join(ids)}",
        ephemeral=True
    )

@tree.command(name="tabnhayzalo", description="Quản lý/dừng tab nhây Zalo")
async def tabnhayzalo(interaction: discord.Interaction):
    if not is_authorized(interaction) and not is_admin(interaction):
        return await interaction.response.send_message("Bạn không có quyền sử dụng lệnh này", ephemeral=True)

    discord_user_id = str(interaction.user.id)
    with NHAY_LOCK:
        tabs = user_nhay_tabs.get(discord_user_id, [])

    if not tabs:
        return await interaction.response.send_message("Bạn không có tab nhây Zalo nào đang hoạt động", ephemeral=True)

    msg = "**Danh sách tab nhây Zalo của bạn:**\n"
    for idx, tab in enumerate(tabs, 1):
        uptime = get_uptime(tab["start"])
        ids_str = ", ".join(tab["ids"])
        msg += (
            f"{idx}. Kiểu: `{'Nhóm' if tab['kieu']==1 else '1-1'}` | "
            f"Delay: `{tab['delay']}`s | ID: `{ids_str}` | "
            f"Uptime: `{uptime}`\n"
        )
    msg += "\nNhập số tab để dừng tab đó:"

    await interaction.response.send_message(msg, ephemeral=True)

    def check(m: discord.Message):
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

    try:
        reply = await bot.wait_for("message", check=check, timeout=30.0)
    except asyncio.TimeoutError:
        return await interaction.followup.send("⏱ Hết thời gian chọn", ephemeral=True)

    content = reply.content.strip()
    if not content.isdigit():
        return await interaction.followup.send("❌ Không dừng tab nào", ephemeral=True)
    idx = int(content)
    if not (1 <= idx <= len(tabs)):
        return await interaction.followup.send("❌ Số không hợp lệ", ephemeral=True)

    with NHAY_LOCK:
        chosen = tabs.pop(idx - 1)
        # Cách nhẹ nhàng hơn: thêm flag trong SpamTool để dừng
        try:
            chosen["tool"].running = False
        except:
            pass
        if not tabs:
            del user_nhay_tabs[discord_user_id]

    await interaction.followup.send(f"✅ Đã dừng tab nhây Zalo số {idx}", ephemeral=True)        
    
   
@tree.command(
    name="tabanhtop",
    description="Quản lý/dừng tab treo ảnh top"
)
async def tabanhtop(interaction: discord.Interaction):
    if not is_authorized(interaction) and not is_admin(interaction):
        return await interaction.response.send_message("Bạn không có quyền sử dụng lệnh này", ephemeral=True)

    discord_user_id = str(interaction.user.id)
    with IMAGE_TAB_LOCK:
        tabs = user_image_tabs.get(discord_user_id, [])

    if not tabs:
        return await interaction.response.send_message("Bạn không có tab ảnh top nào đang hoạt động")

    msg = "**Danh sách tab ảnh top của bạn:**\n"
    for idx, tab in enumerate(tabs, start=1):
        uptime = get_uptime(tab["start"])
        msg += (
             f"{idx}. Post: `{tab['post_id']}` | Delay: `{tab['delay_min']}–{tab['delay_max']}` giây | "
             f"Uptime: `{uptime}` | Số ảnh: `{len(tab['images'])}`\n"
        )
    msg += "\nNhập số tab để dừng tab đó".format(len(tabs))

    await interaction.response.send_message(msg)

    def check(m: discord.Message):
        return (
            m.author.id == interaction.user.id and 
            m.channel.id == interaction.channel.id
        )

    try:
        reply: discord.Message = await bot.wait_for("message", check=check, timeout=30.0)
        content = reply.content.strip()
        if content.isdigit():
            idx = int(content)
            if 1 <= idx <= len(tabs):
                with IMAGE_TAB_LOCK:
                    chosen = tabs[idx-1]
                    chosen["stop_event"].set()
                    tabs.pop(idx-1)
                    if not tabs:
                        del user_image_tabs[discord_user_id]
                return await interaction.followup.send(f"Đã dừng tab ảnh top số {idx}")
        await interaction.followup.send("Không dừng tab nào.")
    except asyncio.TimeoutError:
        return await interaction.followup.send("Hết thời gian (30s). Không dừng tab nào")

def parse_cookie_string(cookie_str):
    cookies = {}
    for part in cookie_str.split(";"):
        if "=" in part:
            k, v = part.strip().split("=", 1)
            cookies[k.strip()] = v.strip()
    return cookies
                            
@tree.command(
    name="treozalo",
    description="Treo ngôn Zalo (spam nhóm hoặc bạn bè)"
)
@app_commands.describe(
    imei="IMEI thiết bị Zalo",
    cookies="Cookie (JSON hoặc chuỗi key=value;...)",
    message="Nội dung cần spam",
    delay="Delay giữa mỗi tin (giây)"
)
async def treozalo(
    interaction: discord.Interaction,
    imei: str,
    cookies: str,
    message: str,
    delay: float
):
    if not is_authorized(interaction) and not is_admin(interaction):
        return await interaction.response.send_message("❌ Bạn không có quyền sử dụng lệnh này", ephemeral=True)

    try:
        if cookies.strip().startswith("{"):
            cookies_dict = json.loads(cookies)
        else:
            cookies_dict = parse_cookie_string(cookies)
    except Exception as e:
        return await interaction.response.send_message(f"❌ Cookie không hợp lệ: {e}", ephemeral=True)

    if delay < 0.5:
        return await interaction.response.send_message("❌ Delay phải >= 0.5 giây.", ephemeral=True)

    # Gửi sớm để tránh timeout
    await interaction.response.send_message("📌 Chọn kiểu spam:\n`1` - Nhóm\n`2` - Bạn bè", ephemeral=True)

    def check(m: discord.Message):
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

    try:
        reply_type: discord.Message = await bot.wait_for("message", check=check, timeout=30.0)
    except asyncio.TimeoutError:
        return await interaction.channel.send("⏱ Hết thời gian chọn kiểu spam.")

    spam_type = reply_type.content.strip()
    if spam_type not in ["1", "2"]:
        return await interaction.channel.send("❌ Chỉ chọn `1` hoặc `2`.")

    try:
        api = ZaloAPI(imei, cookies_dict)
        if spam_type == "1":
            danh_sach = api.fetch_groups()
            label = "nhóm"
            thread_type = ThreadType.GROUP
        else:
            danh_sach = api.fetch_friends()
            label = "bạn bè"
            thread_type = ThreadType.USER
    except Exception as e:
        return await interaction.followup.send(f"❌ Không lấy được danh sách Zalo: {e}", ephemeral=True)

    if not danh_sach:
        return await interaction.followup.send(f"⚠️ Không có {label} nào.", ephemeral=True)

    # ✅ Hiển thị toàn bộ danh sách không giới hạn
    msg = f"**Danh sách {label}:**\n"
    for i, item in enumerate(danh_sach):
        msg += f"{i+1}. **{item['name']}** | ID: `{item['id']}`\n"
    msg += "\nNhập STT các mục muốn spam (phân cách dấu phẩy):"

    chunks = [msg[i:i+1900] for i in range(0, len(msg), 1900)]
    await interaction.followup.send(chunks[0], ephemeral=True)
    for chunk in chunks[1:]:
        await interaction.followup.send(chunk, ephemeral=True)

    try:
        reply = await bot.wait_for("message", check=check, timeout=60.0)
    except asyncio.TimeoutError:
        return await interaction.followup.send("⏱ Hết thời gian chọn", ephemeral=True)

    try:
        picks = [int(x.strip()) - 1 for x in reply.content.strip().split(",")]
        ids = [danh_sach[i]['id'] for i in picks if 0 <= i < len(danh_sach)]
    except:
        return await interaction.followup.send("❌ STT không hợp lệ", ephemeral=True)

    if not ids:
        return await interaction.followup.send("❌ Không có mục nào được chọn", ephemeral=True)

    tool = SpamTool(
        name=f"ZALO#{interaction.user.id}",
        imei=imei,
        cookies=cookies_dict,
        thread_ids=ids,
        thread_type=thread_type,
        use_typing=False
    )

    stop_event = threading.Event()
    start_time = datetime.now()

    th = threading.Thread(target=lambda: tool.send_spam([message], delay), daemon=True)
    th.start()

    discord_user_id = str(interaction.user.id)
    with ZALO_LOCK:
        if discord_user_id not in user_zalo_tabs:
            user_zalo_tabs[discord_user_id] = []
        user_zalo_tabs[discord_user_id].append({
            "tool": tool,
            "thread": th,
            "stop_event": stop_event,
            "targets": ids,
            "type": label,
            "message": message,
            "delay": delay,
            "start": start_time
        })

    await interaction.followup.send(
        f"✅ Đã tạo tab spam Zalo cho <@{discord_user_id}>:\n"
        f"• Mục tiêu: `{', '.join(ids)}`\n"
        f"• Kiểu: `{label}`\n"
        f"• Nội dung: `{message}`\n"
        f"• Delay: `{delay}` giây\n"
        f"• Bắt đầu: `{start_time.strftime('%Y-%m-%d %H:%M:%S')}`",
        ephemeral=True
    )
    
@tree.command(
    name="tabtreozalo",
    description="Quản lý/dừng tab treo Zalo"
)
async def tabtreozalo(interaction: discord.Interaction):
    if not is_authorized(interaction) and not is_admin(interaction):
        return await interaction.response.send_message(
            "Bạn không có quyền sử dụng lệnh này", ephemeral=True
        )

    discord_user_id = str(interaction.user.id)
    with ZALO_LOCK:
        tabs = user_zalo_tabs.get(discord_user_id, [])

    if not tabs:
        return await interaction.response.send_message(
            "❌ Bạn không có tab treo Zalo nào đang hoạt động.", ephemeral=True
        )

    msg = "**📋 Danh sách tab treo Zalo của bạn:**\n"
    for idx, tab in enumerate(tabs, start=1):
        uptime = (datetime.now() - tab["start"]).total_seconds()
        hours, rem = divmod(int(uptime), 3600)
        minutes, seconds = divmod(rem, 60)
        msg += (
            f"{idx}. Kiểu: `{tab.get('type', '?')}` | "
            f"Mục tiêu: `{', '.join(map(str, tab.get('targets', [])))}` | "
            f"Delay: `{tab.get('delay', '?')}` giây | "
            f"Uptime: `{hours:02}:{minutes:02}:{seconds:02}`\n"
        )
    msg += "\n⏳ Nhập **số tab** để dừng tab tương ứng."

    await interaction.response.send_message(msg, ephemeral=True)

    def check(m: discord.Message):
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

    try:
        reply = await bot.wait_for("message", check=check, timeout=30.0)
    except asyncio.TimeoutError:
        return await interaction.followup.send("⏱ Hết thời gian chọn. Không dừng tab nào.", ephemeral=True)

    try:
        index = int(reply.content.strip())
        if not (1 <= index <= len(tabs)):
            raise ValueError()
    except:
        return await interaction.followup.send("❌ Số tab không hợp lệ.", ephemeral=True)

    with ZALO_LOCK:
        chosen = tabs.pop(index - 1)
        chosen["tool"].running = False  # Dừng thread spam
        if not tabs:
            del user_zalo_tabs[discord_user_id]

    await interaction.followup.send(f"✅ Đã dừng tab treo Zalo số `{index}`", ephemeral=True)
    

async def notify_user_token_die(user_id: str, token: str, status_code: int):
    user = await bot.fetch_user(int(user_id))
    if user:
        try:
            await user.send(
                f"\u26a0\ufe0f Token `{token[:20]}...` \u0111\u00e3 b\u1ecb **DIE** v\u1edbi m\u00e3 l\u1ed7i `{status_code}` v\u00e0 \u0111\u00e3 \u0111\u01b0\u1ee3c x\u00f3a kh\u1ecfi tab c\u1ee7a b\u1ea1n."
            )
        except Exception as e:
            print(f"[!] Kh\u00f4ng th\u1ec3 g\u1eedi tin nh\u1eafn DM t\u1edbi user {user_id}: {e}")

async def remove_dead_token(user_id: str, token: str):
    async with DIS_LOCK:
        if user_id in user_discord_tabs:
            for tab in user_discord_tabs[user_id]:
                if token in tab["tokens"]:
                    index = tab["tokens"].index(token)
                    tab["tokens"].pop(index)
                    tab["delays"].pop(index)
                    print(f"[\u2713] \u0110\u00e3 x\u00f3a token DIE: {token[:15]}...")

async def _discord_spam_worker(session, token, channels, message, delay, start_time, user_id):
    headers = {
        "Authorization": token.strip(),
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJjbGllbnRfdmVyc2lvbiI6IjEwMC4wLjAuMCJ9"
    }
    while True:
        for channel_id in channels:
            content = message[:2000] if len(message) > 2000 else message
            data = {"content": content}
            url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
            try:
                async with session.post(url, headers=headers, json=data) as resp:
                    status = resp.status
                    if status in [200, 201]:
                        print(f"[\u2713] {token[:15]}... | G\u1eedi ID {channel_id}")
                    elif status in [401, 403]:
                        print(f"[\u00d7] Token DIE {token[:15]}... | Status: {status}")
                        await notify_user_token_die(user_id, token, status)
                        await remove_dead_token(user_id, token)
                        return
                    else:
                        err = await resp.text()
                        print(f"[\u00d7] Token {token[:15]}... | L\u1ed7i {channel_id} | {status} | {err}")
            except Exception as e:
                print(f"[!] Ngo\u1ea1i l\u1ec7 token {token[:15]}...: {e}")
            await asyncio.sleep(delay)

@tree.command(name="nhaymess", description="Spam nhây Facebook bằng cookie")
@app_commands.describe(
    cookies="Cookie (cách nhau dấu phẩy)",
    box_ids="ID Box (cách nhau dấu phẩy)",
    ten_reo="Tên cần réo (tuỳ chọn)",
    delay="Delay mỗi tin (giây)"
)
async def nhaymess(interaction: discord.Interaction, cookies: str, box_ids: str, ten_reo: str = "", delay: float = 2.0):
    await interaction.response.defer(ephemeral=True)
    discord_user_id = str(interaction.user.id)

    cookie_list = [x.strip() for x in cookies.split(",") if x.strip()]
    id_list = [x.strip() for x in box_ids.split(",") if x.strip()]
    messengers = []

    for c in cookie_list:
        try:
            messengers.append(Kem(c))
        except Exception as e:
            print(f"[!] Cookie lỗi: {e}")

    if not messengers:
        return await interaction.followup.send("❌ Tất cả cookie đều lỗi!", ephemeral=True)

    chon_name = ten_reo or ""
    CAU_CHUI = [
f"ccho sua lofi de {chon_name}",
f"sua di {chon_name} em😏🤞",
f"lofi di {chon_name} cu😝",
f"tk ngu lon {chon_name} eyy🤣🤣",
f"nhanh ti em {chon_name}🤪👌",
f"cam a {chon_name} mo coi😏🤞",
f"hang hai len ti {chon_name} de👉🤣",
f"cn tat nguyen {chon_name}😏??",
f"cn 2 lai mat mam {chon_name}🤪👎",
f"anh cho may sua a {chon_name}😏🤞",
f"ah ba meta 2025 ma {chon_name}😋👎",
f"bi anh da na tho cmnr dk {chon_name}🤣",
f"thieu oxi a {chon_name}🤣🤣",
f"anh cko may oxi hoa ne {chon_name}😏👉🤣",
f"may cay cha qua a cn ngu {chon_name}🤪",
f"may phe nhu con me may bi tao hiep ma {chon_name}🤣",
f"dung ngam dang nuot cay tao nha coan {chon_name}👉🤣",
f"con cho {chon_name} cay tao ro👉🌶",
f"oc cho ngoi do nhay voi tao a {chon_name}🤣",
f"me may bi tao cho len dinh r {chon_name}=))",
f"ui cn ngu {chon_name} oc cac=))",
f"cn gai me may khog bt day nay a {chon_name} cn oc cac😝",
f"cn cho {chon_name} may cam a:))?",
f"cam lang that r a cn ngu {chon_name}🤣",
f"ui tk cac dam cha chem chu ak {chon_name}😝🤞",
f"cn cho dot so tao run cam cap me roi ha em {chon_name} =))",
f"ui cai con hoi {chon_name}👉🤣",
f"cn me may chet duoi ao roi kia {chon_name}😆",
f"djt con {chon_name} cu cn lon tham:))",
f"ui con bem {chon_name} nha la nhin phen v:))",
f"con cho cay gan nha sua di {chon_name}😏",
f"con bem {chon_name} co me khog😏🤞",
f"a quen may mo coi tu nho ma {chon_name}🤣",
f"sua chill de {chon_name} oc🤣",
f"hay cam nhan noi dau di em {chon_name}:))))",
f"hinh anh con bem {chon_name} gie rach bi anh cha dap:))))))",
f"ti anh chup dang tbg la may hot nha {chon_name}🤣",
f"a may muon hot cx dau co de cn ngu {chon_name}👉🤣🤣",
f"oi may bi cha suc pham kia {chon_name}-))",
f"tao co noti con boai {chon_name} so tao:)) ti tao cap dang profile 1m theo doi:))",
f" {chon_name} con o moi khong bame bi tao khinh thuong=)))",
f"may con gi khac hon khong con bem du ngu {chon_name}🤣",
f"cam canh cdy ngu bi cha chui khong giam phan khang a {chon_name}:))",
f"bi tao chui ma toi so a {chon_name}🤞",
f"nhin ga {chon_name} muon ia chay🤣",
f"con culi lua thay phan ban bi phan boi a {chon_name}:))",
f"may bi tao chui cho om han dk {chon_name}👉🤣🤣🤞",
f"bi tao chui cho so queo cac dung khong {chon_name}:))))",
f"dung cam han tao nua {chon_name}:))",
f"con dog {chon_name} bi tao chui ghi thu a:))",
f"su dung ngon sat thuong xiu de bem anh di mo {chon_name}=)))",
f"co sat thuong chi mang ko ay {chon_name}😝",
f"con ngheo nha la {chon_name} bi bo si va👉🤣🤣",
f"nao may co biet thu nhu anh vay {chon_name}🤪👌",
f"thang nghich tu {chon_name} sao may giet cha may the:))",
f"khong ngo thang phan nghich {chon_name} lua cha doi me=))",
f"tk ngu {chon_name} bi anh co lap ma-))",
f"phan khang di con cali {chon_name} mat map:))",
f"may con gi khac ngoai sua khong ay {chon_name}👉😏🤞",
f" {chon_name} mo coi=))",
f"bi cha chui phat nao ghi han phat do {chon_name} dk em:))",
f"may toi day de chi bi tao chui thoi ha {chon_name}:))",
f"bo la ac quy fefe ne {chon_name}🤣🤣",
f"nen bo lay cay ak ban nat so may luon😏🤞",
f"keo lu ban an hai may ra lmj dc anh khong vay {chon_name}🤣🤞",
f"ui ui dung thang an hai mang ten {chon_name}:))",
f"dung la con can ba mxh chi biet nhin anh chui cha mang me no ma {chon_name}=))",
f"may co phan khang duoc khong vay:)) {chon_name}",
f"may khong phan khang duoc a {chon_name}=))",
f"may yeu kem den vay a con cali {chon_name}😋👎",
f"con cali {chon_name} mat mam cay ah roi🌶",
f"cu anh lam dk em {chon_name}:))",
f"may co biet gi ngoai sua kiki dau ma {chon_name}👉🤣🤣",
f"may la chi qua qua ban may la chi gau gau ha {chon_name}=))",
f"mua skill di em {chon_name}🤪🤞",
f"anh mua skill duoc ma em {chon_name}😏🤞",
f"anh mua skill vo cai lon me may ay em {chon_name}:))",
f"con culi {chon_name} said : sap win duoc anh roi mung vai a🤣",
f"con cali {chon_name} nghi vay nen mung lam dk:)) {chon_name}",
f"win duoc anh dau de dau em {chon_name}🤪🤞",
f"con cho dien {chon_name} sua dien cuong nao🤣",
f"ui ui con kiki {chon_name} cay anh da man a🌶",
f"tk mo coi {chon_name} sua belike a🤣",
f"chill ti di em {chon_name}🤣🤣",
f"sao sua ko chill gi het vay {chon_name}🤣🤣",
f"bi anh chui cho tat ngon a {chon_name}=))",
f"may sua mau khong anh dap may tat sua bh {chon_name}:))",
f"sua toi khi kiet que nha cn thu {chon_name}🤣🤣",
f"cam may ngung nha cn kiki {chon_name}😝",
f"bo mat nghen ngon a ma nhai hoai v {chon_name}:🤪👌",
f"tao cam 1887 ban ca gia pha nha may chet {chon_name} ay:))",
f"may thay anh ba qua nen sui cmnr a {chon_name}😜",
f"sao may cam vay {chon_name}🤪🤞",
f"may cam = tao win do {chon_name}🤣🤣",
f"may nham win duoc tao khong {chon_name}🤣",
f"ga ma hay sua vay {chon_name}👉🤣",
f"tao dem 123 may chua len tao giet con gia may do {chon_name}🤣",
f"ra tinh hieu de tao treo co con ba may die di {chon_name}:))",
f"may ra tinh hieu sos chay thoat than trc a {chon_name}🤣",
f"dung thang con bat hieu {chon_name}👉🤣🤣",
f"con me may moi de ra thang con bat hieu nhu vay🤣🤞",
f"thang con troi danh di bao gia pha a {chon_name}🤪🤞",
f"bao nhu may gap anh cung tat dien {chon_name}🤣🤞🤞",
f" {chon_name} bi anh chui off mxh la vua roi=))",
f"may lam lai anh khong vayy {chon_name}:))",
f"tao biet la khongg ma {chon_name}👉🤣",
f"do may bai tao all san ro cmnr ma {chon_name}🤣",
f"tao dep trai ma {chon_name}👉🤣",
f"nen may le luoi liem chan tao di {chon_name}🤪🤞",
f"o o ccho {chon_name} loe toe bo may dap vo mom🤣",
f"tk cac {chon_name} oc cho vai cuc👉🤣",
f"tk ngu {chon_name} thay hw la lam than a🤪🤞",
f"du ngu cung onl mxh a {chon_name}😏😏",
f"svat {chon_name} cay cu anh den tim tai het roi a🤣",
f"moi ti xiu ma go duoi roi a {chon_name}🤣",
f"anh speed ne tk ngu {chon_name}👉😏",
f"cn cho ngu {chon_name} moi 5p ma da met a🤣🤣",
f"tk bach tang {chon_name}",
f"ccho dot la {chon_name}",
f"ngu cn ra de a {chon_name}",
f"tk ngon lu {chon_name}",
f"sped di tk ga {chon_name}",
f"ga v em {chon_name}",
f"anh uoc ga giong may a {chon_name}",
f"o o cn nghich tu {chon_name}",
f"chay dau vay tk {chon_name} ngu",
f"anh cho may chay a {chon_name}",
f"chay nhanh vay em {chon_name}",
f"ma sao em thoat khoi anh duoc ha {chon_name} em",
f"co gang win anh di {chon_name}",
f"sap win dc roi do {chon_name}",
f"e e care t di ma {chon_name}",
f"sao ko giam {chon_name}",
f"roi roi cam lang a {chon_name}",
f"on khong vay {chon_name}",
f"bat on a {chon_name}",
f"bi tao chui ma sao on dc {chon_name}",
f"cn cali {chon_name} sua bay",
f"ai cho m sua v {chon_name}",
f"xin phep ah chua o {chon_name}",
f"da may chetme may ma cn culi {chon_name} du xe",
f"sao may bel vay em {chon_name}",
f"120kg a {chon_name}",
f"sao may khon v {chon_name}",
f"khon nhu con kiki nha tao🤣 {chon_name}",
f"sat thuog ti di em {chon_name}",
f"em kem coi v {chon_name}",
f"co gi khac khong {chon_name}",
f"khong co j a {chon_name}",
f"em phe vay la cung dk {chon_name}",
f"dung a🤣 {chon_name}",
f"roi roi {chon_name}",
f"cn phe {chon_name}",
f"leg keg di troi {chon_name}",
f"lien tuc {chon_name} di boa",
f"sao ko lien tuc {chon_name}",
f"yeu sinh ly a🤣 {chon_name}",
f"nang khong em {chon_name}",
f"so anh nen dai ra mau luon a {chon_name}",
f"cn culi {chon_name} mat mam",
f"gap gap len tk ngu {chon_name}",
f"anh speed vcl ma {chon_name}",
f"may slow vaicalonn {chon_name}",
f"an c j phe lam vay tk phe vat {chon_name}",
f"cay cu anh lam ma {chon_name}",
f"cay ma choi a {chon_name}",
f"nhin mat ns nhu trai ot kia {chon_name}",
f"choi la doi a {chon_name}",
f"sao hay v cn dog ten {chon_name}",
f"t cam ba chia dam dit bme may ma {chon_name}",
f"o o thg cn bat hieu nay chs gay vs cau {chon_name} a",
f"{chon_name} teu v em",
f"tau hai a {chon_name}",
f"cn an hai danh trong lang a {chon_name}",
f"duoi a {chon_name}",
f"nhin biet duoi r🤣 {chon_name}",
f"anh cho may rot a {chon_name}",
f"sao cam lang r {chon_name}",
f"roi roi cn ngu cam {chon_name}",
f"ccho {chon_name} nay phen ia v",
f"anh go ba vcl ay {chon_name}",
f"cay a {chon_name}",
f"Ngầu Êyy {chon_name}",
f"Cố lên con thú {chon_name}",
f"Tao cho mày ngậm chx ? {chon_name}",
f"Mày cút rồi hả {chon_name} ",
f"cố tí nữa {chon_name}",
f"speed nào {chon_name}",
f"nhây tới năm sau dc ko {chon_name}",
f"mạnh mẽ nào {chon_name}",
f"Con culi mocoi ey {chon_name}",
f"k đc à {chon_name}",
f"con chó ngu cố đê {chon_name}",
f"sao m câm kìa {chon_name}",
f"gà j {chon_name}",
f"mày sợ tao à =)) {chon_name}",
f"m gà mà {chon_name}",
f"mày ngu rõ mà {chon_name}",
f"đúng mà {chon_name}",
f"cãi à {chon_name}",
f"mày còn gì khác k {chon_name}",
f"học lỏm kìa {chon_name}",
f"cố tí em {chon_name}",
f"mếu à {chon_name}",
f"sao mếu kìa {chon_name}",
f"tao đã cho m mếu đâu {chon_name}",
f"va lẹ đi con dốt {chon_name}",
f"sao kìa {chon_name}",
f"từ bỏ r à {chon_name}",
f"mạnh mẽ tí đi con đĩ {chon_name}",
f"cố lên con chó ngu {chon_name}",
f"=)) cay tao à con đĩ {chon_name}",
f"sợ tao à {chon_name}",
f"sao sợ tao kìa {chon_name}"
f"cay lắm phải kh {chon_name}",
f"ớt rồi kìa em {chon_name}",
f"mày còn chối à {chon_name}",
f"làm tí đê {chon_name}",
f"mới đó đã mệt r kìa {chon_name}",
f"sao gà mà sồn v {chon_name}",
f"sồn như lúc đầu cho tao {chon_name}",
f"sao à {chon_name}",
f"ai cho m nhai {chon_name}",
f"cay lắm r {chon_name}", 
f"từ bỏ đi em {chon_name}",
f"mày nghĩ mày làm t cay đc à {chon_name}",
f"có đâu {chon_name}",
f"tao đang hành m mà {chon_name}",
f"bịa à {chon_name}",
f"cay :))))) {chon_name}",
f"cố lên chó dốt {chon_name}",
f"hăng tiếp đi {chon_name}",
f"tới sáng k em {chon_name}",
f"k tới sáng à {chon_name}",
f"chán v {chon_name}",
f"m gà mà {chon_name}",
f"log acc thay phiên à {chon_name}",
f"coi tụi nó dồn ngu kìa {chon_name}",
f"sợ tao à con chó đần {chon_name}",
f"lại win à {chon_name}",
f"lại win r {chon_name}",
f"lũ cặc cay tao lắm🤣🤣 {chon_name}",
f"cố lên đê {chon_name}",
f"sao mới 5p đã câm r {chon_name}",
f"yếu đến thế à {chon_name}",
f"sao kìa {chon_name}",
f"khóc kìa {chon_name}",
f"cầu cứu lẹ ei {chon_name}",
f"ai cứu đc m à :)) {chon_name}",
f"tao bá mà {chon_name}",
f"sao m gà thế {chon_name}",
f"hăng lẹ cho tao {chon_name}",
f"con chó eiii🤣 {chon_name}",
f"ổn k em {chon_name}",
f"kh ổn r à {chon_name}",
f"mày óc à con chó bẻm=)) {chon_name}",
f"mẹ mày ngu à {chon_name}",
f"bú cặc cha m k em {chon_name}",
f"thg giả gái :)) {chon_name}",
f"coi nó ngu kìa ae {chon_name}",
f"con chó này giả ngu à {chon_name}",
f"m ổn k {chon_name}",
f"mồ côi kìa {chon_name}",
f"sao v sợ r à {chon_name}",
f"cố gắng tí em {chon_name}",
f"cay cú lắm r {chon_name}",
f"đấy đấy bắt đầu {chon_name}",
f"chảy nước đái bò r à em {chon_name}",
f"sao kìa đừng run {chon_name}",
f"mày run à:)) {chon_name}",
f"thg dái lở {chon_name}",
f"cay mẹ m lắm {chon_name}",
f"lgbt xuất trận à con đĩ {chon_name}",
f"thg cặc giết cha mắng mẹ {chon_name}",
f"sủa mạnh eii {chon_name}",
f"mày chết r à:)) {chon_name}",
f"sao chết kìa {chon_name}",
f"bị t hành nên muốn chết à {chon_name}",
f"con lồn ngu=)) {chon_name}",
f"sao kìa {chon_name}",
f"mạnh lên kìa {chon_name}",
f"yếu sinh lý à {chon_name}",
f"sủa đê {chon_name}",
f"cay à {chon_name}",
f"hăng đê {chon_name}",
f"gà kìa ae {chon_name}",
f"akakaa {chon_name}",
f"óc chó kìa {chon_name}",
f"🤣🤣🤣 {chon_name}",
f"ổn không🤣🤣 {chon_name}",
f"bất ổn à {chon_name}",
f"ơ kìaaa {chon_name}",
f"hăng hái đê {chon_name}",
f"chạy à 🤣🤣 {chon_name}",
f"tởn à {chon_name}",
f"kkkk {chon_name}",
f"mày dốt à {chon_name}",
f"cặc ngu {chon_name}",
f"cháy đê {chon_name}",
f"chat hăng lên {chon_name}",
f"cố lên {chon_name}",
f"mồ côi cay {chon_name}",
f"cay à {chon_name}",
f"cn chó ngu {chon_name}",
f"óc cac kìa {chon_name}",
f"đĩ đú:)) {chon_name}",
f"đú kìa {chon_name}",
f"cùn v {chon_name}",
f"r x {chon_name}",
f"hhhhh {chon_name}",
f"kkakak {chon_name}",
f"sao đú đó em {chon_name}",
f"cac teo a con {chon_name}",
f"ngu kìa {chon_name}",
f"chat mạnh đê {chon_name}",
f"hăng ee {chon_name}",
f"ơ ơ ơ {chon_name}",
f"sủa cháy đê {chon_name}",
f"sủa mạnh eei {chon_name}",
f"mày óc à con {chon_name}",
f"tao cho m chạy à {chon_name}",
f"con đĩ ngu sủa? {chon_name}",
f"mày chạy à con đĩ lồn {chon_name}",
f"co len con {chon_name}",
f"son hang len em {chon_name}",
f"sao m yeu v {chon_name} ",
f"co ti nua {chon_name}",
f"sao kia cham a {chon_name}",
f"hang hai len ti chu {chon_name}",
f"toi sang di {chon_name}",
f"co gang ti con cho {chon_name}",
f"yeu v con {chon_name}",
f"con cho {chon_name} co de",
f"sao m cam kia {chon_name}",
f"ga v {chon_name}",
f"may so a k dam chat hang ak {chon_name}",
f"m ga ma {chon_name}",
f"may ngu ro ma {chon_name}",
f"con {chon_name} an hai ma",
f"cai cun ak {chon_name}",
f"may con gi khac ko vay {chon_name}",
f"hoc dot nen nhay dot ak {chon_name}",
f"co ti di em {chon_name}",
f"meu a {chon_name}",
f"sao meu kia {chon_name}",
f"tao da cho m meu dau {chon_name}",
f"va le di con {chon_name} dot",
f"sao kia {chon_name}",
f"tu bo r a {chon_name}",
f"manh me ti di con {chon_name}",
f"co len con cho {chon_name} ngu",
f"😆 cay tao a con di {chon_name}",
f"so tao a {chon_name}",
f"sao cham roi kia {chon_name}",
f"cay lam phai kh {chon_name}",
f"{chon_name} ot anh cmnr",
f"may con choi a {chon_name}",
f"lam ti keo de {chon_name}",
f"moi do da met r ha {chon_name}",
f"sao ga ma son v {chon_name}",
f"son nhu luc dau cho tao di con {chon_name} dot",
f"sao duoi roi kia {chon_name}",
f"ai cho m nhai vay {chon_name}",
f"cay lam r a {chon_name}",
f"tu bo di em {chon_name}",
f"may nghi may lam t cay dc ha {chon_name}",
f"m dang cay ma {chon_name}",
f"tao dang hanh m ma {chon_name}",
f"keo nhay kg ay {chon_name}",
f"con mo coi {chon_name}",
f"co len {chon_name} oc cho",
f"hang tiep di {chon_name}",
f"toi sang k em {chon_name}",
f"met roi ha {chon_name}",
f"speed ti dc ko {chon_name}",
f"m ga ma {chon_name}",
f"thay phien a {chon_name}",
f"tui anh thay phien ban vo loz me con {chon_name} ma kaka",
f"so tao a con cho {chon_name}",
f"anh win me roi {chon_name} dot",
f"ga ma hay the hien ha {chon_name}",
f"con mo coi {chon_name} keo cai ko em",
f"co len de {chon_name}",
f"sao moi 1 ti ma da cam roi {chon_name}",
f"yeu vay ak {chon_name}",
f"sao kia {chon_name}",
f"bat luc r ak {chon_name}",
f"tim cach roi ha {chon_name}",
f"ai cuu dc m a :)) {chon_name}",
f"anh ba cmnr ma {chon_name}",
f"sao m ga vay {chon_name}",
f"hang le cho tao di {chon_name}",
f"con mo coi {chon_name}",
f"on k em {chon_name}",
f"bat on roi a {chon_name}",
f"may oc a con cho {chon_name}",
f"me may ngu a {chon_name}",
f"bu cac cha m k em {chon_name}",
f"mo coi {chon_name} cay anh ha",
f"me m dot tu roi a {chon_name}",
f"phe vay {chon_name}",
f"m on k {chon_name}",
f"mo coi kia {chon_name}",
f"sao v so r a {chon_name}",
f"co gang ti em {chon_name}",
f"cay cu lam r ha {chon_name}",
f"dien dai di em {chon_name}",
f"chay nuoc dai bo r a em {chon_name}",
f"sao kia dung so anh ma {chon_name}",
f"may run a:)) {chon_name}",
f"thg {chon_name} mo coi",
f"cay tao lam ha {chon_name}",
f"lgbt len phim ngu ak em {chon_name}",
f"thg cac giet cha mang me {chon_name}",
f"sua manh eii {chon_name}",
f"may chet r a:)) {chon_name}",
f"sao chet kia {chon_name}",
f"bi t hanh nen muon chet a {chon_name}",
f"con {chon_name} loz ngu kaka",
f"sao kia {chon_name}",
f"manh len kia {chon_name}",
f"yeu sinh ly a {chon_name}",
f"sua de {chon_name}",
f"cay a {chon_name}",
f"hang de {chon_name}",
f"con ga {chon_name}",
f"phe vat {chon_name}",
f"oc cho {chon_name}",
f"me m bi t du hap hoi kia con {chon_name}",
f"on ko em {chon_name}",
f"bat on ak {chon_name}",
f"o kiaaa sao vayy {chon_name}",
f"hang hai de {chon_name}",
f"chay ak {chon_name}",
f"so ak {chon_name}",
f"quiu luon roi ak {chon_name}",
f"may dot ak {chon_name}",
f"cac ngu {chon_name}",
f"chay de {chon_name}",
f"chat hang len {chon_name}",
f"co len {chon_name}",
f"{chon_name} mo coi",
f"cn cho ngu {chon_name}",
f"oc cac {chon_name}",
f"di du {chon_name}",
f"du kia {chon_name}",
f"cun v {chon_name}",
f"r luon con {chon_name} bi ngu roi",
f"met r am {chon_name}",
f"kkakak",
f"sao du {chon_name}",
f"cac con {chon_name}",
f"ngu kia {chon_name}",
f"chat manh de {chon_name}",
f"hang ee {chon_name}",
f"clm thk oc cho {chon_name}",
f"sua chay de {chon_name}",
f"sua manh eei {chon_name}",
f"may oc a con {chon_name}",
f"tao cho m chay a {chon_name}",
f"con mo coi {chon_name}",
f"may chay a con di lon {chon_name}",
f"sua de {chon_name}",
f"con phen {chon_name}",
f"bat on ho {chon_name}",
f"s do  {chon_name}",
f"sua lien tuc de {chon_name}",
f"moi tay ak {chon_name}",
f"choi t giet cha ma m ne {chon_name}",
f"hang xiu de {chon_name}",
f"th ngu {chon_name}",
f"len daica bieu ne {chon_name}",
f"sua chill de {chon_name}",
f"m thich du ko da {chon_name}",
f"son hang dc kg {chon_name}",
f"cam chay nhen {chon_name}",
f"m mau de {chon_name}",
f"duoi ak {chon_name}",
f"th ngu {chon_name}",
f"con {chon_name} len day anh sut chet me may",
f"m khoc ak {chon_name}",
f"sua lien tuc de {chon_name}",
f"thg {chon_name} cho dien",
f"bi ngu ak {chon_name}",
f"speed de {chon_name}",
f"cham v cn culi {chon_name}",
f"hoang loan ak {chon_name}",
f"bat on ak {chon_name}",
f"run ak {chon_name}",
f"chay ak {chon_name}",
f"duoi ak {chon_name}",
f"met r ak {chon_name}",
f"sua mau {chon_name}",
f"manh dan len {chon_name}",
f"nhanh t cho co hoi cuu ma m ne {chon_name}",
f"cam mach me nha {chon_name}",
f"ao war ak {chon_name}",
f"tk {chon_name} dot v ak",
f"cham chap ak {chon_name}",
f"th cho bua m sao v {chon_name}",
f"th dau buoi mat cho {chon_name}",
f"cam hoang loan ma {chon_name}",
f"lo lo sao may cam v {chon_name}",
f"ai cho may cam vayy {chon_name}",
f"anh cho chx ay=)) {chon_name}",
f"cmm hai a {chon_name}",
f"hai vay em {chon_name}",
f"co gi khac khong {chon_name}",
f"khong a {chon_name}",
f"ga den vay a {chon_name}",
f"thang an hai lien tuc di {chon_name}",
f"bi anh dap dau ma {chon_name}",
f"cay cu anh lam dk {chon_name}",
f"âkkak sua di em {chon_name}",
f"ccho ngu sua {chon_name}",
f"xem ns occho kia {chon_name}",
f"ngu hay sua a👉😏 {chon_name}",
f"alo alo cdy ngu {chon_name}👉🤪",
f"leg keg loc troc lay sa beg dap dau may {chon_name}👉🤣",
f"sua hang hai ti di em ey {chon_name}👉🤪",
f"may vua sua bi tao lay sa beg dap vo 2 hon trug dai ma {chon_name}👉😋",
f"o o cn culi {chon_name} bia ngu a👉🤣🤣",
f"cay anh ma lmj dc anh dau {chon_name} dk🤞🤞",
f"culi {chon_name} cn oc bem a con😋",
f"sao do coan zai {chon_name} cn sua dc khong ay👉😏",
f"khong a {chon_name}🤣🤣",
f"anh biet anh ba ma {chon_name}",
f"ccho ngu hay sua a {chon_name}🤪🤪",
f"mat may nhu trai ot roi kia {chon_name}🤣🤣",
f"ngu ngu bi anh dap dau vo cot dien chetme may nha {chon_name}🤣🤣",
f"anh thog minh vcll ma {chon_name}🤪🤪",
f"may ngu nguc vcll ma em {chon_name}🤣🤣",
f"dk {chon_name} em😏🤞",
f"dung a {chon_name}🤣🤣",
f"may lam tao cuoi dc roi ds {chon_name}🤪🤞",
f"dien siet duoc roi do {chon_name} ngu ey🤣🤣",
f"anh chuc may dien ko ai coi nha {chon_name}👉🤣",
f"bi anh hanh ha den die dk {chon_name}😏🤞",
f"anh dap chetme may ma {chon_name} em🤣🤣",
f"sua lam vay {chon_name} kiki🤣🤣",
f"cn me nay hap hoi a {chon_name}👉😏🤞",
f"may bua nhan a {chon_name}🤣🤣",
f"run ray khi gap a ma {chon_name}🤪🤞",
f"anh len san la may khiep so dk {chon_name}🤣🤣",
f"do ah ba qua nen may so dk {chon_name}👉😏",
f"may van xin anh tha thu ma {chon_name}😝🙏",
f"tao cam ak47 na vo dau mat chetme may {chon_name}😝🙏",
f"may sua dien cuong di {chon_name}🤣🤣",
f"cmm ngu the em {chon_name}🤣🤞",
f"ai ngu = may nua dau {chon_name} em 👉🤣🤞",
f"may nhu culi giang tran vay {chon_name}🤣🤣",
f"may ma culi j may lgbt ma {chon_name} em🤣",
f"anh ba dao san war ma {chon_name} cu😝👎",
f"may an cut san treo ma {chon_name} 👉🤣🤞",
f"bu cut tao song qua ngay ma {chon_name}🤣🤣",
f"xao lon cn gay a {chon_name}😝",
f"culi biet sua la day a {chon_name}😏🤞",
f"ga ma gay quai vay {chon_name}🤪👌",
f"may can ngon roi a {chon_name}😏🤞",
f"con gi khac hon khong {chon_name}🤪🤪",
f"khog a {chon_name}🤣",
f"ngu den vay la cung ha {chon_name}😏🤞",
f"sao may phe nhan vay😏🤞",
f"con nghich tu phan loan {chon_name}🤣🤣",
f"con cho chiu so phan di {chon_name}😏🤞",
f"chiu so phan bi anh dam cha giet ma {chon_name} ha🤣🤣",
f"anh cs hoi dau may tu tra loi a {chon_name}🤣",
f"tk bua nhan {chon_name}😏🤞",
f"sao culi khong sua nx di {chon_name}🤣🤣",
f"nin ngon roi a {chon_name}🤣🤪",
f"gap phai cha la may phai ngam ot roi {chon_name}🤣🤣",
f"ngon xam cac lay len doi bem ah a tk culi {chon_name}🤪🤞",
f"cn cali mat mam sua j ay {chon_name}😏🤞",
f"len nhay vs ah toi trang tron di {chon_name}😝",
f"sao ay tai mat roi a {chon_name}🤣🤣",
f"so lam roi a {chon_name}😏🤞",
f"co may anh da dau may toi chet me {chon_name}🤣",
f"dcm cay cu anh a {chon_name}🤣🤣",
]

    class NhayReoWorker:
        def __init__(self, messengers, box_ids, messages, delay, stop_event):
            self.messengers = messengers
            self.box_ids = box_ids
            self.messages = messages
            self.delay = delay
            self.stop_event = stop_event

        def run(self):
            idx = 0
            while not self.stop_event.is_set():
                for messenger in self.messengers:
                    for box_id in self.box_ids:
                        msg = self.messages[idx % len(self.messages)]
                        result = messenger.gui_tn(box_id, msg)
                        if result.get("success"):
                            print(f"[NHAY][{messenger.user_id}] → {box_id}: OK")
                        else:
                            print(f"[NHAY][{messenger.user_id}] → {box_id}: FAIL")
                        time.sleep(0.2)
                idx += 1
                time.sleep(self.delay)

    stop_event = threading.Event()
    start_time = datetime.now()

    worker = NhayReoWorker(messengers, id_list, CAU_CHUI, delay, stop_event)
    thread = threading.Thread(target=worker.run, daemon=True)
    thread.start()

    if discord_user_id not in user_nhaymess_tabs:
        user_nhaymess_tabs[discord_user_id] = []
    user_nhaymess_tabs[discord_user_id].append({
        "messengers": messengers,
        "box_ids": id_list,
        "delay": delay,
        "start_time": start_time,
        "stop_event": stop_event,
        "thread": thread
    })

    embed = discord.Embed(title="✅ Đã tạo tab nhây mess", color=0x00ff00)
    embed.add_field(name="👤 Người dùng", value=f"<@{discord_user_id}>", inline=False)
    embed.add_field(name="📨 To", value=", ".join(id_list), inline=False)
    embed.add_field(name="📡 Tài khoản", value=str(len(messengers)), inline=True)
    embed.add_field(name="⏱ Delay", value=f"{delay} giây", inline=True)
    embed.add_field(name="🕰 Bắt đầu", value=start_time.strftime("%Y-%m-%d %H:%M:%S"), inline=False)

    await interaction.followup.send(embed=embed)            
                                    


@tree.command(name="tabnhaymess", description="Xem tab đang chạy và dừng từng tab")
async def tabnhaymess(interaction: discord.Interaction):
    discord_user_id = str(interaction.user.id)
    tabs = user_nhaymess_tabs.get(discord_user_id, [])
    if not tabs:
        return await interaction.response.send_message("⚠️ Không có tab nào đang chạy.", ephemeral=True)

    desc = ""
    for idx, tab in enumerate(tabs):
        elapsed = (datetime.now() - tab["start_time"]).total_seconds()
        h, rem = divmod(int(elapsed), 3600)
        m, s = divmod(rem, 60)
        uptime = f"{h:02}:{m:02}:{s:02}"
        desc += (
            f"**{idx + 1}.** Box: `{', '.join(tab['box_ids'])}` | "
            f"Delay: `{tab['delay']}s` | Uptime: `{uptime}`\n"
        )

    embed = discord.Embed(title="📋 Danh sách tab nhây đang chạy", description=desc, color=0x3498db)
    embed.set_footer(text="Trả lời tin nhắn này bằng STT để dừng tab.")
    await interaction.response.send_message(embed=embed, ephemeral=True)

    def check(msg):
        return (
            msg.author.id == interaction.user.id and 
            msg.channel.id == interaction.channel.id and 
            msg.content.isdigit()
        )

    try:
        msg = await bot.wait_for("message", check=check, timeout=60)
        stt = int(msg.content.strip()) - 1
        if 0 <= stt < len(tabs):
            tabs[stt]["stop_event"].set()
            del tabs[stt]
            if not tabs:
                del user_nhaymess_tabs[discord_user_id]
            await msg.reply("🛑 Đã dừng tab thành công.")
        else:
            await msg.reply("❌ STT không hợp lệ.")
    except:
        await interaction.followup.send("⏰ Hết thời gian chọn STT.", ephemeral=True)

@bot.event
async def on_ready():
    await tree.sync()
    print("✅ Bot đã online và đã sync slash command")            

@tree.command(name="treodis", description="Treo ng\u00f4n discord")
@app_commands.describe(
    tokens="Token",
    channels="ID Channel",
    message="N\u1ed9i dung",
    delays="Delay"
)
async def treodis(
    interaction: discord.Interaction,
    tokens: str,
    channels: str,
    message: str,
    delays: str
):
    if not is_authorized(interaction) and not is_admin(interaction):
        return await interaction.response.send_message("B\u1ea1n kh\u00f4ng c\u00f3 quy\u1ec1n s\u1eed d\u1ee5ng bot", ephemeral=True)

    tokens_list = [t.strip() for t in tokens.split(",") if t.strip()]
    channels_list = [c.strip() for c in channels.split(",") if c.strip()]
    try:
        delays_list = [float(d.strip()) for d in delays.split(",") if d.strip()]
    except:
        return await interaction.response.send_message("Delay ph\u1ea3i l\u00e0 s\u1ed1", ephemeral=True)

    if not tokens_list or not channels_list or not delays_list:
        return await interaction.response.send_message("Thi\u1ebfu tokens/channels/delays h\u1ee3p l\u1ec7", ephemeral=True)
    if len(delays_list) not in (1, len(tokens_list)):
        return await interaction.response.send_message("Delay count ph\u1ea3i =1 ho\u1eb7c = s\u1ed1 token", ephemeral=True)
    if any(d < 0.5 for d in delays_list):
        return await interaction.response.send_message("Delay ph\u1ea3i tr\u00ean 0.5s.", ephemeral=True)

    if len(delays_list) == 1:
        delays_list *= len(tokens_list)

    session = aiohttp.ClientSession()
    start_time = datetime.now()
    discord_user_id = str(interaction.user.id)
    tasks = []

    for token, delay in zip(tokens_list, delays_list):
        task = asyncio.create_task(
            _discord_spam_worker(session, token, channels_list, message, delay, start_time, discord_user_id)
        )
        tasks.append(task)

    async with DIS_LOCK:
        if discord_user_id not in user_discord_tabs:
            user_discord_tabs[discord_user_id] = []
        user_discord_tabs[discord_user_id].append({
            "session": session,
            "tasks": tasks,
            "channels": channels_list,
            "tokens": tokens_list,
            "delays": delays_list,
            "message": message,
            "start": start_time
        })

    return await interaction.response.send_message(
        f"\u0110\u00e3 t\u1ea1o tab treo discord cho <@{discord_user_id}>:\n"
        f"\u2022 Channels: `{', '.join(channels_list)}`\n"
        f"\u2022 Tokens: `{len(tokens_list)}`\n"
        f"\u2022 Delay(s): `{', '.join(str(d) for d in delays_list)}` gi\u00e2y\n"
        f"\u2022 B\u1eaft \u0111\u1ea7u: `{start_time.strftime('%Y-%m-%d %H:%M:%S')}`",
        ephemeral=True
    )
    
def format_time(seconds):
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    return f"{h:02}:{m:02}:{s:02}"    
  
@tree.command(
    name="tabtreodis",
    description="Quản lý/dừng tab treo iscord"
)
async def tabtreodis(interaction: discord.Interaction):
    if not is_authorized(interaction) and not is_admin(interaction):
        return await interaction.response.send_message("Bạn không có quyền sử dụng bot", ephemeral=True)

    discord_user_id = str(interaction.user.id)
    async with DIS_LOCK:
        tabs = user_discord_tabs.get(discord_user_id, [])

    if not tabs:
        return await interaction.response.send_message("Bạn không có tab treo discord nào đang hoạt động", ephemeral=True)

    msg = "**Danh sách tab treo discord của bạn:**\n"
    for idx, tab in enumerate(tabs, 1):
        elapsed = int((datetime.now() - tab["start"]).total_seconds())
        uptime = format_time(elapsed)
        msg += (
            f"{idx}. Channels:`{','.join(tab['channels'])}` | "
            f"Tokens:`{len(tab['tokens'])}` | Delays:`{','.join(str(d) for d in tab['delays'])}`s | "
            f"Uptime:`{uptime}`\n"
        )
    msg += f"\nNhập số tab để dừng tab"

    await interaction.response.send_message(msg, ephemeral=True)

    def check(m: discord.Message):
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

    try:
        reply = await bot.wait_for("message", check=check, timeout=30.0)
    except asyncio.TimeoutError:
        return await interaction.followup.send("Hết thời gian. Không dừng tab nào", ephemeral=True)

    c = reply.content.strip()
    if not c.isdigit():
        return await interaction.followup.send("Không dừng tab nào", ephemeral=True)
    i = int(c)
    if not (1 <= i <= len(tabs)):
        return await interaction.followup.send("Số không hợp lệ", ephemeral=True)

    async with DIS_LOCK:
        tab = tabs.pop(i-1)
        for t in tab["tasks"]:
            t.cancel()
        await tab["session"].close()
        if not tabs:
            del user_discord_tabs[discord_user_id]

    return await interaction.followup.send(f"Đã dừng tab số {i}", ephemeral=True)
    

import sys
import os
import asyncio
import aiohttp
from datetime import datetime
import itertools
from discord.ui import Modal, TextInput, View, Button

NHAYDIS_FILE = os.environ.get('NHAYDIS_FILE', 'nhaydis.txt')
_NHAYDIS_SESSION = None
_SESSION_LOCK = asyncio.Lock()

NHAYDIS_LOCK = asyncio.Lock()
THREADS_LOCK = asyncio.Lock()
POLL_LOCK = asyncio.Lock()
user_nhaydis_tabs = {}
user_thread_sessions = {}
user_poll_sessions = {}

def load_nhaydis_file(path=NHAYDIS_FILE):
    import io
    import contextlib
    data = {}
    if not os.path.exists(path):
        return data

    try:
        txt = open(path, 'r', encoding='utf-8').read()
    except UnicodeDecodeError:
        txt = open(path, 'r', encoding='latin1').read()

    ns = {}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(txt, {}, ns)
    for k, v in ns.items():
        if isinstance(v, list):
            data[k.lower()] = v
    return data


async def get_session():
    global _NHAYDIS_SESSION
    async with _SESSION_LOCK:
        if _NHAYDIS_SESSION is None or _NHAYDIS_SESSION.closed:
            connector = aiohttp.TCPConnector(limit_per_host=10)
            _NHAYDIS_SESSION = aiohttp.ClientSession(connector=connector)
        return _NHAYDIS_SESSION

def encode_emoji_for_reaction(emoji_char: str) -> str:
    from urllib.parse import quote
    return quote(emoji_char, safe='')

def get_uptime(start):
    if not start:
        return '??'
    delta = datetime.now() - start
    seconds = int(delta.total_seconds())
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    return f"{h}h {m}m {s}s"

_sections = load_nhaydis_file()

MESSAGES_NAM = _sections.get('messages_nam', [])
MESSAGES_NU = _sections.get('messages_nu', [])
nhaydis2c = _sections.get('nhaydis2c', [])
sodiscord = _sections.get('sodiscord', [])
codelag = _sections.get('codelag', [])
nhaycopy = _sections.get('nhaycopy', [])
nhayemoji = _sections.get('nhayemoji', [])
nhaychina = _sections.get('nhaychina', [])
EMOJI_LIST = list(_sections.get('emoji_list', [])) or ["🐷","😏","👏","💥","😃","😭","🙏","🤡","💩","😈"]

async def discord_spam_worker(token, channel_id, delay, mention_ids, color, semaphore, messages):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    typing_url = f"https://discord.com/api/v10/channels/{channel_id}/typing"
    send_url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    mention_text = " ".join([f"<@{uid}>" for uid in mention_ids]) if mention_ids else ""
    session = await get_session()
    while True:
        for msg in messages:
            try:
                await semaphore.acquire()
                await session.post(typing_url, headers=headers)
                await asyncio.sleep(random.uniform(delay, delay + 0.4))
                full_msg = f"{msg} {mention_text}" if mention_text else msg
                async with session.post(send_url, json={"content": full_msg}, headers=headers) as resp:
                    if resp.status == 200:
                        print(f"✅ GỬI • {color}→ {channel_id}")
                    else:
                        error_text = await resp.text()
                        print(f"❌ LỖI {resp.status} • {color} • {error_text[:200]}")
            except asyncio.CancelledError:
                raise
            except Exception as e:
                print(f"{color}⚠️ TOKEN LỖI • {e}")
                await asyncio.sleep(2)
            finally:
                semaphore.release()

async def discord_spam_worker_all(token, channel_id, delay, mention_ids, color, semaphore, messages):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    typing_url = f"https://discord.com/api/v10/channels/{channel_id}/typing"
    send_url = f"https://discord.com/api/v10/channels/{channel_id}/messages"
    mention_text = " ".join([f"<@{uid}>" for uid in mention_ids]) if mention_ids else ""
    session = await get_session()
    while True:
        for msg in messages:
            try:
                await semaphore.acquire()
                await session.post(typing_url, headers=headers)
                await asyncio.sleep(random.uniform(delay, delay + 0.4))
                full_msg = f"{msg} {mention_text}" if mention_text else msg
                async with session.post(send_url, json={"content": full_msg}, headers=headers) as resp:
                    if resp.status == 200:
                        try:
                            msg_json = await resp.json()
                            print(f"✅ [ĐÃ GỬI] {color}→ {channel_id}")
                            if messages is nhayemoji:
                                message_id = msg_json.get('id')
                                if message_id:
                                    for emoji in random.sample(EMOJI_LIST, min(5, len(EMOJI_LIST))):
                                        emoji_encoded = encode_emoji_for_reaction(emoji)
                                        react_url = f"https://discord.com/api/v10/channels/{channel_id}/messages/{message_id}/reactions/{emoji_encoded}/@me"
                                        await session.put(react_url, headers=headers)
                                        await asyncio.sleep(0.25)
                        except Exception:
                            pass
                    else:
                        error_text = await resp.text()
                        print(f"❌ [LỖI {resp.status}] {error_text[:200]}")
            except asyncio.CancelledError:
                raise
            except Exception as e:
                print(f"{color}⚠️ [TOKEN LỖI] {e}")
                await asyncio.sleep(2)
            finally:
                semaphore.release()

class SpamChoiceView(discord.ui.View):
    def __init__(self, owner_id):
        super().__init__(timeout=60)
        self.owner_id = owner_id

    @discord.ui.button(label="♂️Nam", style=discord.ButtonStyle.primary)
    async def nam_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message(f"❌ Bạn không có quyền sử dụng lệnh này, xin vui lòng liên hệ <@{admin_id}>.", ephemeral=True)
        await interaction.response.send_modal(NhayDisModalCustom(messages=MESSAGES_NAM, title="Tool war Discord (Nam)"))

    @discord.ui.button(label="♀️Nữ", style=discord.ButtonStyle.danger)
    async def nu_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.owner_id:
            return await interaction.response.send_message(f"❌ Bạn không có quyền sử dụng lệnh này, xin vui lòng liên hệ admin <@{admin_id}>.", ephemeral=True)
        await interaction.response.send_modal(NhayDisModalCustom(messages=MESSAGES_NU, title="Tool war Discord (Nữ)"))

class NhayDisModalCustom(discord.ui.Modal):
    def __init__(self, messages, title="Tool war Discord"):
        super().__init__(title=title)
        self.messages = messages
        self.token = discord.ui.TextInput(label="⚡ Token (Nhập token Discord của bạn)", style=discord.TextStyle.paragraph)
        self.channel_id = discord.ui.TextInput(label="📡 Channel IDs (nhập ID kênh cần spam)")
        self.delay = discord.ui.TextInput(label="⏱️ Delay (giây)")
        self.mention_ids = discord.ui.TextInput(label="👥 ID người cần tag (Không bắt buộc)", required=False)
        self.add_item(self.token)
        self.add_item(self.channel_id)
        self.add_item(self.delay)
        self.add_item(self.mention_ids)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(embed=discord.Embed(title="⏳ Đang xử lý...", description="Hệ thống đang tiến hành **tạo tab**. Vui lòng chờ...", color=discord.Color.yellow()), ephemeral=True)
        try:
            tokens = [t.strip() for t in self.token.value.strip().split(",") if t.strip()]
            channel_ids = [c.strip() for c in self.channel_id.value.strip().split(",") if c.strip()]
            delay = float(self.delay.value.strip())
            mention_list = ([i.strip() for i in self.mention_ids.value.split(",")] if self.mention_ids.value else [])
            discord_user_id = str(interaction.user.id)
            start_time = datetime.now()
            semaphore = asyncio.Semaphore(1)
            tasks = []
            for token in tokens:
                for channel_id in channel_ids:
                    task = asyncio.create_task(discord_spam_worker(token=token, channel_id=channel_id, delay=delay, mention_ids=mention_list, color=f"[{discord_user_id}] ", semaphore=semaphore, messages=self.messages))
                    tasks.append(task)
            async with NHAYDIS_LOCK:
                if discord_user_id not in user_nhaydis_tabs:
                    user_nhaydis_tabs[discord_user_id] = []
                user_nhaydis_tabs[discord_user_id].append({"session_count": len(tokens), "channels": channel_ids, "delay": delay, "start": start_time, "tasks": tasks, "messages": self.messages})
            embed = discord.Embed(title="✅ Tạo Tab Thành Công!", color=discord.Color.green())
            embed.set_author(name=str(interaction.user), icon_url=interaction.user.display_avatar.url)
            embed.add_field(name="📦 Tổng số tab", value=f"`{len(tokens) * len(channel_ids)}`", inline=False)
            embed.add_field(name="📡 Kênh", value=f"`{', '.join(channel_ids)}`", inline=False)
            embed.add_field(name="👥 Mention", value=f"`{', '.join(mention_list) if mention_list else 'Không'}`", inline=False)
            embed.add_field(name="⏱️ Delay", value=f"`{delay}` giây", inline=True)
            embed.add_field(name="🕒 Bắt đầu lúc", value=f"`{start_time.strftime('%Y-%m-%d %H:%M:%S')}`", inline=True)
            embed.set_footer(text="Hệ thống khởi tạo tab hoàn tất!")
            await interaction.followup.send(embed=embed)
        except Exception as e:
            error_embed = discord.Embed(title="❌ Lỗi", description=f"```{e}```", color=discord.Color.red())
            await interaction.followup.send(embed=error_embed)

class SpamVuiceView(discord.ui.View):
    def __init__(self, owner_id):
        super().__init__(timeout=60)
        self.owner_id = owner_id

    async def check_owner(self, interaction):
        if interaction.user.id != self.owner_id:
            await interaction.response.send_message(f"❌ Bạn không có quyền sử dụng lệnh này, xin vui lòng liên hệ <@{admin_id}>.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Sớ discord", style=discord.ButtonStyle.secondary)
    async def so_button(self, interaction, button):
        if not await self.check_owner(interaction):
            return
        await interaction.response.send_modal(AllDisModalCustom(messages=sodiscord, title="Sớ Discord"))

    @discord.ui.button(label="2c discord", style=discord.ButtonStyle.secondary)
    async def dis2c_button(self, interaction, button):
        if not await self.check_owner(interaction):
            return
        await interaction.response.send_modal(AllDisModalCustom(messages=nhaydis2c, title="2c Discord"))

    @discord.ui.button(label="Code lag", style=discord.ButtonStyle.secondary)
    async def lag_button(self, interaction, button):
        if not await self.check_owner(interaction):
            return
        await interaction.response.send_modal(AllDisModalCustom(messages=codelag, title="Code lag"))

    @discord.ui.button(label="Nhây copy", style=discord.ButtonStyle.secondary)
    async def copy_button(self, interaction, button):
        if not await self.check_owner(interaction):
            return
        await interaction.response.send_modal(AllDisModalCustom(messages=nhaycopy, title="Nhây copy"))

    @discord.ui.button(label="Nhây emoji", style=discord.ButtonStyle.secondary)
    async def emoji_button(self, interaction, button):
        if not await self.check_owner(interaction):
            return
        await interaction.response.send_modal(AllDisModalCustom(messages=nhayemoji, title="Nhây emoji"))

    @discord.ui.button(label="Nhây china", style=discord.ButtonStyle.secondary)
    async def china_button(self, interaction, button):
        if not await self.check_owner(interaction):
            return
        await interaction.response.send_modal(AllDisModalCustom(messages=nhaychina, title="Nhây china"))

    @discord.ui.button(label="Nhây idea", style=discord.ButtonStyle.secondary)
    async def idea_button(self, interaction, button):
        if not await self.check_owner(interaction):
            return
        embed = discord.Embed(title="📌 Chọn đối tượng", description="- Vui lòng chọn đối tượng cần spam 🗣️", color=discord.Color.blue())
        view = SpamChoiceView(owner_id=interaction.user.id)
        await interaction.response.send_message(embed=embed, view=view)

    @discord.ui.button(label="Thread Discord", style=discord.ButtonStyle.primary)
    async def open_thread(self, interaction: discord.Interaction, button: Button):
        if not is_authorized(interaction) and not is_admin(interaction):
            await interaction.response.send_message(embed=discord.Embed(title="❌ Quyền hạn", description="Bạn không có quyền sử dụng bot.", color=discord.Color.red()), ephemeral=True)
            return
        view = ThreadButtonView()
        embed = discord.Embed(title="🧵 Spam Thread Discord", description="Chọn chế độ spam bạn muốn sử dụng:", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed, view=view)

class AllDisModalCustom(discord.ui.Modal):
    def __init__(self, messages, title="All Discord"):
        super().__init__(title=title)
        self.messages = messages
        self.token = discord.ui.TextInput(label="⚡Token (Nhập token discord của bạn)", style=discord.TextStyle.paragraph)
        self.channel_id = discord.ui.TextInput(label="⚡Channel IDs (nhập id kênh cần spam)")
        self.delay = discord.ui.TextInput(label="⚡Delay (giây)")
        self.mention_ids = discord.ui.TextInput(label="⚡ID Người cần tag (Không bắt buộc)", required=False)
        self.add_item(self.token)
        self.add_item(self.channel_id)
        self.add_item(self.delay)
        self.add_item(self.mention_ids)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message("🚀 Đang tiến hành tạo tab...")
        try:
            tokens = [t.strip() for t in self.token.value.strip().split(",") if t.strip()]
            channel_ids = [c.strip() for c in self.channel_id.value.strip().split(",") if c.strip()]
            delay = float(self.delay.value.strip())
            mention_list = ([i.strip() for i in self.mention_ids.value.split(",")] if self.mention_ids.value else [])
            discord_user_id = str(interaction.user.id)
            start_time = datetime.now()
            semaphore = asyncio.Semaphore(1)
            tasks = []
            for token in tokens:
                for channel_id in channel_ids:
                    task = asyncio.create_task(discord_spam_worker_all(token=token, channel_id=channel_id, delay=delay, mention_ids=mention_list, color=f"[{discord_user_id}] ", semaphore=semaphore, messages=self.messages))
                    tasks.append(task)
            async with NHAYDIS_LOCK:
                if discord_user_id not in user_nhaydis_tabs:
                    user_nhaydis_tabs[discord_user_id] = []
                user_nhaydis_tabs[discord_user_id].append({"session_count": len(tokens), "channels": channel_ids, "delay": delay, "start": start_time, "tasks": tasks, "messages": self.messages})
            embed = discord.Embed(title="✅ Đã tạo tab spam discord thành công", description=f"Thông tin chi tiết về tab spam của <@{discord_user_id}>", color=discord.Color.green(), timestamp=start_time)
            embed.add_field(name="• Số tab", value=f"{len(tokens) * len(channel_ids)}", inline=True)
            embed.add_field(name="• Kênh", value=", ".join(channel_ids), inline=True)
            embed.add_field(name="• Mention", value=", ".join(mention_list) if mention_list else "Không", inline=True)
            embed.add_field(name="• Delay", value=f"{delay} giây", inline=True)
            embed.set_footer(text="Bắt đầu lúc")
            embed.timestamp = start_time
            await interaction.followup.send(embed=embed)
        except Exception as e:
            embed_error = discord.Embed(title="❌ Lỗi khi tạo tab spam", description=f"`{e}`", color=discord.Color.red())
            await interaction.followup.send(embed=embed_error)

@tree.command(name="allnhaydis", description="Tạo all tab nhây Discord")
async def allnhaydis(interaction: discord.Interaction):
    if not is_admin(interaction) and not is_authorized(interaction):
        return await interaction.response.send_message("❌ Bạn không có quyền sử dụng bot")
    embed = discord.Embed(title="Chọn phương thức", description=("- Vui lòng chọn 1 phương thức trong số phương thức nhây discord sau đây.\n- dùng lệnh /taballnhaydis để dừng bot spam⛔\n"), color = discord.Color.from_rgb(72, 209, 204))
    view = SpamVuiceView(owner_id=interaction.user.id)
    await interaction.response.send_message(embed=embed, view=view, allowed_mentions=discord.AllowedMentions(users=True))

@tree.command(name="taballnhaydis", description="Quản lý/dừng tất cả các phương thức nhây Discord (kèm Thread & Poll)")
async def taballnhaydis(interaction: discord.Interaction):
    if not is_admin(interaction) and not is_authorized(interaction):
        embed = discord.Embed(
            title="🚫 Không có quyền",
            description=f"Bạn không có quyền sử dụng bot, vui lòng liên hệ <@{admin_id}>.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    discord_user_id = str(interaction.user.id)

    async with NHAYDIS_LOCK:
        nhay_tabs = user_nhaydis_tabs.get(discord_user_id, [])
    async with THREADS_LOCK:
        thread_tabs = user_thread_sessions.get(discord_user_id, [])
    async with POLL_LOCK:
        poll_tabs = user_poll_sessions.get(discord_user_id, [])

    combined_tabs = []
    combined_tabs.extend([{"type": "discord", **tab} for tab in nhay_tabs])
    combined_tabs.extend([{"type": "thread", **tab} for tab in thread_tabs])
    combined_tabs.extend([{"type": "poll", **tab} for tab in poll_tabs])

    if not combined_tabs:
        embed = discord.Embed(
            title="❌ Không có tab hoạt động",
            description="Hiện tại bạn không có bất kỳ tab spam Discord, Thread hoặc Poll nào đang chạy.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    embed = discord.Embed(
        title="📋 Danh sách các tab đang hoạt động",
        description="Các tab **spam/nhây** hiện tại của bạn đang chạy:",
        color=discord.Color.blurple()
    )

    for idx, tab in enumerate(combined_tabs, 1):
        uptime = get_uptime(tab.get("start"))
        delay = tab.get("delay", "?")
        channels = ", ".join(tab.get("channels", [])) or "Không rõ"
        ttype = tab.get("type")

        if ttype == "thread":
            target = "🧵 Thread Discord"
        elif ttype == "poll":
            target = "📊 Poll Discord"
        else:
            method = str(tab.get("method", "")).lower()
            if "sớ" in method:
                target = "💫 Sớ Discord"
            elif "2c" in method:
                target = "💢 2C Discord"
            elif "code lag" in method or "lag" in method:
                target = "⚙️ Code Lag"
            elif "copy" in method:
                target = "📋 Nhây Copy"
            elif "emoji" in method:
                target = "😜 Nhây Emoji"
            elif "china" in method:
                target = "🐉 Nhây China"
            elif "idea" in method:
                target = "💡 Nhây Idea"
            else:
                target = "💬 Khác"

        embed.add_field(
            name=f"#{idx} | {target}",
            value=f"**Delay:** `{delay}s`\n**Kênh:** `{channels}`\n**Thời gian chạy:** `{uptime}`",
            inline=False
        )

    embed.set_footer(text="➡️ Nhập số thứ tự để dừng tab hoặc 'All' để dừng tất cả (trong 30 giây).")
    await interaction.response.send_message(embed=embed)

    def check(m: discord.Message):
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

    try:
        reply = await bot.wait_for("message", check=check, timeout=30.0)
    except asyncio.TimeoutError:
        embed = discord.Embed(
            title="⏱️ Hết thời gian",
            description="Bạn không nhập kịp, không có tab nào bị dừng.",
            color=discord.Color.orange()
        )
        return await interaction.followup.send(embed=embed)

    choice = reply.content.strip()

    if choice.lower() == "all":
        async with NHAYDIS_LOCK:
            for tab in nhay_tabs:
                for task in tab.get("tasks", []):
                    task.cancel()
            user_nhaydis_tabs.pop(discord_user_id, None)

        async with THREADS_LOCK:
            for tab in thread_tabs:
                for task in tab.get("tasks", []):
                    task.cancel()
            user_thread_sessions.pop(discord_user_id, None)

        async with POLL_LOCK:
            for tab in poll_tabs:
                for task in tab.get("tasks", []):
                    task.cancel()
            user_poll_sessions.pop(discord_user_id, None)

        embed = discord.Embed(
            title="⛔ Đã dừng tất cả tab",
            description="Tất cả các tab spam Discord, Thread và Poll đã được dừng.",
            color=discord.Color.red()
        )
        return await interaction.followup.send(embed=embed)

    if not choice.isdigit():
        embed = discord.Embed(
            title="⚠️ Không hợp lệ",
            description="Vui lòng nhập số thứ tự hoặc 'All'.",
            color=discord.Color.yellow()
        )
        return await interaction.followup.send(embed=embed)

    index = int(choice)
    if not (1 <= index <= len(combined_tabs)):
        embed = discord.Embed(
            title="⚠️ Số không hợp lệ",
            description=f"Vui lòng nhập số từ 1 đến {len(combined_tabs)}.",
            color=discord.Color.yellow()
        )
        return await interaction.followup.send(embed=embed)

    selected = combined_tabs[index - 1]
    tab_type = selected.get("type")
    start_time = selected.get("start")

    if tab_type == "thread":
        async with THREADS_LOCK:
            for tab in list(thread_tabs):
                if tab.get("start") == start_time:
                    for t in tab.get("tasks", []):
                        t.cancel()
                    thread_tabs.remove(tab)
                    break
            if not thread_tabs:
                user_thread_sessions.pop(discord_user_id, None)

    elif tab_type == "poll":
        async with POLL_LOCK:
            for tab in list(poll_tabs):
                if tab.get("start") == start_time:
                    for t in tab.get("tasks", []):
                        t.cancel()
                    poll_tabs.remove(tab)
                    break
            if not poll_tabs:
                user_poll_sessions.pop(discord_user_id, None)

    else:
        async with NHAYDIS_LOCK:
            for tab in list(nhay_tabs):
                if tab.get("start") == start_time:
                    for t in tab.get("tasks", []):
                        t.cancel()
                    nhay_tabs.remove(tab)
                    break
            if not nhay_tabs:
                user_nhaydis_tabs.pop(discord_user_id, None)

    embed = discord.Embed(
        title="🛑 Đã dừng tab thành công",
        description=f"Tab số `{index}` ({tab_type}) đã được dừng.",
        color=discord.Color.red()
    )
    await interaction.followup.send(embed=embed)


from thread import (thread_worker, read_chude_file, THREADS_LOCK as THREADS_LOCK_EXTERNAL, user_thread_sessions as USER_THREAD_SESSIONS_EXTERNAL, format_time)


THREADS_LOCK = THREADS_LOCK_EXTERNAL
user_thread_sessions = USER_THREAD_SESSIONS_EXTERNAL


VERBOSE = False

def log(*args, **kwargs):
    if VERBOSE:
        print(*args, **kwargs)

class ThreadButtonView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="No Message", style=discord.ButtonStyle.danger, custom_id="open_thread_no_msg")
    async def open_no_msg_modal(self, interaction: discord.Interaction, button: Button):
        if not is_authorized(interaction) and not is_admin(interaction):
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Lỗi Quyền hạn",
                    description="Bạn không có quyền sử dụng bot.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
            return

        modal = ThreadModal(mode="no_message")
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Message", style=discord.ButtonStyle.success, custom_id="open_thread_with_msg")
    async def open_with_msg_modal(self, interaction: discord.Interaction, button: Button):
        if not is_authorized(interaction) and not is_admin(interaction):
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Lỗi Quyền hạn",
                    description="Bạn không có quyền sử dụng bot.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
            return

        modal = ThreadModal(mode="message")
        await interaction.response.send_modal(modal)


class ThreadModal(Modal, title="Spam Thread Discord"):
    def __init__(self, mode):
        super().__init__()
        self.mode = mode

        self.token = TextInput(
            label="Token",
            style=discord.TextStyle.paragraph,
            placeholder="Nhập token phân tách bằng dấu ,"
        )

        self.guild_id = TextInput(
            label="Guild ID (ID server)",
            placeholder="Nhập ID server muốn spam thread"
        )

        self.delay = TextInput(
            label="Delay",
            required=False,
            placeholder="2.0 giây"
        )

        self.tag_users = TextInput(
            label="User IDs cần tag",
            style=discord.TextStyle.paragraph,
            required=False,
            placeholder="Cách nhau bằng dấu phẩy"
        )

        self.add_item(self.token)
        self.add_item(self.guild_id)
        self.add_item(self.delay)
        self.add_item(self.tag_users)

    async def on_submit(self, interaction: discord.Interaction):
        if not is_authorized(interaction) and not is_admin(interaction):
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Lỗi Quyền hạn",
                    description="Bạn không có quyền sử dụng bot.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
            return

        token_list = [t.strip() for t in self.token.value.split(",") if t.strip()]
        guild_id = self.guild_id.value.strip()

        try:
            delay = float(self.delay.value.strip()) if self.delay.value else 2.0
        except:
            delay = 2.0

        tag_user_ids = [uid.strip() for uid in self.tag_users.value.split(",") if uid.strip()]
        chude_pairs = read_chude_file("nhay2.txt")
        user_id = str(interaction.user.id)
        start_time = datetime.now()
        tasks = []

        base_api = "https://discord.com/api/v10"

        for token in token_list:
            headers = {"Authorization": token, "Content-Type": "application/json"}
            expanded_channels = []

            try:
                session = await get_session()
                async with session.get(f"{base_api}/guilds/{guild_id}/channels", headers=headers, timeout=10) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        text_chs = [str(c["id"]) for c in data if c.get("type") == 0]
                        if text_chs:
                            expanded_channels.extend(text_chs)
                            print(f"[{user_id}] ✅ Lấy {len(text_chs)} kênh text từ server {guild_id}")
                    else:
                        print(f"[{user_id}] ⚠️ Không thể lấy channel server {guild_id}, status {resp.status}")
            except Exception as e:
                print(f"[{user_id}] ⚠️ Exception khi lấy channel: {e}")

            if not expanded_channels:
                print(f"[{user_id}] ❌ Không có channel text hợp lệ từ server {guild_id}.")
                continue

            t = asyncio.create_task(
                thread_worker(
                    token=token,
                    channel_ids=expanded_channels,
                    delay=delay,
                    chude_pairs=chude_pairs,
                    color_prefix=f"[{user_id}] ",
                    semaphore=asyncio.Semaphore(1),
                    tag_user_ids=tag_user_ids,
                    mode=self.mode
                )
            )
            tasks.append(t)

        async with THREADS_LOCK:
            if user_id not in user_thread_sessions:
                user_thread_sessions[user_id] = []

            user_thread_sessions[user_id].append({
                "session_count": len(token_list),
                "guild_id": guild_id,
                "channels": expanded_channels,
                "delay": delay,
                "start": start_time,
                "tasks": tasks,
                "mode": self.mode
            })

        embed = discord.Embed(
            title="✅ Đã khởi chạy tạo chủ đề",
            description=(
                f"Chế độ: `{self.mode}`\n"
                f"Số worker: `{len(tasks)}`\n"
                f"Server ID: `{guild_id}`\n"
                f"Số kênh text: `{len(expanded_channels)}`\n"
                f"Delay: `{delay}s`\n"
                f"Tag user: `{', '.join(tag_user_ids) if tag_user_ids else 'Không có'}`\n"
                f"Bắt đầu lúc: `{start_time.strftime('%Y-%m-%d %H:%M:%S')}`"
            ),
            color=discord.Color.green()
        )

        await interaction.response.send_message(embed=embed)

        

def telegram_send_loop(token, chat_ids, caption, photo, delay, stop_event, discord_user_id):
    while not stop_event.is_set():
        for chat_id in chat_ids:
            if stop_event.is_set():
                break
            try:
                if photo:
                    if photo.startswith("http"):
                        url = f"https://api.telegram.org/bot{token}/sendPhoto"
                        data = {"chat_id": chat_id, "caption": caption, "photo": photo}
                        resp = requests.post(url, data=data, timeout=10)
                    else:
                        url = f"https://api.telegram.org/bot{token}/sendPhoto"
                        with open(photo, "rb") as f:
                            files = {"photo": f}
                            data = {"chat_id": chat_id, "caption": caption}
                            resp = requests.post(url, data=data, files=files, timeout=10)
                else:
                    url = f"https://api.telegram.org/bot{token}/sendMessage"
                    data = {"chat_id": chat_id, "text": caption}
                    resp = requests.post(url, data=data, timeout=10)

                if resp.status_code == 200:
                    print(f"[TELE][{discord_user_id}] Gửi thành công → {chat_id}")
                elif resp.status_code == 429:
                    retry = resp.json().get("parameters", {}).get("retry_after", 10)
                    print(f"[TELE][{discord_user_id}] Rate limit {retry}s")
                    time.sleep(retry)
                else:
                    print(f"[TELE][{discord_user_id}] Lỗi {resp.status_code}: {resp.text[:100]}")
            except Exception as e:
                print(f"[TELE][{discord_user_id}] Exception: {e}")
            time.sleep(0.2)
        time.sleep(delay)
        

@tree.command(
    name="treotele",
    description="Treo ngôn telegram"
)
@app_commands.describe(
    tokens="Token Telegram bot (ngăn cách dấu phẩy)",
    chats="ID nhóm chat (ngăn cách dấu phẩy)",
    text="Nội dung tin nhắn",
    delay="Delay giữa mỗi lần gửi (giây)",
    img="Link ảnh đính kèm (tuỳ chọn)"
)
async def treotele(
    interaction: discord.Interaction,
    tokens: str,
    chats: str,
    text: str,
    delay: int,
    img: str = None
):
    # ✅ Phân quyền
    if not is_authorized(interaction) and not is_admin(interaction):
        return await interaction.response.send_message("❌ Bạn không có quyền sử dụng bot", ephemeral=True)

    await interaction.response.defer(ephemeral=True)

    tokens_list = [t.strip() for t in tokens.split(",") if t.strip()]
    chats_list = [c.strip() for c in chats.split(",") if c.strip()]

    if delay < 1:
        return await interaction.followup.send("❌ Delay phải lớn hơn 1 giây")

    valid = []
    for tk in tokens_list:
        try:
            resp = requests.get(f"https://api.telegram.org/bot{tk}/getMe", timeout=5)
            if resp.ok:
                valid.append(tk)
            else:
                await interaction.followup.send(f"⚠️ Token không hợp lệ: `{tk}`")
        except requests.exceptions.ConnectTimeout:
            await interaction.followup.send(f"⚠️ Không thể kiểm tra token `{tk}`: kết nối Telegram bị timeout, vẫn cho phép chạy")
            valid.append(tk)  # ✅ vẫn cho chạy
        except Exception as e:
            await interaction.followup.send(f"⚠️ Lỗi kiểm tra token `{tk}`: `{e}`")

    if not valid:
        return await interaction.followup.send("❌ Không có token hợp lệ")

    discord_user_id = str(interaction.user.id)
    start_time = datetime.now()

    for tk in valid:
        stop_event = multiprocessing.Event()
        process = multiprocessing.Process(
            target=telegram_send_loop,
            args=(tk, chats_list, text, img, delay, stop_event, discord_user_id),
            daemon=True
        )
        process.start()

        with TREOTELE_LOCK:
            user_treotele_tabs.setdefault(discord_user_id, []).append({
                "process": process,
                "stop_event": stop_event,
                "start": start_time,
                "token": tk,
                "chats": chats_list,
                "text": text,
                "img": img,
                "delay": delay
            })

    await interaction.followup.send(
        f"✅ Đã tạo tab treo Telegram cho <@{discord_user_id}>:\n"
        f"• Chats: `{', '.join(chats_list)}`\n"
        f"• Tokens: `{len(valid)}`\n"
        f"• Delay: `{delay}` giây\n"
        f"• Ảnh: `{img or 'Không có'}`\n"
        f"• Bắt đầu: `{start_time.strftime('%Y-%m-%d %H:%M:%S')}`"
    )
                
@tree.command(
    name="tabtreotele",
    description="Quản lý/dừng tab treo telegram"
)
async def tabtreotele(interaction: discord.Interaction):
    if not is_authorized(interaction) and not is_admin(interaction):
        return await interaction.response.send_message("Bạn không có quyền sử dụng bot", ephemeral=True)

    discord_user_id = str(interaction.user.id)
    with TREOTELE_LOCK:
        tabs = user_treotele_tabs.get(discord_user_id, [])

    if not tabs:
        return await interaction.response.send_message("Bạn không có tab treo telegram nào đang hoạt động", ephemeral=True)

    msg = "**Danh sách tab treo telegram của bạn:**\n"
    for i, tab in enumerate(tabs, 1):
        elapsed = int((datetime.now() - tab["start"]).total_seconds())
        uptime = time.strftime("%H:%M:%S", time.gmtime(elapsed))
        msg += (
            f"{i}. Token:`{tab['token'][:10]}...` | Chats:`{','.join(tab['chats'])}` | "
            f"Delay:`{tab['delay']}`s | Up:`{uptime}`\n"
        )
    msg += f"\nNhập số tab để dừng tab"

    await interaction.response.send_message(msg, ephemeral=True)

    def check(m: discord.Message):
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

    try:
        reply = await bot.wait_for("message", check=check, timeout=30.0)
    except asyncio.TimeoutError:
        return await interaction.followup.send("Hết thời gian. Không dừng tab nào", ephemeral=True)

    choice = reply.content.strip()
    if not choice.isdigit():
        return await interaction.followup.send("Không dừng tab nào", ephemeral=True)
    idx = int(choice)
    if not (1 <= idx <= len(tabs)):
        return await interaction.followup.send("Số không hợp lệ", ephemeral=True)

    with TREOTELE_LOCK:
        tab = tabs.pop(idx-1)
        tab["stop_event"].set()
        if not tabs:
            user_treotele_tabs.pop(discord_user_id, None)

    return await interaction.followup.send(f"Đã dừng tab số {idx}", ephemeral=True)
    


def parse_cookie_str(cookie_str):
    return dict(item.strip().split('=') for item in cookie_str.split(';') if '=' in item)

def spam_loop(acc_id):
    info = SPAM_TASKS.get(acc_id)
    if not info:
        return

    cl = info["client"]
    targets = info["targets"]
    message = info["message"]
    delay = info["delay"]

    while True:
        for target in targets:
            if target in info["stop_targets"]:
                continue
            try:
                if target.isdigit():
                    cl.direct_send(message, thread_ids=[target])
                else:
                    user_id = cl.user_id_from_username(target)
                    cl.direct_send(message, [user_id])
                print(f"[+] Gửi thành công tới: {target}")
            except Exception as e:
                print(f"[!] Lỗi gửi {target}: {e}")
        time.sleep(delay)

@tree.command(name="treoig", description="Treo spam IG bằng sessionid")
@app_commands.describe(
    cookie="Cookie Instagram (chỉ cần chứa sessionid=...)",
    targets="Danh sách username hoặc thread ID, phân cách dấu phẩy",
    message="Nội dung muốn gửi",
    delay="Delay mỗi vòng (giây)"
)
async def treoig(
    interaction: discord.Interaction,
    cookie: str,
    targets: str,
    message: str,
    delay: float
):
    if str(interaction.user.id) not in ADMIN_IDS:
        return await interaction.response.send_message("❌ Bạn không có quyền sử dụng bot.", ephemeral=True)

    await interaction.response.defer(thinking=True)

    cookie_dict = parse_cookie_str(cookie)
    sessionid = cookie_dict.get("sessionid")
    if not sessionid:
        return await interaction.followup.send("❌ Cookie thiếu sessionid.", ephemeral=True)

    try:
        cl = Client()
        cl.login_by_sessionid(sessionid=sessionid)
    except Exception as e:
        return await interaction.followup.send(f"❌ Đăng nhập thất bại: {e}", ephemeral=True)

    target_list = [t.strip() for t in targets.split(",") if t.strip()]
    if not target_list:
        return await interaction.followup.send("❌ Không có username hoặc thread nào.", ephemeral=True)

    idx = len(SPAM_TASKS) + 1
    stop_set = set()
    spam_info = {
        "thread": None,
        "start_time": datetime.now(),
        "targets": target_list,
        "message": message,
        "delay": delay,
        "client": cl,
        "stop_targets": stop_set
    }

    thread = threading.Thread(target=spam_loop, args=(idx,), daemon=True)
    spam_info["thread"] = thread
    SPAM_TASKS[idx] = spam_info
    thread.start()

    await interaction.followup.send(
        f"✅ Đã bắt đầu spam IG (Tab {idx}):\n"
        f"• Số người nhận: `{len(target_list)}`\n"
        f"• Delay: `{delay}` giây\n"
        f"• Thời gian: `{spam_info['start_time'].strftime('%Y-%m-%d %H:%M:%S')}`",
        ephemeral=True
    )

@tree.command(name="tabtreoig", description="Xem và dừng tab đang treo IG")
async def tabtreoig(interaction: discord.Interaction):
    if str(interaction.user.id) not in ADMIN_IDS:
        return await interaction.response.send_message("❌ Bạn không có quyền sử dụng bot.", ephemeral=True)


    if not SPAM_TASKS:
        return await interaction.response.send_message("⚠️ Không có tab IG nào đang chạy.", ephemeral=True)

    msg = "**📌 Danh sách tab treo IG:**\n"
    for i, (idx, info) in enumerate(SPAM_TASKS.items(), start=1):
        uptime = datetime.now() - info["start_time"]
        msg += (
            f"{idx}. Targets: `{len(info['targets'])}` | Delay: `{info['delay']}s` | "
            f"Up: `{str(uptime).split('.')[0]}`\n"
        )
    msg += "\n🛑 Nhập STT tab muốn dừng (VD: `1`)"

    await interaction.response.send_message(msg, ephemeral=True)

    def check(m: discord.Message):
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

    try:
        reply = await bot.wait_for("message", check=check, timeout=30)
        stt = int(reply.content.strip())
    except:
        return await interaction.followup.send("⏰ Hết thời gian hoặc nhập sai. Không dừng tab nào.", ephemeral=True)

    if stt not in SPAM_TASKS:
        return await interaction.followup.send("❌ STT không hợp lệ.", ephemeral=True)

    task = SPAM_TASKS.pop(stt)
    task["stop_targets"].update(task["targets"])  # stop toàn bộ target
    return await interaction.followup.send(f"✅ Đã dừng tab IG `{stt}`.", ephemeral=True)

@tree.command(
    name="treogmail",
    description="Treo gmail"
)
@app_commands.describe(
    accounts="Email|Passapp",
    to_email="Email nhận",
    content="Nội dung",
    delay="Delay"
)
async def treogmail(
    interaction: discord.Interaction,
    accounts: str,
    to_email: str,
    content: str,
    delay: float
):
    if not is_authorized(interaction) and not is_admin(interaction):
        return await interaction.response.send_message("Bạn không có quyền sử dụng bot", ephemeral=True)
    if delay < 1:
        return await interaction.response.send_message("Delay phải trên 1s", ephemeral=True)

    smtp_list = parse_gmail_accounts(accounts)
    if not smtp_list:
        return await interaction.response.send_message("Không parse được tài khoản", ephemeral=True)

    discord_user_id = str(interaction.user.id)
    stop_evt = threading.Event()
    start_time = datetime.now()

    tab = {
        "thread": None,
        "stop_event": stop_evt,
        "start": start_time,
        "smtp_list": smtp_list,
        "to_email": to_email,
        "content": content,
        "delay": delay
    }
    thread = threading.Thread(target=gmail_spam_loop, args=(tab, discord_user_id), daemon=True)
    tab["thread"] = thread

    with TREOGMAIL_LOCK:
        user_treogmail_tabs.setdefault(discord_user_id, []).append(tab)

    thread.start()

    await interaction.response.send_message(
        f"Đã tạo tab treo gmail cho <@{discord_user_id}>:\n"
        f"• Tài khoản: `{len(smtp_list)}`\n"
        f"• To: `{to_email}`\n"
        f"• Delay: `{delay}` giây\n"
        f"• Bắt đầu: `{start_time.strftime('%Y-%m-%d %H:%M:%S')}`",
        ephemeral=True
    )    
    
@tree.command(
    name="tabtreogmail",
    description="Quản lý/dừng tab treo gmail"
)
async def tabtreogmail(interaction: discord.Interaction):
    if not is_authorized(interaction) and not is_admin(interaction):
        return await interaction.response.send_message("Bạn không có quyền sử dụng bot", ephemeral=True)

    discord_user_id = str(interaction.user.id)
    with TREOGMAIL_LOCK:
        tabs = user_treogmail_tabs.get(discord_user_id, [])

    if not tabs:
        return await interaction.response.send_message("Bạn không có tab treo gmail nào đang hoạt động", ephemeral=True)

    msg = "**Danh sách tab treo gmail của bạn:**\n"
    for i, tab in enumerate(tabs, 1):
        up = datetime.now() - tab["start"]
        msg += (
            f"{i}. Accounts:`{len(tab['smtp_list'])}` → `{tab['to_email']}` | "
            f"Delay:`{tab['delay']}`s | Up:`{str(up).split('.')[0]}`\n"
        )
    msg += f"\nNhập số tab để dừng tab"

    await interaction.response.send_message(msg, ephemeral=True)

    def check(m: discord.Message):
        return m.author.id==interaction.user.id and m.channel.id==interaction.channel.id

    try:
        reply = await bot.wait_for("message", check=check, timeout=30.0)
    except asyncio.TimeoutError:
        return await interaction.followup.send("Hết thời gian. Không dừng tab nào", ephemeral=True)

    c = reply.content.strip()
    if not c.isdigit():
        return await interaction.followup.send("Không dừng tab nào", ephemeral=True)
    idx = int(c)
    if not (1<=idx<=len(tabs)):
        return await interaction.followup.send("Số không hợp lệ", ephemeral=True)

    with TREOGMAIL_LOCK:
        tab = tabs.pop(idx-1)
        tab["stop_event"].set()
        if not tabs:
            user_treogmail_tabs.pop(discord_user_id, None)

    return await interaction.followup.send(f"Đã dừng tab số {idx}", ephemeral=True)
    
@tree.command(name="checkcookie", description="Kiểm tra tối đa 5 cookie Facebook")
@app_commands.describe(
    cookie1="Cookie 1 (tùy chọn)",
    cookie2="Cookie 2 (tùy chọn)",
    cookie3="Cookie 3 (tùy chọn)",
    cookie4="Cookie 4 (tùy chọn)",
    cookie5="Cookie 5 (tùy chọn)"
)
async def checkcookie(
    interaction: discord.Interaction,
    cookie1: str = "",
    cookie2: str = "",
    cookie3: str = "",
    cookie4: str = "",
    cookie5: str = ""
):
    if not is_authorized(interaction) and not is_admin(interaction):
        return await interaction.response.send_message("Bạn không có quyền sử dụng lệnh này", ephemeral=True)

    await interaction.response.defer(ephemeral=True)

    cookies = [cookie1, cookie2, cookie3, cookie4, cookie5]
    result_lines = []

    for idx, ck in enumerate(cookies, start=1):
        if not ck.strip():
            continue  # Bỏ qua ô trống

        try:
            kem = Kem(ck.strip())
            result_lines.append(f"✅ **CK{idx}** sống → UID: `{kem.user_id}`")
        except Exception as e:
            result_lines.append(f"❌ **CK{idx}** die → `{str(e)}`")

    if not result_lines:
        return await interaction.followup.send("❗ Bạn chưa nhập cookie nào.", ephemeral=True)

    await interaction.followup.send(
        "**Kết quả kiểm tra cookie:**\n" + "\n".join(result_lines),
        ephemeral=True
    )                   

def spam_sms_forever(phone, stop_event):
    while not stop_event.is_set():
        for fn in functions:
            if stop_event.is_set():
                break
            try:
                fn(phone)
            except Exception as e:
                print(f"[SPAM] Lỗi từ {fn.__name__}: {e}")
            time.sleep(1)

@tree.command(name="treosms", description="Spam OTP SmS")
@app_commands.describe(sdt="Số điện thoại muốn spam")
async def treosms(interaction: discord.Interaction, sdt: str):
    uid = str(interaction.user.id)
    with TREOSMS_LOCK:
        if uid not in TREOSMS_TASKS:
            TREOSMS_TASKS[uid] = []
        for t in TREOSMS_TASKS[uid]:
            if t["sdt"] == sdt:
                await interaction.response.send_message(f"⚠️ Số {sdt} đã được spam rồi", ephemeral=True)
                return
        stop_event = threading.Event()
        thread = threading.Thread(target=spam_sms_forever, args=(sdt, stop_event), daemon=True)
        thread.start()
        TREOSMS_TASKS[uid].append({"sdt": sdt, "stop_event": stop_event, "start": datetime.now()})
    await interaction.response.send_message(f"✅ Đã bắt đầu spam OTP vào số `{sdt}`", ephemeral=True)

@tree.command(name="tabtreosms", description="Xem và dừng các số đang spam")
async def tabtreosms(interaction: discord.Interaction):
    uid = str(interaction.user.id)
    with TREOSMS_LOCK:
        tabs = TREOSMS_TASKS.get(uid, [])
    if not tabs:
        await interaction.response.send_message("📭 Không có tab treo SMS nào đang chạy", ephemeral=True)
        return
    msg = "**Danh sách tab treo SMS của bạn:**\n"
    for i, tab in enumerate(tabs):
        uptime = datetime.now() - tab["start"]
        mins, secs = divmod(uptime.seconds, 60)
        msg += f"{i+1}. `{tab['sdt']}` - Uptime: {mins} phút {secs} giây\n"
    msg += "\nNhập số thứ tự để dừng tab đó (trong vòng 30s)"
    await interaction.response.send_message(msg, ephemeral=True)
    def check(m):
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id
    try:
        reply = await bot.wait_for("message", timeout=30.0, check=check)
    except:
        await interaction.followup.send("⏰ Hết thời gian", ephemeral=True)
        return
    idx = reply.content.strip()
    if not idx.isdigit():
        await interaction.followup.send("❌ Không hợp lệ", ephemeral=True)
        return
    idx = int(idx) - 1
    with TREOSMS_LOCK:
        if 0 <= idx < len(tabs):
            tabs[idx]["stop_event"].set()
            sdt = tabs[idx]["sdt"]
            tabs.pop(idx)
            if not tabs:
                del TREOSMS_TASKS[uid]
            await interaction.followup.send(f"🛑 Đã dừng spam số `{sdt}`", ephemeral=True)
        else:
            await interaction.followup.send("❌ Không tìm thấy tab", ephemeral=True)

def parse_cookie_string(cookie_str):
    try:
        cookie_str = cookie_str.strip()
        if cookie_str.startswith("{") and cookie_str.endswith("}"):
            data = json.loads(cookie_str)
        else:
            data = {}
            for part in cookie_str.split(";"):
                if "=" in part:
                    k, v = part.strip().split("=", 1)
                    data[k.strip()] = v.strip()

        # Ánh xạ tự động nếu thiếu session_key
        if "session_key" not in data:
            if "zpw_sek" in data:
                data["session_key"] = data["zpw_sek"]

        return data if "session_key" in data else None
    except Exception as e:
        print(f"[!] Lỗi parse cookie: {e}")
        return None

class UserSelectView(discord.ui.View):
    def __init__(self, users, callback, timeout=60):
        super().__init__(timeout=timeout)
        self.callback_fn = callback
        self.add_item(UserDropdown(users, self.callback_fn))

class UserDropdown(discord.ui.Select):
    def __init__(self, users, callback):
        options = [
            discord.SelectOption(label=f"{i+1}. {user}", value=user)
            for i, user in enumerate(users)
        ]
        super().__init__(placeholder="Chọn người nhận để spam...", min_values=1, max_values=len(users), options=options)
        self.callback_fn = callback

    async def callback(self, interaction: discord.Interaction):
        await self.callback_fn(interaction, self.values)

def get_access_token(corp_id, secret):
    url = f'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid={corp_id}&corpsecret={secret}'
    response = requests.get(url).json()
    return response.get('access_token', '')

def send_wecom_msg(token, agent_id, user, msg):
    send_url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}'
    data = {
        "touser": user,
        "msgtype": "text",
        "agentid": agent_id,
        "text": {"content": msg},
        "safe": 0
    }
    return requests.post(send_url, json=data)

@tree.command(name="treowechat", description="Spam tin nhắn WeCom lặp vô hạn")
@app_commands.describe(
    corp_id="CORP_ID của WeCom",
    agent_id="AGENT_ID của ứng dụng",
    secret="SECRET API của WeCom",
    delay="Số giây giữa mỗi lần gửi",
    message="Nội dung tin nhắn muốn gửi",
    users="Danh sách người dùng, phân cách bằng dấu | (vd: user1|user2)"
)
async def treowechat(
    interaction: discord.Interaction,
    corp_id: str,
    agent_id: str,
    secret: str,
    delay: float,
    message: str,
    users: str
):
    if not is_admin(interaction) and not is_authorized(interaction):
        return await interaction.response.send_message("❌ Bạn không có quyền dùng lệnh này!", ephemeral=True)

    await interaction.response.defer(ephemeral=True)

    user_list = [u.strip() for u in users.split("|") if u.strip()]
    if not user_list:
        return await interaction.followup.send("❌ Danh sách người dùng trống!", ephemeral=True)

    token = get_access_token(corp_id, secret)
    if not token:
        return await interaction.followup.send("❌ Không thể lấy access token!", ephemeral=True)

    discord_user_id = str(interaction.user.id)
    stop_event = threading.Event()
    start_time = datetime.now()

    def spam_worker():
        while not stop_event.is_set():
            for user in user_list:
                if stop_event.is_set(): return
                try:
                    res = send_wecom_msg(token, agent_id, user, message)
                    if res.status_code == 200:
                        print(f"[✓] Gửi tới {user}: {message}")
                    else:
                        print(f"[×] Lỗi tới {user}: {res.text}")
                except Exception as e:
                    print(f"[!] Lỗi gửi tới {user}: {e}")
                time.sleep(delay)

    th = threading.Thread(target=spam_worker, daemon=True)

    with WECHAT_SPAM_LOCK:
        if discord_user_id not in wechat_spam_tabs:
            wechat_spam_tabs[discord_user_id] = []
        wechat_spam_tabs[discord_user_id].append({
            "thread": th,
            "stop_event": stop_event,
            "start": start_time,
            "users": user_list,
            "message": message
        })

    th.start()

    await interaction.followup.send(
        f"✅ Đã bắt đầu spam WeCom tới `{', '.join(user_list)}` mỗi `{delay}` giây.\n"
        f"• Tin nhắn: `{message}`\n"
        f"• Số lượng người: `{len(user_list)}`\n"
        f"• Dừng bằng lệnh `/tabwechat` theo STT.",
        ephemeral=True
    )

# Bộ nhớ lưu các tab wechat đang chạy
wechat_tabs = {}  # {discord_user_id: [{"thread": th, "stop_event": stop_event, "start": start_time, "to_user": "ID"}]}
WAITING_WECHAT_STOP = {}  # Tạm lưu trạng thái chờ người dùng chọn STT

@tree.command(name="tabwechat", description="Xem & quản lý các phiên spam WeChat")
async def tabwechat(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    await interaction.response.defer(ephemeral=True)

    if user_id not in wechat_tabs or not wechat_tabs[user_id]:
        return await interaction.followup.send("🔍 Bạn không có tab WeChat nào đang chạy.", ephemeral=True)

    # Hiển thị danh sách tab đang chạy
    text = "📋 **Danh sách tab WeChat đang chạy:**\n"
    for i, tab in enumerate(wechat_tabs[user_id], 1):
        uptime = datetime.now() - tab["start"]
        uptime_str = str(uptime).split('.')[0]  # bỏ mili giây
        text += f"`{i}`. Đang gửi đến: `{tab['to_user']}` | Uptime: `{uptime_str}`\n"

    text += "\n✏️ Nhập số STT (ví dụ `1`, `2`, `3`) để dừng một tab cụ thể."

    WAITING_WECHAT_STOP[user_id] = True
    await interaction.followup.send(text, ephemeral=True)

# Lắng nghe tin nhắn tiếp theo từ user để nhận STT
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    user_id = str(message.author.id)

    if user_id in WAITING_WECHAT_STOP:
        content = message.content.strip()
        if content.isdigit():
            index = int(content) - 1

            if user_id in wechat_tabs and 0 <= index < len(wechat_tabs[user_id]):
                tab = wechat_tabs[user_id][index]
                tab["stop_event"].set()
                wechat_tabs[user_id].pop(index)

                await message.channel.send(f"🛑 Đã dừng tab WeChat số `{content}`.", ephemeral=True)
            else:
                await message.channel.send("❌ STT không hợp lệ!", ephemeral=True)
        else:
            await message.channel.send("⚠️ Vui lòng nhập **số thứ tự** của tab để dừng.", ephemeral=True)

        # Dù đúng hay sai, xoá trạng thái chờ
        WAITING_WECHAT_STOP.pop(user_id, None)

    await bot.process_commands(message)        
    
@tree.command(name="treopollzl", description="Treo spam bình chọn Zalo kèm tag")
@app_commands.describe(
    imei="IMEI Zalo",
    cookie="Cookie Zalo (JSON hoặc thô: key=value;...)",
    poll_options="Mỗi dòng là 1 lựa chọn bình chọn",
    delay="Delay giữa mỗi lần gửi (giây)"
)
async def treopollzl(
    interaction: discord.Interaction,
    imei: str,
    cookie: str,
    poll_options: str,
    delay: float
):
    if not is_authorized(interaction) and not is_admin(interaction):
        return await safe_send(interaction, "Bạn không có quyền dùng lệnh này.", ephemeral=True)

    await interaction.response.defer(thinking=True, ephemeral=True)

    try:
        with open("nhay.txt", "r", encoding="utf-8") as f:
            questions = [line.strip() for line in f if line.strip()]
    except:
        return await interaction.followup.send("❌ Không tìm thấy file `nhay.txt`!", ephemeral=True)

    poll_list = [line.strip() for line in poll_options.split('\n') if line.strip()]
    if not poll_list:
        return await interaction.followup.send("❌ Không có lựa chọn nào trong poll_options!", ephemeral=True)

    cookies = parse_cookie_string(cookie)
    if not cookies:
        return await interaction.followup.send("❌ Cookie không hợp lệ hoặc thiếu `session_key`.", ephemeral=True)

    from tooltreopoll import Bot
    bot = Bot(imei, cookies)

    groups = bot.fetch_groups()
    if not groups:
        return await interaction.followup.send("❌ Không tìm thấy nhóm nào!", ephemeral=True)

    group_msg = "**📋 Danh sách nhóm Zalo:**\n"
    for i, g in enumerate(groups, 1):
        group_msg += f"{i}. {g['name']} — `{g['id']}`\n"

    await interaction.followup.send(group_msg[:2000], ephemeral=True)
    await interaction.followup.send("👉 Nhập STT nhóm muốn gửi poll (VD: `1,2`) trong 30s", ephemeral=True)

    def check_group(m: discord.Message):
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

    try:
        reply = await interaction.client.wait_for("message", check=check_group, timeout=30)
        selected_indexes = [int(x.strip()) for x in reply.content.split(",") if x.strip().isdigit()]
        selected_indexes = [i for i in selected_indexes if 1 <= i <= len(groups)]
    except:
        return await interaction.followup.send("⏱️ Hết thời gian hoặc định dạng không hợp lệ.", ephemeral=True)

    tag_map = {}

    for idx in selected_indexes:
        group = groups[idx - 1]
        members = bot.fetch_members(group['id'])

        mem_msg = f"👥 Thành viên nhóm **{group['name']}**:\n"
        for i, m in enumerate(members, 1):
            mem_msg += f"{i}. {m['name']} — `{m['id']}`\n"
        await interaction.followup.send(mem_msg[:2000], ephemeral=True)
        await interaction.followup.send("👉 Nhập STT thành viên cần tag (VD: `1,2`) trong 30s", ephemeral=True)

        def check_tag(m):
            return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

        try:
            reply_tag = await interaction.client.wait_for("message", check=check_tag, timeout=30)
            tag_indexes = [int(x.strip()) for x in reply_tag.content.split(",") if x.strip().isdigit()]
            tag_indexes = [i for i in tag_indexes if 1 <= i <= len(members)]
        except:
            return await interaction.followup.send("⏱️ Hết thời gian chọn tag.", ephemeral=True)

        tag_users = [members[i - 1] for i in tag_indexes]
        tag_map[group['id']] = {
            'info': group,
            'members': tag_users
        }

    # Khởi động spam poll
    stop_event = threading.Event()
    discord_user_id = str(interaction.user.id)
    start_time = datetime.now()

    def poll_worker():
        while not stop_event.is_set():
            for group_id, data in tag_map.items():
                group = data['info']
                tag_users = data['members']
                for question in questions:
                    if stop_event.is_set():
                        return
                    mention_text = " ".join([f"@{u['name']}" for u in tag_users])
                    poll_text = f"{mention_text} {question}"
                    try:
                        bot.createPoll(question=poll_text, options=poll_list, groupId=group['id'])
                        print(f"📤 Poll đến {group['name']}: {poll_text}")
                    except Exception as e:
                        print(f"❌ Lỗi gửi poll: {e}")
                    time.sleep(delay)

    th = threading.Thread(target=poll_worker, daemon=True)

    with POLL_LOCK:
        if discord_user_id not in user_poll_tabs:
            user_poll_tabs[discord_user_id] = []
        user_poll_tabs[discord_user_id].append({
            "thread": th,
            "stop_event": stop_event,
            "start": start_time,
            "groups": list(tag_map.keys()),
            "delay": delay
        })

    th.start()

    await interaction.followup.send(
        f"✅ Đã bắt đầu spam poll vô hạn.\n"
        f"• Nhóm: `{len(tag_map)}` nhóm\n"
        f"• Delay: `{delay}`s\n"
        f"• Bắt đầu: `{start_time.strftime('%Y-%m-%d %H:%M:%S')}`",
        ephemeral=True
    )
    
@tree.command(name="tabpollzl", description="Quản lý/dừng tab spam poll Zalo")
async def tabpollzl(interaction: discord.Interaction):
    if not is_authorized(interaction) and not is_admin(interaction):
        return await safe_send(interaction, "Bạn không có quyền dùng lệnh này.", ephemeral=True)

    discord_user_id = str(interaction.user.id)
    with POLL_LOCK:
        tabs = user_poll_tabs.get(discord_user_id, [])

    if not tabs:
        return await interaction.response.send_message("❌ Bạn không có tab poll nào đang chạy.", ephemeral=True)

    msg = "**📊 Danh sách tab poll của bạn:**\n"
    for idx, tab in enumerate(tabs, 1):
        uptime = get_uptime(tab["start"])
        groups = ', '.join([f"`{gid}`" for gid in tab["groups"]])
        msg += f"{idx}. 🧾 GroupID(s): {groups}\n   ⏳ Delay: `{tab['delay']}s` | Uptime: `{uptime}`\n"
    msg += "\n👉 Nhập STT tab muốn **dừng** (1 - {}).".format(len(tabs))

    await interaction.response.send_message(msg, ephemeral=True)

    def check(m: discord.Message):
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

    try:
        reply = await bot.wait_for("message", check=check, timeout=30.0)
    except asyncio.TimeoutError:
        return await interaction.followup.send("⏱️ Hết thời gian. Không dừng tab nào.", ephemeral=True)

    c = reply.content.strip()
    if not c.isdigit():
        return await interaction.followup.send("⚠️ Không hợp lệ.", ephemeral=True)
    i = int(c)
    if not (1 <= i <= len(tabs)):
        return await interaction.followup.send("⚠️ Số không hợp lệ.", ephemeral=True)

    with POLL_LOCK:
        chosen = tabs.pop(i - 1)
        chosen["stop_event"].set()
        if not tabs:
            del user_poll_tabs[discord_user_id]

    await interaction.followup.send(f"⛔ Đã dừng tab poll số `{i}`", ephemeral=True)      

@tree.command(name="nhaytagzalo", description="Spam tag zalo fake soạn")
@app_commands.describe(
    imei="IMEI thiết bị Zalo",
    cookie="Cookie Zalo (JSON hoặc thô: key=value;...)",
    delay="Delay giữa các lần gửi (giây)"
)
async def nhaytagzalo(
    interaction: discord.Interaction,
    imei: str,
    cookie: str,
    delay: float
):
    # ✅ Chặn người không có quyền
    if not is_authorized(interaction) and not is_admin(interaction):
        return await interaction.response.send_message("⛔ Bạn không có quyền sử dụng lệnh này.", ephemeral=True)

    await interaction.response.defer(thinking=True, ephemeral=True)

    from toolnhaytagzl import Bot, tag_user_from_nhay, Mention, ThreadType, Message

    def parse_cookie_string(cookie_str):
        try:
            cookie_str = cookie_str.strip()
            if cookie_str.startswith("{") and cookie_str.endswith("}"):
                data = json.loads(cookie_str)
            else:
                data = {}
                for part in cookie_str.split(";"):
                    if "=" in part:
                        k, v = part.strip().split("=", 1)
                        data[k.strip()] = v.strip()
            if "session_key" not in data and "zpw_sek" in data:
                data["session_key"] = data["zpw_sek"]
            return data if "session_key" in data else None
        except Exception as e:
            print(f"[!] Lỗi parse cookie: {e}")
            return None

    cookies = parse_cookie_string(cookie)
    if not cookies:
        return await interaction.followup.send("❌ Cookie không hợp lệ hoặc thiếu session_key.", ephemeral=True)

    bot = Bot(imei, cookies)
    groups = bot.fetch_groups()
    if not groups:
        return await interaction.followup.send("❌ Không tìm thấy nhóm nào!", ephemeral=True)

    group_msg = "**📋 Danh sách nhóm Zalo:**\n"
    for i, g in enumerate(groups, 1):
        group_msg += f"{i}. {g['name']} — `{g['id']}`\n"
    await interaction.followup.send(group_msg[:2000], ephemeral=True)
    await interaction.followup.send("👉 Nhập STT nhóm muốn spam (VD: `1`) trong 30s")

    def check_group(m: discord.Message):
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

    try:
        reply = await interaction.client.wait_for("message", check=check_group, timeout=30)
        index = int(reply.content.strip())
        if not (1 <= index <= len(groups)):
            raise ValueError()
    except:
        return await interaction.followup.send("⏱️ Hết thời gian hoặc STT nhóm không hợp lệ.", ephemeral=True)

    group = groups[index - 1]
    members = bot.fetch_members(group['id'])
    if not members:
        return await interaction.followup.send("❌ Không lấy được danh sách thành viên!", ephemeral=True)

    mem_msg = f"👥 Thành viên nhóm **{group['name']}**:\n"
    for i, m in enumerate(members, 1):
        mem_msg += f"{i}. {m['name']} — `{m['id']}`\n"
    await interaction.followup.send(mem_msg[:2000], ephemeral=True)
    await interaction.followup.send("👉 Nhập STT thành viên muốn tag (VD: `1`)")

    def check_member(m: discord.Message):
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

    try:
        reply = await interaction.client.wait_for("message", check=check_member, timeout=30)
        member_idx = int(reply.content.strip())
        if not (1 <= member_idx <= len(members)):
            raise ValueError()
    except:
        return await interaction.followup.send("⏱️ Hết thời gian hoặc STT không hợp lệ.", ephemeral=True)

    target = members[member_idx - 1]
    target_uid = target['id']
    target_name = target['name']
    thread_id = group['id']

    stop_event = threading.Event()
    thread = threading.Thread(
        target=tag_user_from_nhay,
        args=(bot, target_uid, thread_id, target_name, delay, imei, cookies, stop_event),
        daemon=True
    )
    thread.start()

    discord_user_id = str(interaction.user.id)
    start_time = datetime.now()

    with NHAYTAGZALO_LOCK:
        if discord_user_id not in user_nhaytagzalo_tabs:
            user_nhaytagzalo_tabs[discord_user_id] = []
        user_nhaytagzalo_tabs[discord_user_id].append({
            "thread": thread,
            "stop_event": stop_event,
            "start": start_time,
            "group_name": group['name'],
            "uid": target_uid,
            "target_name": target_name
        })

    await interaction.followup.send(
        f"✅ Bắt đầu spam tag `@{target_name}` mỗi `{delay}`s trong nhóm `{group['name']}`.",
        ephemeral=True
    )
    
@tree.command(name="tabnhaytagzalo", description="Xem & dừng các tab spam tag Zalo")
async def tabnhaytagzalo(interaction: discord.Interaction):
    discord_user_id = str(interaction.user.id)
    with NHAYTAGZALO_LOCK:
        tabs = user_nhaytagzalo_tabs.get(discord_user_id, [])

    if not tabs:
        return await interaction.response.send_message("❌ Bạn không có tab spam tag Zalo nào đang chạy.", ephemeral=True)

    msg = "**📌 Danh sách tab nhây tag Zalo của bạn:**\n"
    for idx, tab in enumerate(tabs, 1):
        uptime = str(datetime.now() - tab["start"]).split('.')[0]
        msg += (
            f"{idx}. 👥 Nhóm: `{tab['group_name']}`\n"
            f"   🧑‍💬 Tag: `{tab['target_name']} ({tab['uid']})`\n"
            f"   ⏱️ Uptime: `{uptime}`\n"
        )
    msg += "\n👉 Nhập STT tab muốn dừng (VD: `1`) trong 30s."

    await interaction.response.send_message(msg[:2000], ephemeral=True)

    def check(m: discord.Message):
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

    try:
        reply = await interaction.client.wait_for("message", check=check, timeout=30)
        index = int(reply.content.strip())
        if not (1 <= index <= len(tabs)):
            raise ValueError("out of range")
    except:
        return await interaction.followup.send("⏱️ Hết thời gian hoặc STT không hợp lệ.", ephemeral=True)

    with NHAYTAGZALO_LOCK:
        tab = tabs.pop(index - 1)
        tab["stop_event"].set()
        if not tabs:
            del user_nhaytagzalo_tabs[discord_user_id]

    await interaction.followup.send(f"⛔ Đã dừng tab spam tag Zalo số `{index}`.", ephemeral=True)

                                                
@tree.command(name="treosticker", description="Treo spam sticker vào nhóm Zalo")
@app_commands.describe(
    imei="IMEI thiết bị Zalo",
    cookie="Cookie Zalo (JSON hoặc thô: key=value;...)",
    delay="Thời gian chờ giữa mỗi lần gửi (giây)"
)
async def treosticker(
    interaction: discord.Interaction,
    imei: str,
    cookie: str,
    delay: float
):
    # ✅ Giới hạn người dùng
    if not is_authorized(interaction) and not is_admin(interaction):
        return await interaction.response.send_message("⛔ Bạn không có quyền sử dụng lệnh này.", ephemeral=True)

    await interaction.response.defer(thinking=True, ephemeral=True)

    import json, threading
    from datetime import datetime
    from spamstk import Bot

    def parse_cookie_string(cookie_str):
        try:
            cookie_str = cookie_str.strip()
            if cookie_str.startswith("{") and cookie_str.endswith("}"):
                return json.loads(cookie_str)
            data = {}
            for part in cookie_str.split(";"):
                if "=" in part:
                    k, v = part.strip().split("=", 1)
                    data[k.strip()] = v.strip()
            if "session_key" not in data and "zpw_sek" in data:
                data["session_key"] = data["zpw_sek"]
            return data if "session_key" in data else None
        except:
            return None

    cookies = parse_cookie_string(cookie)
    if not cookies:
        return await interaction.followup.send("❌ Cookie không hợp lệ!", ephemeral=True)

    bot = Bot(imei, cookies)
    groups = bot.fetch_groups()
    if not groups:
        return await interaction.followup.send("❌ Không tìm thấy nhóm nào!", ephemeral=True)

    group_msg = "**📋 Danh sách nhóm Zalo:**\n"
    for i, g in enumerate(groups, 1):
        group_msg += f"{i}. {g['name']} — `{g['id']}`\n"
    await interaction.followup.send(group_msg[:2000], ephemeral=True)
    await interaction.followup.send("👉 Nhập STT nhóm muốn spam (trong 30s)")

    def check_group(m: discord.Message):
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

    try:
        reply = await interaction.client.wait_for("message", check=check_group, timeout=30)
        index = int(reply.content.strip())
        if index < 1 or index > len(groups):
            raise ValueError()
    except:
        return await interaction.followup.send("⏱️ Hết thời gian hoặc STT không hợp lệ!", ephemeral=True)

    group = groups[index - 1]

    await interaction.followup.send("🎭 Chọn loại sticker:\n1. 👊 Nấm đấm\n2. 🎂 Happy Birthday\n👉 Trả lời bằng số:", ephemeral=True)

    def check_sticker(m: discord.Message):
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

    try:
        sticker_reply = await interaction.client.wait_for("message", check=check_sticker, timeout=30)
        choice = sticker_reply.content.strip()
        if choice == "1":
            sticker_id, cate_id = 23339, 10425
        elif choice == "2":
            sticker_id, cate_id = 21979, 10194
        else:
            raise ValueError()
    except:
        return await interaction.followup.send("❌ Lựa chọn không hợp lệ hoặc hết thời gian!", ephemeral=True)

    stop_event = threading.Event()
    thread = threading.Thread(
        target=bot.spam_sticker_loop,
        args=(group['id'], group['name'], sticker_id, cate_id, delay, stop_event),
        daemon=True
    )
    thread.start()

    discord_user_id = str(interaction.user.id)
    start_time = datetime.now()

    with TREOSTICKER_LOCK:
        if discord_user_id not in user_sticker_tabs:
            user_sticker_tabs[discord_user_id] = []
        user_sticker_tabs[discord_user_id].append({
            "thread": thread,
            "stop_event": stop_event,
            "start": start_time,
            "group_name": group['name']
        })

    await interaction.followup.send(
        f"✅ Bắt đầu spam sticker vào nhóm `{group['name']}` mỗi `{delay}`s.",
        ephemeral=True
    )
    
@tree.command(name="tabtreosticker", description="Quản lý các sticker đang spam")
async def tabtreosticker(interaction: discord.Interaction):
    discord_user_id = str(interaction.user.id)

    with TREOSTICKER_LOCK:
        tabs = user_sticker_tabs.get(discord_user_id, [])

    if not tabs:
        return await interaction.response.send_message("❌ Không có sticker nào đang chạy!", ephemeral=True)

    tab_msg = "**📌 Các nhóm đang spam sticker:**\n"
    for i, tab in enumerate(tabs, 1):
        start_time = tab["start"].strftime("%Y-%m-%d %H:%M:%S")
        tab_msg += f"{i}. `{tab['group_name']}` — Bắt đầu: `{start_time}`\n"
    tab_msg += "\n👉 Gõ STT để dừng (trong 30s)."

    await interaction.response.send_message(tab_msg, ephemeral=True)

    def check(m: discord.Message):
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

    try:
        reply = await interaction.client.wait_for("message", check=check, timeout=30)
        index = int(reply.content.strip())
        if index < 1 or index > len(tabs):
            raise ValueError()
    except:
        return await interaction.followup.send("⏱️ Hết thời gian hoặc STT không hợp lệ!", ephemeral=True)

    with TREOSTICKER_LOCK:
        stop_tab = user_sticker_tabs[discord_user_id].pop(index - 1)
        stop_tab["stop_event"].set()

    await interaction.followup.send("🛑 Đã dừng spam sticker!", ephemeral=True)  
def get_uid_fbdtsg(ck):
    try:
        headers = {
            'Accept': 'text/html',
            'Cookie': ck,
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        }

        response = requests.get('https://www.facebook.com/', headers=headers)
        html_content = response.text

        if '"USER_ID":"' not in html_content:
            return None, None, None, None, None, None

        user_id = re.search(r'"USER_ID":"(\d+)"', html_content)
        fb_dtsg = re.search(r'"f":"([^"]+)"', html_content)
        jazoest = re.search(r'jazoest=(\d+)', html_content)
        rev = re.search(r'"server_revision":(\d+),"client_revision":(\d+)', html_content)
        a = re.search(r'__a=(\d+)', html_content)

        user_id = user_id.group(1) if user_id else None
        fb_dtsg = fb_dtsg.group(1) if fb_dtsg else None
        jazoest = jazoest.group(1) if jazoest else None
        rev = rev.group(1) if rev else None
        a = a.group(1) if a else "1"
        req = "1b"

        if not all([user_id, fb_dtsg, jazoest, rev]):
            return None, None, None, None, None, None

        return user_id, fb_dtsg, rev, req, a, jazoest

    except Exception as e:
        print(f"Lỗi Khi Check Cookie: {e}")
        return None, None, None, None, None, None

def upload_image_get_fbid(image_path_or_url: str, ck: str) -> str:
    result = get_uid_fbdtsg(ck)
    if not result or len(result) != 6 or any(v is None for v in result):
        return "Không thể lấy thông tin từ cookie. Vui lòng kiểm tra lại."

    user_id, fb_dtsg, rev, req, a, jazoest = result

    is_url = image_path_or_url.startswith("http://") or image_path_or_url.startswith("https://")
    try:
        if is_url:
            resp = requests.get(image_path_or_url)
            if resp.status_code != 200:
                return "Không thể tải ảnh từ URL."
            img_data = BytesIO(resp.content)
            img_data.name = "image.jpg"
        else:
            if not os.path.isfile(image_path_or_url):
                return "File không tồn tại. Hãy nhập đúng đường dẫn tới ảnh."
            img_data = open(image_path_or_url, 'rb')
    except Exception as e:
        return f"Lỗi khi đọc ảnh: {e}"

    headers = {
        'cookie': ck,
        'origin': 'https://www.facebook.com',
        'referer': 'https://www.facebook.com/',
        'user-agent': 'Mozilla/5.0',
        'x-fb-lsd': fb_dtsg,
    }

    params = {
        'av': user_id,
        'profile_id': user_id,
        'source': '19',
        'target_id': user_id,
        '__user': user_id,
        '__a': a,
        '__req': req,
        '__rev': rev,
        'fb_dtsg': fb_dtsg,
        'jazoest': jazoest,
    }

    try:
        files = {
            'file': (img_data.name, img_data, 'image/jpeg')
        }

        response = requests.post(
            'https://www.facebook.com/ajax/ufi/upload/',
            headers=headers,
            params=params,
            files=files
        )

        if is_url:
            img_data.close()

        text = response.text.strip()
        if text.startswith("for(;;);"):
            text = text[8:]

        try:
            data = json.loads(text)
            fbid = data.get("payload", {}).get("fbid")
            if fbid:
                return fbid
            return "Không tìm thấy fbid trong JSON."
        except json.JSONDecodeError:
            match = re.search(r'"fbid"\s*:\s*"(\d+)"', text)
            if match:
                return match.group(1)
            return "Không tìm thấy fbid trong text."

    except Exception as e:
        return f"Lỗi khi upload: {e}"                                                                                                              
@tree.command(name="reostr", description="Spam story ảnh + tag UID từ file nhay.txt")
@app_commands.describe(
    cookie="Cookie Facebook",
    image_link="Đường dẫn ảnh (URL hoặc local path)",
    uid_tag="UID cần tag vào ảnh",
    delay="Delay giữa mỗi lần gửi (giây)"
)
async def reostr(
    interaction: discord.Interaction,
    cookie: str,
    image_link: str,
    uid_tag: str,
    delay: float
):
    if not is_admin(interaction) and not is_authorized(interaction):
        return await safe_send(interaction, "⛔ Bạn không có quyền dùng lệnh này", ephemeral=True)

    await interaction.response.defer(thinking=True, ephemeral=True)

    info = get_uid_fbdtsg(cookie)
    if not info:
        return await interaction.followup.send("❌ Cookie không hợp lệ hoặc thiếu dữ liệu", ephemeral=True)

    user_id, fb_dtsg, rev, req, a, jazoest = info

    if not os.path.exists("nhay.txt"):
        return await interaction.followup.send("❌ Không tìm thấy file nhay.txt!", ephemeral=True)

    with open("nhay.txt", "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        return await interaction.followup.send("❌ File nhay.txt không có nội dung!", ephemeral=True)

    stop_event = threading.Event()
    discord_user_id = str(interaction.user.id)
    start_time = datetime.now()

    def reostr_worker():
        headers = {
            'content-type': 'application/x-www-form-urlencoded',
            'cookie': cookie,
            'origin': 'https://www.facebook.com',
            'referer': 'https://www.facebook.com/stories/create',
            'user-agent': 'Mozilla/5.0',
            'x-fb-friendly-name': 'StoriesCreateMutation',
            'x-fb-lsd': fb_dtsg,
        }

        while not stop_event.is_set():
            for content_text in lines:
                if stop_event.is_set():
                    break

                # 🔁 Upload ảnh mỗi lần gửi
                fbid = upload_image_get_fbid(image_link, cookie)
                if not isinstance(fbid, str) or not fbid.isdigit():
                    print(f"❌ Lỗi upload ảnh: {fbid}")
                    continue  # bỏ qua nếu upload thất bại

                variables = {
                    "input": {
                        "audiences": [{"stories": {"self": {"target_id": user_id}}}],
                        "audiences_is_complete": True,
                        "logging": {"composer_session_id": ""},
                        "navigation_data": {"attribution_id_v2": "StoriesCreateRoot.react"},
                        "source": "WWW",
                        "message": {"ranges": [], "text": content_text},
                        "attachments": [{
                            "photo": {
                                "id": fbid,
                                "overlays": [{
                                    "tag_sticker": {
                                        "bounds": {
                                            "height": 0.0356,
                                            "rotation": 0,
                                            "width": 0.3764,
                                            "x": 0.3944,
                                            "y": 0.4582
                                        },
                                        "creation_source": "TEXT_TOOL_MENTION",
                                        "tag_id": uid_tag,
                                        "type": "PEOPLE"
                                    }
                                }]
                            }
                        }],
                        "tracking": [None],
                        "actor_id": user_id,
                        "client_mutation_id": str(time.time())
                    }
                }

                data = {
                    '__user': user_id,
                    '__a': a,
                    '__req': req,
                    'fb_dtsg': fb_dtsg,
                    'jazoest': jazoest,
                    'lsd': fb_dtsg,
                    'variables': json.dumps(variables),
                    'doc_id': '7490607150987409',
                }

                try:
                    requests.post('https://www.facebook.com/api/graphql/', headers=headers, data=data)
                    print(f"✅ Gửi story: {content_text}")
                except Exception as e:
                    print(f"❌ Lỗi gửi story: {e}")

                time.sleep(delay)

    th = threading.Thread(target=reostr_worker, daemon=True)
    th.start()

    with TAB_LOCK:
        if discord_user_id not in user_reostr_tabs:
            user_reostr_tabs[discord_user_id] = []
        user_reostr_tabs[discord_user_id].append({
            "thread": th,
            "stop_event": stop_event,
            "start": start_time,
            "fbid": None,  # không cần lưu fbid cố định nữa
            "delay": delay,
            "uid_tag": uid_tag
        })

    await interaction.followup.send(
        f"✅ Đã bắt đầu spam story ảnh tag UID `{uid_tag}` mỗi `{delay}` giây (mỗi lần upload lại ảnh).",
        ephemeral=True
    )

@tree.command(name="tabreostr", description="Xem và dừng các tab story ảnh đang chạy")
async def tabreostr(interaction: discord.Interaction):
    if not is_admin(interaction) and not is_authorized(interaction):
        return await safe_send(interaction, "Bạn không có quyền dùng lệnh này", ephemeral=True)

    discord_user_id = str(interaction.user.id)
    with TAB_LOCK:
        tabs = user_reostr_tabs.get(discord_user_id, [])

    if not tabs:
        return await safe_send(interaction, "❌ Không có tab nào đang hoạt động", ephemeral=True)

    msg = "**Danh sách tab reostr của bạn:**\n"
    for idx, tab in enumerate(tabs, 1):
        uptime = get_uptime(tab["start"])
        msg += f"{idx}. UID: `{tab['uid_tag']}` | Delay: `{tab['delay']}`s | Uptime: `{uptime}`\n"
    msg += "\n➡️ Nhập số thứ tự của tab bạn muốn **dừng**."

    await interaction.response.send_message(msg, ephemeral=True)

    def check(m: discord.Message):
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

    try:
        reply = await bot.wait_for("message", check=check, timeout=30.0)
    except asyncio.TimeoutError:
        return await interaction.followup.send("⏱️ Hết thời gian. Không dừng tab nào.", ephemeral=True)

    index = reply.content.strip()
    if not index.isdigit():
        return await interaction.followup.send("⚠️ Không hợp lệ.", ephemeral=True)

    i = int(index)
    if not (1 <= i <= len(tabs)):
        return await interaction.followup.send("⚠️ Số không hợp lệ.", ephemeral=True)

    with TAB_LOCK:
        chosen = tabs.pop(i - 1)
        chosen["stop_event"].set()
        if not tabs:
            del user_reostr_tabs[discord_user_id]

    await interaction.followup.send(f"⛔ Đã dừng tab reostr số `{i}`", ephemeral=True)

from toolrnboxzl import ZaloRenameBot
import threading
from datetime import datetime

@tree.command(name="nhaynameboxzl", description="Đổi tên box Zalo liên tục từ nhay.txt")
@app_commands.describe(
    imei="IMEI thiết bị Zalo",
    cookie="Cookie Zalo (JSON hoặc key=value;...)",
    delay="Delay giữa mỗi lần đổi tên (giây)"
)
async def nhaynameboxzl(interaction: discord.Interaction, imei: str, cookie: str, delay: float):
    if not is_admin(interaction) and not is_authorized(interaction):
        return await interaction.response.send_message("⛔ Bạn không có quyền dùng lệnh này.", ephemeral=True)

    await interaction.response.defer(ephemeral=True)


    def parse_cookie_string(cookie_str):
        try:
            cookie_str = cookie_str.strip()
            if cookie_str.startswith("{") and cookie_str.endswith("}"):
                data = json.loads(cookie_str)
            else:
                data = {}
                for part in cookie_str.split(";"):
                    if "=" in part:
                        k, v = part.strip().split("=", 1)
                        data[k.strip()] = v.strip()

            if "session_key" not in data and "zpw_sek" in data:
                data["session_key"] = data["zpw_sek"]

            return data
        except Exception as e:
            print(f"[!] Lỗi parse cookie: {e}")
            return None

    cookies = parse_cookie_string(cookie)
    if not cookies or "session_key" not in cookies:
        return await interaction.followup.send("❌ Cookie không hợp lệ hoặc thiếu session_key.", ephemeral=True)

    bot = ZaloRenameBot(imei, cookies)
    groups = bot.fetch_groups()
    if not groups:
        return await interaction.followup.send("❌ Không tìm thấy nhóm nào!", ephemeral=True)

    msg = "**📋 Danh sách nhóm:**\n"
    for i, g in enumerate(groups, 1):
        msg += f"{i}. {g['name']} — `{g['id']}`\n"
    await interaction.followup.send(msg[:2000], ephemeral=True)
    await interaction.followup.send("👉 Nhập STT nhóm muốn đổi tên (trong 30s):")

    def check(m): return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

    try:
        reply = await interaction.client.wait_for("message", check=check, timeout=30)
        index = int(reply.content.strip())
        if index < 1 or index > len(groups):
            raise ValueError()
    except:
        return await interaction.followup.send("❌ STT không hợp lệ hoặc hết thời gian.", ephemeral=True)

    group = groups[index - 1]
    stop_event = threading.Event()
    thread = threading.Thread(target=bot.rename_loop, args=(group['id'], delay, stop_event), daemon=True)
    thread.start()

    discord_user_id = str(interaction.user.id)
    start_time = datetime.now()
    global nhaynameboxzl_tabs
    if discord_user_id not in nhaynameboxzl_tabs:
        nhaynameboxzl_tabs[discord_user_id] = []

    nhaynameboxzl_tabs[discord_user_id].append({
        "thread": thread,
        "stop_event": stop_event,
        "start": start_time,
        "group": group
    })

    await interaction.followup.send(
        f"✅ Đã bắt đầu spam đổi tên nhóm `{group['name']}` mỗi {delay}s!",
        ephemeral=True
    )
    
@tree.command(name="tabnhaynameboxzl", description="Xem và dừng tab đổi tên nhóm Zalo")
async def tabnhaynameboxzl(interaction: discord.Interaction):
    if not is_admin(interaction) and not is_authorized(interaction):
        return await interaction.response.send_message("⛔ Bạn không có quyền dùng lệnh này.", ephemeral=True)

    discord_user_id = str(interaction.user.id)
    tabs = nhaynameboxzl_tabs.get(discord_user_id)
    if not tabs:
        return await interaction.response.send_message("❌ Không có tab nào đang chạy!", ephemeral=True)

    msg = "**📂 Danh sách tab đang chạy:**\n"
    for i, tab in enumerate(tabs, 1):
        uptime = datetime.now() - tab["start"]
        msg += f"{i}. Nhóm: `{tab['group']['name']}` — Uptime: `{str(uptime).split('.')[0]}`\n"
    msg += "\n👉 Nhập STT tab muốn dừng (trong 30s):"

    await interaction.response.send_message(msg[:2000], ephemeral=True)

    def check(m): return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

    try:
        reply = await interaction.client.wait_for("message", check=check, timeout=30)
        index = int(reply.content.strip())
        if index < 1 or index > len(tabs):
            raise ValueError()
    except:
        return await interaction.followup.send("❌ STT không hợp lệ hoặc hết thời gian.", ephemeral=True)

    tabs[index - 1]["stop_event"].set()
    tabs.pop(index - 1)
    await interaction.followup.send("🛑 Đã dừng tab thành công!", ephemeral=True)

import threading, os, time, re, discord
from discord import app_commands
from nenMqtt import MQTTThemeClient

USER_TASKS = {}


class SetThemeModal(discord.ui.Modal, title="Set Theme Messenger"):
    cookie = discord.ui.TextInput(label="Cookie Facebook", style=discord.TextStyle.paragraph, required=True)
    box_id = discord.ui.TextInput(label="ID Box/Thread", placeholder="Nhập ID nhóm chat", required=True)
    delay = discord.ui.TextInput(label="Delay (giây)", placeholder="Ví dụ: 5", default="5", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        if not is_admin(interaction) and not is_authorized(interaction):
            embed = discord.Embed(
                title="❌ Lỗi quyền hạn",
                description="Bạn không có quyền sử dụng lệnh này.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed)

        try:
            cookie = str(self.cookie.value).strip()
            box_id = re.sub(r"[^\d]", "", str(self.box_id.value))
            delay = max(float(self.delay.value), 2.0)  

            if not box_id:
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description="ID box không hợp lệ.",
                    color=discord.Color.red()
                )
                return await interaction.response.send_message(embed=embed)

            stop_event = threading.Event()

            def run_set_theme():
                client = None
                try:
                    client = MQTTThemeClient(cookie)
                    client.connect()
                    while not stop_event.wait(delay):  
                        try:
                            client.set_theme(box_id)
                        except Exception as e:
                            print(f"[⚠️] Lỗi set theme: {e}")
                            time.sleep(3)
                except Exception as e:
                    print(f"[❌] Thread lỗi nghiêm trọng: {e}")
                finally:
                    if client:
                        try:
                            client.disconnect()
                        except:
                            pass
                    print(f"[🛑] Task set theme {box_id} dừng.")

            t = threading.Thread(target=run_set_theme, daemon=True)
            t.start()

            if interaction.user.id not in USER_TASKS:
                USER_TASKS[interaction.user.id] = []

            USER_TASKS[interaction.user.id].append({
                "stop_event": stop_event,
                "thread": t,
                "box_id": box_id,
                "delay": delay
            })

            embed = discord.Embed(
                title="✅ Task Set Theme đã bắt đầu",
                description=(
                    f"**Box ID:** `{box_id}`\n"
                    f"**Delay:** `{delay}` giây\n"
                    f"**Người tạo:** {interaction.user.mention}\n\n"
                    f"⚙️ Bot sẽ set theme liên tục cho box này."
                ),
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="❌ Lỗi",
                description=str(e),
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)


@tree.command(name="setnenmess", description="Set theme Messenger liên tục")
async def settheme(interaction: discord.Interaction):
    if not is_admin(interaction) and not is_authorized(interaction):
        embed = discord.Embed(
            title="❌ Lỗi quyền hạn",
            description="Bạn không có quyền sử dụng lệnh này.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    embed = discord.Embed(
        title="🎨 Set Theme Messenger siêu múp",
        description="Ấn **Bắt đầu** để điền thông tin cần thiết.",
        color=discord.Color.yellow()
    )
    view = discord.ui.View()
    button = discord.ui.Button(label="Bắt đầu", style=discord.ButtonStyle.secondary)

    async def button_callback(btn_inter: discord.Interaction):
        await btn_inter.response.send_modal(SetThemeModal())

    button.callback = button_callback
    view.add_item(button)
    await interaction.response.send_message(embed=embed, view=view)


@tree.command(name="tabsetnenmess", description="Quản lý và dừng task set theme")
@app_commands.describe(stop="Nhập số task để dừng (ví dụ: 1) hoặc All để dừng tất cả")
async def tabsettheme(interaction: discord.Interaction, stop: str = None):
    if not is_admin(interaction) and not is_authorized(interaction):
        embed = discord.Embed(
            title="❌ Lỗi quyền hạn",
            description="Bạn không có quyền sử dụng lệnh này.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    user_id = interaction.user.id
    tasks = USER_TASKS.get(user_id, [])

    if not tasks:
        embed = discord.Embed(
            title="📋 Danh sách task",
            description="❌ Bạn không có task nào đang chạy.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    if stop:
        if stop.lower() == "all":
            for task in tasks:
                task["stop_event"].set()
            USER_TASKS[user_id] = []
            embed = discord.Embed(
                title="🛑 Dừng task",
                description="✅ Đã dừng tất cả task set theme.",
                color=discord.Color.green()
            )
            return await interaction.response.send_message(embed=embed)

        try:
            num = int(stop) - 1
            if 0 <= num < len(tasks):
                task = tasks.pop(num)
                task["stop_event"].set()
                embed = discord.Embed(
                    title="🛑 Dừng task",
                    description=f"✅ Đã dừng task số **{stop}**.",
                    color=discord.Color.green()
                )
                return await interaction.response.send_message(embed=embed)
            else:
                raise ValueError
        except:
            embed = discord.Embed(
                title="⚠️ Lỗi",
                description="Vui lòng nhập số hợp lệ hoặc 'all'.",
                color=discord.Color.orange()
            )
            return await interaction.response.send_message(embed=embed)

    desc = ""
    for idx, task in enumerate(tasks, 1):
        desc += f"**{idx}.** Box `{task['box_id']}` | Delay: {task['delay']}s\n"

    embed = discord.Embed(
        title="📋 Danh sách task Set Theme",
        description=desc + "\n👉 Dùng `/tabsetnenmess stop:<số>` để dừng task.\n👉 Dùng `/tabsetnenmess stop:all` để dừng tất cả.",
        color=discord.Color.orange()
    )
    await interaction.response.send_message(embed=embed)



import asyncio, discord, os, re, shutil, time
from discord import app_commands
from discord.ui import Button, View
from module.nhaypoll import start_nhay_poll_func

USER_POLL_TASKS = {}
USER_POLL_LOCK = asyncio.Lock()

class NhayPollModal(discord.ui.Modal, title="Nhây Poll Messenger"):
    cookie = discord.ui.TextInput(label="Cookie Facebook", style=discord.TextStyle.paragraph, required=True)
    box_id = discord.ui.TextInput(label="ID Box/Thread", placeholder="Nhập ID nhóm chat", required=True)
    delay = discord.ui.TextInput(label="Delay (giây)", placeholder="Ví dụ: 30", default="30", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        if not is_authorized(interaction) and not is_admin(interaction):
            return await interaction.response.send_message("❌ Bạn không có quyền sử dụng bot.", ephemeral=True)

        await interaction.response.defer(thinking=True, ephemeral=True)

        try:
            cookie = str(self.cookie.value).strip()
            box_id = re.sub(r"[^\d]", "", str(self.box_id.value))
            delay = max(float(self.delay.value), 1.0)

            if not box_id:
                return await interaction.followup.send("❌ ID box không hợp lệ.", ephemeral=True)

            folder_name = f"nhaypoll_{interaction.user.id}_{int(time.time())}"
            folder_path = os.path.join("data", folder_name)
            os.makedirs(folder_path, exist_ok=True)

            stop_event = asyncio.Event()
            loop = asyncio.get_event_loop()

            async def run_nhay_poll():
                try:
                    while not stop_event.is_set():
                        try:
                            await loop.run_in_executor(None, start_nhay_poll_func, cookie, box_id, delay, folder_name)
                        except Exception as e:
                            print(f"[⚠️] Lỗi nhây poll: {e}")
                            await asyncio.sleep(3)
                        await asyncio.sleep(delay)
                finally:
                    if os.path.exists(folder_path):
                        try:
                            shutil.rmtree(folder_path)
                        except Exception:
                            pass
                    print(f"[🛑] Task nhây poll {box_id} dừng.")

            task = asyncio.create_task(run_nhay_poll())

            async with USER_POLL_LOCK:
                if interaction.user.id not in USER_POLL_TASKS:
                    USER_POLL_TASKS[interaction.user.id] = []
                USER_POLL_TASKS[interaction.user.id].append({
                    "stop_event": stop_event,
                    "task": task,
                    "box_id": box_id,
                    "delay": delay
                })

            embed = discord.Embed(
                title="✅ Task Nhây Poll đã bắt đầu",
                description=(
                    f"**Box ID:** `{box_id}`\n"
                    f"**Delay:** `{delay}` giây\n"
                    f"**Người tạo:** {interaction.user.mention}\n\n"
                    f"⚙️ Bot sẽ tạo poll liên tục cho box này."
                ),
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed)

        except Exception as e:
            print(f"[❌] Lỗi trong on_submit: {e}")
            await interaction.followup.send("❌ Đã xảy ra lỗi khi xử lý yêu cầu.", ephemeral=True)


@tree.command(name="nhaypollmess", description="Tạo nhây poll Messenger")
async def nhaypollmess(interaction: discord.Interaction):
    if not is_authorized(interaction) and not is_admin(interaction):
        return await interaction.response.send_message("❌ Bạn không có quyền sử dụng bot.", ephemeral=True)

    embed = discord.Embed(
        title="📊 Nhây Poll Messenger",
        description="Ấn **Start** để điền thông tin cần thiết.",
        color=discord.Color.blue()
    )
    view = View()
    button = Button(label="Start", style=discord.ButtonStyle.secondary)

    async def button_callback(btn_inter: discord.Interaction):
        await btn_inter.response.send_modal(NhayPollModal())

    button.callback = button_callback
    view.add_item(button)
    await interaction.response.send_message(embed=embed, view=view)


@tree.command(name="tabnhaypollmess", description="Quản lý và dừng task nhây poll")
@app_commands.describe(stop="Nhập số task để dừng (ví dụ: 1) hoặc 'all' để dừng tất cả")
async def tabnhaypollmess(interaction: discord.Interaction, stop: str = None):
    if not is_authorized(interaction) and not is_admin(interaction):
        return await interaction.response.send_message("❌ Bạn không có quyền sử dụng bot.", ephemeral=True)

    user_id = interaction.user.id

    async with USER_POLL_LOCK:
        tasks = USER_POLL_TASKS.get(user_id, [])

    if not tasks:
        return await interaction.response.send_message("❌ Bạn không có task nhây poll nào đang chạy.", ephemeral=True)

    if stop:
        if stop.lower() == "all":
            async with USER_POLL_LOCK:
                for task in tasks:
                    task["stop_event"].set()
                    task["task"].cancel()
                USER_POLL_TASKS[user_id] = []
            return await interaction.response.send_message("✅ Đã dừng tất cả task nhây poll.", ephemeral=True)

        try:
            num = int(stop) - 1
            if 0 <= num < len(tasks):
                async with USER_POLL_LOCK:
                    task = tasks.pop(num)
                    task["stop_event"].set()
                    task["task"].cancel()
                    if not tasks:
                        USER_POLL_TASKS.pop(user_id, None)
                return await interaction.response.send_message(f"✅ Đã dừng task số `{stop}`.", ephemeral=True)
            else:
                raise ValueError
        except:
            return await interaction.response.send_message("⚠️ Vui lòng nhập số hợp lệ hoặc 'all'.", ephemeral=True)

    desc = ""
    for idx, task in enumerate(tasks, 1):
        desc += f"**{idx}.** Box `{task['box_id']}` | Delay: `{task['delay']}s`\n"

    embed = discord.Embed(
        title="📋 Danh sách task nhây Poll",
        description=desc + "\n👉 Dùng `/tabnhaypollmess stop:<số>` để dừng task.\n👉 Dùng `/tabnhaypollmess stop:all` để dừng tất cả.",
        color=discord.Color.orange()
    )
    await interaction.response.send_message(embed=embed)



from raid import FacebookGroupManager, dataGetHome 

LOG_FILE = "raid_log.txt"
UID_FILE = "users.txt"

def read_uid_list():
    if not os.path.exists(UID_FILE):
        return []
    with open(UID_FILE, "r", encoding="utf-8") as f:
        uids = [line.strip() for line in f if line.strip().isdigit()]
    return uids


def write_log(result):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")




def get_box_name(cookie, box_id):
    return "Unknown"

class RaidBoxModal(discord.ui.Modal, title="Raid Box Messenger (Tag UID 1 lần)"):
    cookie = discord.ui.TextInput(
        label="Cookie Facebook",
        style=discord.TextStyle.paragraph,
        required=True
    )
    box_id = discord.ui.TextInput(
        label="ID Box/Thread",
        placeholder="Nhập ID nhóm chat (thread_fbid)",
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=True)

        if not is_authorized(interaction) and not is_admin(interaction):
            return await interaction.followup.send(
                embed=discord.Embed(
                    title="❌ Lỗi quyền hạn",
                    description="Bạn không có quyền sử dụng bot này.",
                    color=discord.Color.red()
                )
            )

        try:
            cookie = self.cookie.value.strip()
            box_id = re.sub(r"[^\d]", "", self.box_id.value.strip())

            uid_list = read_uid_list()
            if not uid_list:
                raise ValueError("File `users.txt` trống hoặc không có UID hợp lệ.")

            fb = FacebookGroupManager(dataGetHome(cookie))

            def run_tag():
                result = fb.add_user_to_group(uid_list, box_id)
                write_log(result)

            thread = threading.Thread(target=run_tag, daemon=True)
            thread.start()

            box_name = get_box_name(cookie, box_id)
            embed = discord.Embed(
                title="✅ Tag UID đang chạy!",
                description=(
                    f"**Box ID:** `{box_id}`\n"
                    f"**Tên Box:** `{box_name}`\n"
                    f"**Số UID:** `{len(uid_list)}`\n"
                    f"📂 Log sẽ lưu tại: `{LOG_FILE}`"
                ),
                color=discord.Color.green()
            )
            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(
                embed=discord.Embed(
                    title="❌ Lỗi không xác định",
                    description=f"Đã xảy ra lỗi: `{e}`",
                    color=discord.Color.red()
                )
            )

@tree.command(name="raidbox", description="Tag tất cả UID trong users.txt vào box Messenger")
async def raidbox(interaction: discord.Interaction):
    if not is_authorized(interaction) and not is_admin(interaction):
        return await interaction.response.send_message(
            embed=discord.Embed(
                title="❌ Lỗi quyền hạn",
                description="Bạn không có quyền sử dụng bot này.",
                color=discord.Color.red()
            )
        )

    embed = discord.Embed(
        title="📞 Raid Box Messenger",
        description="Nhấn **Start** để nhập cookie và ID box.",
        color=discord.Color.red()
    )
    view = discord.ui.View()
    button = discord.ui.Button(label="Start", style=discord.ButtonStyle.secondary)

    async def on_click(btn_inter: discord.Interaction):
        await btn_inter.response.send_modal(RaidBoxModal())

    button.callback = on_click
    view.add_item(button)

    await interaction.response.send_message(embed=embed, view=view)
    
    
from module.username import FacebookNicknameChanger  
USER_NAMECHANGE_TASKS = {}


class NameChangeModal(discord.ui.Modal, title="Name Change Messenger"):
    cookie = discord.ui.TextInput(label="Cookie Facebook", style=discord.TextStyle.paragraph, required=True)
    box_id = discord.ui.TextInput(label="ID Box/Thread", placeholder="Nhập ID nhóm chat", required=True)
    delay = discord.ui.TextInput(label="Delay (giây)", placeholder="Ví dụ: 5", default="5", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        if not is_authorized(interaction) and not is_admin(interaction):
            embed = discord.Embed(
                title="❌ Lỗi quyền hạn",
                description="Bạn không có quyền sử dụng lệnh này.",
                color=discord.Color.red()
            )
            return await interaction.response.send_message(embed=embed)

        try:
            cookie = str(self.cookie.value).strip()
            box_id = re.sub(r"[^\d]", "", str(self.box_id.value))
            delay = float(self.delay.value)

            if not box_id:
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description="ID box không hợp lệ.",
                    color=discord.Color.red()
                )
                return await interaction.response.send_message(embed=embed)

            if not os.path.exists("nhay2.txt"):
                embed = discord.Embed(
                    title="❌ Thiếu file nhay2.txt",
                    description="Không tìm thấy file nhay2.txt trong thư mục bot.",
                    color=discord.Color.red()
                )
                return await interaction.response.send_message(embed=embed)

            with open("nhay2.txt", "r", encoding="utf-8") as f:
                nicknames = [line.strip() for line in f if line.strip()]

            if not nicknames:
                embed = discord.Embed(
                    title="❌ Lỗi",
                    description="File nhay2.txt không có dòng nickname nào!",
                    color=discord.Color.red()
                )
                return await interaction.response.send_message(embed=embed)

            folder_name = f"namechange_{interaction.user.id}_{int(time.time())}"
            folder_path = os.path.join("data", folder_name)
            os.makedirs(folder_path, exist_ok=True)

            def run_namechange():
                try:
                    changer = FacebookNicknameChanger(cookie, nicknames, int(delay))
                    members = changer.get_thread_members(box_id)
                    if not members:
                        print("Không lấy được danh sách thành viên.")
                        return

                    members = [m for m in members if m['id'] != changer.user_id]

                    while os.path.exists(folder_path):
                        for i, member in enumerate(members):
                            nickname = nicknames[i % len(nicknames)]
                            changer.change_nickname(box_id, member['id'], nickname)
                            time.sleep(delay)
                except Exception as e:
                    print(f"Lỗi namechange: {e}")

            t = threading.Thread(target=run_namechange, daemon=True)
            t.start()

            if interaction.user.id not in USER_NAMECHANGE_TASKS:
                USER_NAMECHANGE_TASKS[interaction.user.id] = []
            USER_NAMECHANGE_TASKS[interaction.user.id].append({
                "folder": folder_path,
                "thread": t,
                "box_id": box_id,
                "delay": delay
            })

            embed = discord.Embed(
                title="✅ Đã bắt đầu Name Change",
                description=(
                    f"**Box ID:** `{box_id}`\n"
                    f"**Delay:** `{delay}` giây\n"
                    f"**Nickname:** Lấy từ file `nhay2.txt`\n"
                    f"**Người tạo:** {interaction.user.mention}\n\n"
                    "✅ Bot đang đổi biệt danh liên tục."
                ),
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="❌ Lỗi",
                description=str(e),
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed)

@tree.command(name="namechange", description="Đổi biệt danh Messenger liên tục từ file name.txt")
async def namechange(interaction: discord.Interaction):
    if not is_authorized(interaction) and not is_admin(interaction):
        embed = discord.Embed(
            title="❌ Lỗi quyền hạn",
            description="Bạn không có quyền sử dụng lệnh này.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    embed = discord.Embed(
        title="📝 Name Change Messenger",
        description="Nhấn **Bắt đầu** để nhập cookie, box ID và delay.",
        color=discord.Color.yellow()
    )
    view = discord.ui.View()
    button = discord.ui.Button(label="Bắt đầu", style=discord.ButtonStyle.secondary)

    async def button_callback(btn_inter: discord.Interaction):
        await btn_inter.response.send_modal(NameChangeModal())

    button.callback = button_callback
    view.add_item(button)
    await interaction.response.send_message(embed=embed, view=view)

@tree.command(name="tabnamechange", description="Quản lý và dừng task Name Change")
@app_commands.describe(stop="Nhập số task hoặc All để dừng toàn bộ")
async def tabnamechange(interaction: discord.Interaction, stop: str = None):
    if not is_authorized(interaction) and not is_admin(interaction):
        embed = discord.Embed(
            title="❌ Lỗi quyền hạn",
            description="Bạn không có quyền sử dụng lệnh này.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    user_id = interaction.user.id
    tasks = USER_NAMECHANGE_TASKS.get(user_id, [])

    if not tasks:
        embed = discord.Embed(
            title="📋 Danh sách task",
            description="❌ Bạn không có task namechange nào đang chạy.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    if stop:
        if stop.lower() == "all":
            for task in tasks:
                folder = task["folder"]
                if os.path.exists(folder):
                    os.rmdir(folder)
            USER_NAMECHANGE_TASKS[user_id] = []
            embed = discord.Embed(
                title="🛑 Dừng task",
                description="✅ Đã dừng tất cả task namechange.",
                color=discord.Color.green()
            )
            return await interaction.response.send_message(embed=embed)

        try:
            num = int(stop) - 1
            if 0 <= num < len(tasks):
                folder = tasks[num]["folder"]
                if os.path.exists(folder):
                    os.rmdir(folder)
                tasks.pop(num)
                embed = discord.Embed(
                    title="🛑 Dừng task",
                    description=f"✅ Đã dừng task số **{stop}**.",
                    color=discord.Color.green()
                )
                return await interaction.response.send_message(embed=embed)
            else:
                embed = discord.Embed(
                    title="⚠️ Lỗi",
                    description="Số task không hợp lệ.",
                    color=discord.Color.orange()
                )
                return await interaction.response.send_message(embed=embed)
        except:
            embed = discord.Embed(
                title="⚠️ Lỗi",
                description="Vui lòng nhập số hợp lệ hoặc 'all'.",
                color=discord.Color.orange()
            )
            return await interaction.response.send_message(embed=embed)

    desc = ""
    for idx, task in enumerate(tasks, 1):
        desc += f"**{idx}.** Box `{task['box_id']}` | Delay: {task['delay']}s\n"

    embed = discord.Embed(
        title="📋 Danh sách task Name Change",
        description=desc + "\n👉 Dùng `/tabnamechange stop:<số>`\n👉 Hoặc `/tabnamechange stop:all`",
        color=discord.Color.orange()
    )
    await interaction.response.send_message(embed=embed)

    
import time
import shutil
import threading
from module.treopoll import start_treo_poll_func, stop_treo_poll

USER_COMBO_TASKS = {}
STOP_FLAGS = {}
THEME_CLIENTS = {}

def run_theme(cookie, box_id, delay, task_key):
    print(f"[✅] Đã set nền mess")
    try:
        client = MQTTThemeClient(cookie)
        THEME_CLIENTS[task_key] = client
        client.connect()
        sleep_time = max(0.5, delay)
        while not STOP_FLAGS.get(task_key, False):
            try:
                theme = client.get_random_theme()
                client.set_theme(str(box_id), theme_id=theme["id"])
                print(f"[Theme {task_key}] Đã đổi theme: {theme['name']}")
            except Exception as e:
                print(f"[Theme {task_key}] Lỗi set theme: {e}")
                time.sleep(2)
            time.sleep(sleep_time)
        try:
            client.disconnect()
        except:
            pass
        print(f">>> Theme thread stopped [{task_key}]")
    except Exception as e:
        print(f"[Theme {task_key}] Lỗi theme: {e}")

def run_poll(cookie, box_id, delay, user_id, task_key):
    folder_name = f"combopoll_{task_key}"
    folder_path = os.path.join("data", folder_name)
    print(f"[✅] Đã gửi poll mess")
    try:
        os.makedirs(folder_path, exist_ok=True)
        start_treo_poll_func(cookie, box_id, delay, folder_name)
    except Exception as e:
        print(f"[Poll {task_key}] Lỗi poll: {e}")
    finally:
        try:
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)
                print(f"[Poll {task_key}] Dọn xong folder {folder_path}")
        except Exception as e:
            print(f"[Poll {task_key}] Lỗi dọn folder: {e}")
    print(f">>> Poll thread stopped [{task_key}]")

def run_namebox(cookie, box_id, delay, task_key):
    print(f"[✅] Đã đổi name box")
    try:
        dataFB = dataGetHome(cookie)
        if not dataFB:
            print(f"[NameBox {task_key}] ❌ Lỗi: dataGetHome trả về None, dừng NameBox.")
            return
        nhay_file = "nhay.txt"
        if not os.path.exists(nhay_file):
            with open(nhay_file, "w", encoding="utf-8") as f:
                f.write("TestName\n")
            print(f"[NameBox {task_key}] ⚠️ Không tìm thấy nhay.txt, đã tạo file mặc định.")
        sleep_time = max(0.5, delay)
        while not STOP_FLAGS.get(task_key, False):
            try:
                with open(nhay_file, "r", encoding="utf-8") as f:
                    lines = [line.strip() for line in f if line.strip()]
            except Exception as e:
                print(f"[NameBox {task_key}] Lỗi đọc nhay.txt: {e}")
                break
            if not lines:
                print(f"[NameBox {task_key}] nhay.txt rỗng, chờ {delay}s rồi thử lại.")
                time.sleep(delay)
                continue
            for name in lines:
                if STOP_FLAGS.get(task_key, False):
                    break
                try:
                    success, log = tenbox(name, box_id, dataFB)
                    print(f"[NameBox {task_key}] {log}")
                except Exception as e:
                    print(f"[NameBox {task_key}] ❌ Lỗi tenbox với '{name}': {e}")
                time.sleep(sleep_time)
        print(f">>> NameBox thread stopped [{task_key}]")
    except Exception as e:
        print(f"[NameBox {task_key}] Lỗi namebox tổng: {e}")

def run_combo(cookie, box_id, delay, user_id, task_key):
    STOP_FLAGS[task_key] = False
    t1 = threading.Thread(target=run_theme, args=(cookie, box_id, delay, task_key), daemon=True)
    t2 = threading.Thread(target=run_poll, args=(cookie, box_id, delay, user_id, task_key), daemon=True)
    t3 = threading.Thread(target=run_namebox, args=(cookie, box_id, delay, task_key), daemon=True)
    t1.start()
    time.sleep(0.3)
    t2.start()
    time.sleep(0.3)
    t3.start()

class ComboMessModal(discord.ui.Modal, title="ComboMess"):
    cookie = discord.ui.TextInput(label="Cookie Facebook", style=discord.TextStyle.paragraph, required=True)
    box_id = discord.ui.TextInput(label="ID Box/Thread", placeholder="Nhập ID nhóm chat", required=True)
    delay = discord.ui.TextInput(label="Delay (giây)", placeholder="Ví dụ: 30", default="30", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        if not is_admin(interaction):
            embed = discord.Embed(title="❌ Lỗi quyền hạn", description="Bạn không có quyền sử dụng bot.", color=discord.Color.red())
            return await interaction.response.send_message(embed=embed)
        try:
            cookie = str(self.cookie.value).strip()
            box_id = re.sub(r"[^\d]", "", str(self.box_id.value))
            delay = float(self.delay.value)
            if not box_id:
                embed = discord.Embed(title="❌ Lỗi", description="ID box không hợp lệ.", color=discord.Color.red())
                return await interaction.response.send_message(embed=embed)
            if interaction.user.id not in USER_COMBO_TASKS:
                USER_COMBO_TASKS[interaction.user.id] = []
            task_id = len(USER_COMBO_TASKS[interaction.user.id]) + 1
            task_key = f"{interaction.user.id}_{task_id}"
            t = threading.Thread(target=run_combo, args=(cookie, box_id, delay, interaction.user.id, task_key), daemon=True)
            t.start()
            USER_COMBO_TASKS[interaction.user.id].append({"id": task_id, "task_key": task_key, "box_id": box_id, "delay": delay})
            embed = discord.Embed(
                title="🚀 ComboMess đã khởi động",
                description=(
                    f"**Box ID:** `{box_id}`\n"
                    f"**Delay:** `{delay}` giây\n"
                    f"**Task ID:** `{task_id}`\n"
                    f"**Người tạo:** {interaction.user.mention}\n\n"
                    "⚙️ Bot đang chạy 3 chức năng: Theme, Poll, NameBox."
                ),
                color=discord.Color.green()
            )
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            embed = discord.Embed(title="❌ Lỗi", description=str(e), color=discord.Color.red())
            await interaction.response.send_message(embed=embed)

@tree.command(name="combomess", description="Chạy combo Theme + Poll + NameBox cùng lúc")
async def combomess(interaction: discord.Interaction):
    if not is_admin(interaction):
        embed = discord.Embed(title="❌ Lỗi quyền hạn", description="Bạn không có quyền sử dụng bot.", color=discord.Color.red())
        return await interaction.response.send_message(embed=embed)
    embed = discord.Embed(title="💢 Combo mess", description="Ấn **Start** để điền cookie, id box và delay.", color=discord.Color.purple())
    view = View()
    button = Button(label="Start", style=discord.ButtonStyle.secondary)
    async def button_callback(btn_inter: discord.Interaction):
        await btn_inter.response.send_modal(ComboMessModal())
    button.callback = button_callback
    view.add_item(button)
    await interaction.response.send_message(embed=embed, view=view)



@tree.command(name="tabcombomess", description="Quản lý và dừng combo task")
@app_commands.describe(stop="Nhập số task để dừng (ví dụ: 1) hoặc 'all' để dừng tất cả")
async def tabcombomess(interaction: discord.Interaction, stop: str = None):
    if not is_admin(interaction):
        embed = discord.Embed(
            title="❌ Lỗi quyền hạn",
            description="Bạn không có quyền sử dụng chức năng độc quyền của admin.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    user_id = interaction.user.id
    tasks = USER_COMBO_TASKS.get(user_id, [])

    if not tasks:
        embed = discord.Embed(
            title="📋 Danh sách task",
            description="❌ Bạn không có task ComboMess nào đang chạy.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    if stop:
        if stop.lower() == "all":
            for task in list(tasks):
                STOP_FLAGS[task["task_key"]] = True
                if task["task_key"] in THEME_CLIENTS:
                    try:
                        THEME_CLIENTS[task["task_key"]].disconnect()
                    except:
                        pass
                    try:
                        del THEME_CLIENTS[task["task_key"]]
                    except:
                        pass
                folder_path = os.path.join("data", f"combopoll_{task['task_key']}")
                try:
                    if os.path.exists(folder_path):
                        shutil.rmtree(folder_path)
                        print(f"[Stop] Xóa folder poll {folder_path}")
                except Exception as e:
                    print(f"[Stop] Lỗi xóa folder {folder_path}: {e}")
            USER_COMBO_TASKS[user_id] = []
            embed = discord.Embed(
                title="🛑 Dừng task",
                description="✅ Đã dừng tất cả task ComboMess.",
                color=discord.Color.green()
            )
            return await interaction.response.send_message(embed=embed)

        try:
            num = int(stop) - 1
            if 0 <= num < len(tasks):
                task = tasks.pop(num)
                STOP_FLAGS[task["task_key"]] = True

                if task["task_key"] in THEME_CLIENTS:
                    try:
                        THEME_CLIENTS[task["task_key"]].disconnect()
                    except:
                        pass
                    try:
                        del THEME_CLIENTS[task["task_key"]]
                    except:
                        pass

                folder_path = os.path.join("data", f"combopoll_{task['task_key']}")
                try:
                    if os.path.exists(folder_path):
                        shutil.rmtree(folder_path)
                        print(f"[Stop] Xóa folder poll {folder_path}")
                except Exception as e:
                    print(f"[Stop] Lỗi xóa folder {folder_path}: {e}")

                embed = discord.Embed(
                    title="🛑 Dừng task",
                    description=f"✅ Đã dừng task số **{stop}**.",
                    color=discord.Color.green()
                )
                return await interaction.response.send_message(embed=embed)
            else:
                embed = discord.Embed(
                    title="⚠️ Lỗi",
                    description="Số task không hợp lệ.",
                    color=discord.Color.orange()
                )
                return await interaction.response.send_message(embed=embed)
        except:
            embed = discord.Embed(
                title="⚠️ Lỗi",
                description="Vui lòng nhập số hợp lệ hoặc 'all'.",
                color=discord.Color.orange()
            )
            return await interaction.response.send_message(embed=embed)

    desc = ""
    for idx, task in enumerate(tasks, 1):
        desc += f"**{idx}.** Box `{task['box_id']}` | Delay: {task['delay']}s | Key: `{task['task_key']}`\n"

    embed = discord.Embed(
        title="📋 Danh sách task ComboMess",
        description=desc + "\n👉 Dùng `/tabcombomess stop:<số>` để dừng task.\n👉 Dùng `/tabcombomess stop:all` để dừng tất cả.",
        color=discord.Color.orange()
    )
    await interaction.response.send_message(embed=embed)


@tree.command(
    name="checkuid",
    description="Xem thông tin chi tiết của một user qua UID Discord (Admin hoặc Admin phụ)"
)
@app_commands.describe(uid="Nhập UID Discord của người cần tra")
async def checkuid(interaction: discord.Interaction, uid: str):
    if not is_authorized(interaction) and not is_admin(interaction):
        embed = discord.Embed(
            title="❌ Lỗi quyền hạn",
            description="Bạn không có quyền dùng lệnh này.",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        return await interaction.response.send_message(embed=embed)

    try:
        user_id = int(uid)
        user = await bot.fetch_user(user_id)
    except Exception:
        embed = discord.Embed(
            title="❌ Không tìm thấy user",
            description=f"Không tìm thấy user với UID `{uid}`.",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        return await interaction.response.send_message(embed=embed)

 
    embed = discord.Embed(
        title="🔍 Thông tin người dùng được tra cứu",
        color=discord.Color.green(),
        timestamp=datetime.now()
    )

    embed.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
    embed.add_field(name="👤 User", value=f"<@{user.id}>", inline=True)
    embed.add_field(name="🆔 UID", value=f"`{user.id}`", inline=True)
    embed.add_field(name="💬 Username", value=f"`{user.name}`", inline=True)

    if user.global_name:
        embed.add_field(name="🌍 Global Name", value=f"`{user.global_name}`", inline=True)

    if hasattr(user, "pronouns") and user.pronouns:
        embed.add_field(name="🙋 Pronouns", value=f"`{user.pronouns}`", inline=True)

    embed.add_field(
        name="📅 Ngày tạo tài khoản",
        value=f"`{user.created_at.strftime('%d/%m/%Y %H:%M:%S')}`",
        inline=False
    )

    await interaction.response.send_message(embed=embed)




@tree.command(name="idkenh", description="Lấy ID kênh hiện tại")
async def idkenh(interaction: discord.Interaction):
    if not is_authorized(interaction) and not is_admin(interaction):
        embed = discord.Embed(
            title="❌ Lỗi quyền hạn",
            description="Bạn không có quyền sử dụng lệnh này.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    channel = interaction.channel
    if channel is None:
        embed = discord.Embed(
            title="❌ Lỗi",
            description="Không thể lấy kênh hiện tại.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    channel_id = channel.id

   
    if isinstance(channel, discord.DMChannel):
        channel_display = f"Tin nhắn trực tiếp với {channel.recipient}"
        guild_name = "Không thuộc server (DM)"
    else:
        channel_display = channel.mention
        guild_name = interaction.guild.name if interaction.guild else "Không rõ server"

    
    main_embed = discord.Embed(
        title="📋 Channel Info",
        description=f"Thông tin kênh trong **{guild_name}**",
        color=0x5865F2
    )
    main_embed.add_field(name="Tên kênh", value=channel_display, inline=False)
    main_embed.set_footer(text="Bấm nút bên dưới để hiện ID kênh")


    class CopyView(discord.ui.View):
        def __init__(self, cid: int):
            super().__init__(timeout=None)
            self.cid = cid

        @discord.ui.button(label="📋  Channel ID", style=discord.ButtonStyle.primary, emoji="🔑")
        async def copy_btn(self, interaction_btn: discord.Interaction, button: discord.ui.Button):
            copy_embed = discord.Embed(
                title="📋 Channel ID",
                description=f"```{self.cid}```",
                color=0x57F287
            )
            copy_embed.set_footer(text="lấy id kênh")
            await interaction_btn.response.send_message(embed=copy_embed)

    view = CopyView(channel_id)

    await interaction.response.send_message(embed=main_embed, view=view)



class Say1Modal(discord.ui.Modal, title="💬 Nhập nội dung để bot nói lại"):
    message = discord.ui.TextInput(
        label="Nội dung cần bot nói",
        style=discord.TextStyle.paragraph,
        placeholder="Ví dụ: Xin chào mọi người 👋",
        required=True,
        max_length=2000,
    )

    def __init__(self, author: discord.Member | discord.User):
        super().__init__()
        self.author = author

    async def on_submit(self, interaction: discord.Interaction):
        if not is_admin(interaction):
            embed = discord.Embed(
                title="🚫 Không có quyền",
                description="Bạn không có quyền sử dụng lệnh này.",
                color=discord.Color.red(),
            )
            return await interaction.response.send_message(embed=embed)

        content = self.message.value
        allowed = discord.AllowedMentions(everyone=False, roles=False, users=True)

        embed = discord.Embed(description=content, color=discord.Color.blurple())
        embed.set_footer(
            text="Minh Quân 𝙱𝚘𝚝",
            icon_url=getattr(self.author, "display_avatar", None)
        )
        await interaction.response.send_message(embed=embed, allowed_mentions=allowed)


@tree.command(name="say1", description="Nhại lại lời admin nói bằng embed")
async def say1_command(interaction: discord.Interaction):
    if not is_admin(interaction):
        embed = discord.Embed(
            title="🚫 Không có quyền",
            description="Bạn không có quyền sử dụng lệnh này.",
            color=discord.Color.red(),
        )
        return await interaction.response.send_message(embed=embed)

    modal = Say1Modal(author=interaction.user)
    await interaction.response.send_modal(modal)


class Say2Modal(discord.ui.Modal, title="💬 Nhập nội dung để bot nói lại (Text thường)"):
    message = discord.ui.TextInput(
        label="Nội dung",
        style=discord.TextStyle.paragraph,
        placeholder="Ví dụ: Hello",
        required=True,
        max_length=2000,
    )

    def __init__(self, author: discord.Member | discord.User):
        super().__init__()
        self.author = author

    async def on_submit(self, interaction: discord.Interaction):
        if not is_admin(interaction):
            return await interaction.response.send_message(
                "🚫 Bạn không có quyền sử dụng lệnh này.", ephemeral=True
            )

        await interaction.response.send_message(self.message.value)


import asyncio

@tree.command(name="say2", description="Nhại lại lời admin bằng tin nhắn thường")
@app_commands.describe(message="Nội dung bot sẽ nói")
async def say2_command(interaction: discord.Interaction, message: str):
    if not is_admin(interaction):
        embed = discord.Embed(
            title="🚫 Không có quyền",
            description="Bạn không có quyền sử dụng lệnh này.",
            color=discord.Color.red(),
        )
        return await interaction.response.send_message(embed=embed)

    await interaction.response.defer(ephemeral=True)

    channel = interaction.channel
    allowed = discord.AllowedMentions(everyone=False, roles=False, users=True)
    await channel.send(content=message, allowed_mentions=allowed)

    try:
        await interaction.delete_original_response()
    except:
        pass


from discord import ButtonStyle
from module.audio import send_blank_audio

AUDIO_LOCK = asyncio.Lock()
user_audio_sessions = {}


def format_time(seconds: int) -> str:
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    parts = []
    if d: parts.append(f"{d}d")
    if h: parts.append(f"{h}h")
    if m: parts.append(f"{m}m")
    parts.append(f"{s}s")
    return " ".join(parts)

async def audio_worker(token, channel_id, delay, color_prefix):
    i = 0
    async with SEMAPHORE:
        while True:
            try:
                await GLOBAL_LIMITER.acquire()
                await send_blank_audio(token, channel_id)
            except Exception as e:
                print(f"{color_prefix}[⚠️] Lỗi gửi audio: {e}")
            i += 1
            await cooperative_sleep(i)
            await asyncio.sleep(delay)

class AudioButtonView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Start", style=ButtonStyle.secondary, custom_id="open_audio_modal")
    async def open_modal(self, interaction: discord.Interaction, button: Button):
        if not is_authorized(interaction) and not is_admin(interaction):
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Lỗi Quyền hạn",
                    description="Bạn không có quyền sử dụng bot.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
            return
        modal = AudioModal()
        await interaction.response.send_modal(modal)

class AudioModal(Modal, title="Spam Audio Discord"):
    token = TextInput(label="Token", style=discord.TextStyle.paragraph)
    channel_id = TextInput(label="Channel ID")
    delay = TextInput(label="Delay (giây)", required=False)

    async def on_submit(self, interaction: discord.Interaction):
        if not is_authorized(interaction) and not is_admin(interaction):
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="❌ Quyền hạn",
                    description="Bạn không có quyền sử dụng bot.",
                    color=discord.Color.red()
                ),
                ephemeral=True
            )
            return

        token_list = [t.strip() for t in self.token.value.split(",") if t.strip()]
        channel_ids = [c.strip() for c in self.channel_id.value.split(",") if c.strip()]

        try:
            delay = float(self.delay.value.strip()) if self.delay.value else 3.0
        except:
            delay = 3.0

        user_id = str(interaction.user.id)
        start_time = datetime.now()
        tasks = []

        for token in token_list:
            for cid in channel_ids:
                t = asyncio.create_task(audio_worker(token, cid, delay, f"[{user_id}] "))
                tasks.append(t)

        async with AUDIO_LOCK:
            if user_id not in user_audio_sessions:
                user_audio_sessions[user_id] = []
            user_audio_sessions[user_id].append({
                "session_count": len(token_list),
                "channels": channel_ids,
                "delay": delay,
                "start": start_time,
                "tasks": tasks
            })

        embed = discord.Embed(
            title="✅ Đã khởi chạy spam Audio",
            description=(f"Số worker: `{len(tasks)}`\n"
                         f"Channel(s): `{', '.join(channel_ids)}`\n"
                         f"Delay: `{delay}s`\n"
                         f"Bắt đầu lúc: `{start_time.strftime('%Y-%m-%d %H:%M:%S')}`"),
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

@tree.command(name="treoaudio", description="Khởi chạy spam audio Discord")
async def treoaudio_cmd(interaction: discord.Interaction):
    if not is_authorized(interaction) and not is_admin(interaction):
        await interaction.response.send_message(
            embed=discord.Embed(
                title="❌ Lỗi Quyền hạn",
                description="Bạn không có quyền sử dụng lệnh này.",
                color=discord.Color.red()
            ),
        )
        return

    embed = discord.Embed(
        title="🎧 Spam Audio Discord",
        description="Nhấn nút bên dưới để nhập thông tin gửi audio.",
        color=discord.Color.dark_gray()
    )
    view = AudioButtonView()
    await interaction.response.send_message(embed=embed, view=view)

@tree.command(name="tabtreoaudio", description="Quản lý / dừng các session spam audio")
async def tabtreoaudio(interaction: discord.Interaction):
    if not is_authorized(interaction) and not is_admin(interaction):
        await interaction.response.send_message(
            embed=discord.Embed(
                title="❌ Lỗi Quyền hạn",
                description="Bạn không có quyền sử dụng lệnh này.",
                color=discord.Color.red()
            ),
            ephemeral=True
        )
        return

    user_id = str(interaction.user.id)
    async with AUDIO_LOCK:
        sessions = user_audio_sessions.get(user_id, [])

    if not sessions:
        embed = discord.Embed(
            title="❌ Không có session nào đang chạy",
            description="Bạn chưa có tab audio nào hoạt động.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
        return

    embed = discord.Embed(title="📋 Danh sách tab Audio đang chạy", color=discord.Color.gold())
    for i, s in enumerate(sessions, start=1):
        uptime = format_time(int((datetime.now() - s["start"]).total_seconds()))
        embed.add_field(
            name=f"Session {i}",
            value=(f"- Tokens: `{s['session_count']}`\n"
                   f"- Channels: `{', '.join(s['channels'])}`\n"
                   f"- Delay: `{s['delay']}s`\n"
                   f"- Uptime: `{uptime}`"),
            inline=False
        )
    embed.set_footer(text="Nhập số thứ tự tab muốn dừng (trong 30s).")
    await interaction.response.send_message(embed=embed)

    def check(m: discord.Message):
        return m.author.id == interaction.user.id and m.channel.id == interaction.channel.id

    try:
        reply = await bot.wait_for("message", check=check, timeout=30.0)
    except asyncio.TimeoutError:
        timeout_embed = discord.Embed(
            title="⏰ Hết thời gian",
            description="Không dừng tab nào.",
            color=discord.Color.orange()
        )
        await interaction.followup.send(embed=timeout_embed)
        return

    choice = reply.content.strip()
    if not choice.isdigit():
        await interaction.followup.send(embed=discord.Embed(
            title="❌ Lỗi",
            description="Giá trị nhập không hợp lệ.",
            color=discord.Color.red()
        ))
        return

    idx = int(choice)
    if not (1 <= idx <= len(sessions)):
        await interaction.followup.send(embed=discord.Embed(
            title="❌ Lỗi",
            description="Số tab không hợp lệ.",
            color=discord.Color.red()
        ))
        return

    async with AUDIO_LOCK:
        target = sessions.pop(idx - 1)
        for t in target["tasks"]:
            t.cancel()
        if not sessions:
            user_audio_sessions.pop(user_id, None)

    done_embed = discord.Embed(
        title="✅ Dừng tab thành công",
        description=f"Tab số `{idx}` đã bị dừng.",
        color=discord.Color.green()
    )
    await interaction.followup.send(embed=done_embed)


    
import psutil
import platform
import time

bot_start_time = time.time()

@tree.command(name="ping", description="Xem tình trạng hệ thống Bot Thế Giới Ảo ⚙️")
async def ping_cmd(interaction: discord.Interaction):
    """Lệnh /ping hiển thị CPU, RAM, ping và uptime của bot"""
    await interaction.response.defer(thinking=True)

    try:
        
        process = psutil.Process(os.getpid())
        with process.oneshot():  
            cpu_usage = process.cpu_percent(interval=0.3)
            mem_usage = process.memory_info().rss / 1024 / 1024 
            threads = process.num_threads()

        uptime_seconds = int(time.time() - bot_start_time)
        uptime_str = time.strftime("%Hh %Mm %Ss", time.gmtime(uptime_seconds))

        latency = round(interaction.client.latency * 1000, 1)

        embed = discord.Embed(
            title="📡 Thế Giới Ảo System Monitor",
            description="Thông tin hiệu suất của bot Thế Giới Ảo",
            color=discord.Color.blurple()
        )

        embed.add_field(name="**CPU**", value=f"{cpu_usage:.2f}%", inline=True)
        embed.add_field(name="**RAM**", value=f"{mem_usage:.1f} MB", inline=True)
        embed.add_field(name="Threads", value=str(threads), inline=True)

        embed.add_field(name="**Ping**", value=f"{latency} ms", inline=True)
        embed.add_field(name="**⏱Uptime**", value=uptime_str, inline=True)
        embed.add_field(name="**System**", value=platform.system(), inline=True)

        embed.add_field(name="**Python**", value=platform.python_version(), inline=True)
        embed.add_field(name="**Platform**", value=platform.release(), inline=True)

        embed.set_footer(
            text=f"Thế Giới Ảo System Monitor • Cập nhật: {time.strftime('%H:%M:%S')}",
            icon_url="https://cdn-icons-png.flaticon.com/512/4712/4712035.png"
        )

        await interaction.followup.send(embed=embed)

    except Exception as e:
        await interaction.followup.send(
            embed=discord.Embed(
                title="⚠️ Lỗi khi đọc dữ liệu hệ thống",
                description=f"Chi tiết: `{e}`",
                color=discord.Color.red()
            )
        )



from discord.ext import commands

intents = discord.Intents.default()
intents.presences = True
intents.members = True

class StatusView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.auto_task = None

    @discord.ui.button(label="Chờ 💤", style=discord.ButtonStyle.secondary)
    async def idle_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await bot.change_presence(status=discord.Status.idle)
        await interaction.response.send_message("✅ Bot đã chuyển sang chế độ **Chờ**", ephemeral=True)

    @discord.ui.button(label="Bận 🚫", style=discord.ButtonStyle.danger)
    async def dnd_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await bot.change_presence(status=discord.Status.dnd)
        await interaction.response.send_message("✅ Bot đã chuyển sang chế độ **Bận**", ephemeral=True)

    @discord.ui.button(label="Online 🟢", style=discord.ButtonStyle.success)
    async def online_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await bot.change_presence(status=discord.Status.online)
        await interaction.response.send_message("✅ Bot đã chuyển sang chế độ **Online**", ephemeral=True)

    @discord.ui.button(label="Auto Set 🔁", style=discord.ButtonStyle.primary)
    async def auto_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.auto_task and not self.auto_task.done():
            self.auto_task.cancel()
            self.auto_task = None
            await interaction.response.send_message("🛑 Đã **tắt chế độ tự động** thay đổi trạng thái.", ephemeral=True)
            return

        await interaction.response.send_message("🔁 Đã bật **chế độ tự động** thay đổi trạng thái.", ephemeral=True)
        self.auto_task = asyncio.create_task(self.auto_status_loop())

    async def auto_status_loop(self):
        statuses = [discord.Status.online, discord.Status.dnd, discord.Status.idle]
        while True:
            for s in statuses:
                await bot.change_presence(status=s)
                await asyncio.sleep(2)

@tree.command(name="setstatus", description="⚙️ Thay đổi trạng thái hoạt động của bot (chỉ Admin, dùng trong DM)")
async def setstatus(interaction: discord.Interaction):
    if not isinstance(interaction.channel, discord.DMChannel):
        embed = discord.Embed(
            title="🚫 Không hợp lệ",
            description="Lệnh này chỉ sử dụng được trong DM riêng với bot.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    if interaction.user.id != admin_id:
        embed = discord.Embed(
            title="🚫 Không có quyền",
            description="Chỉ Admin mới được phép sử dụng lệnh này.",
            color=discord.Color.red()
        )
        return await interaction.response.send_message(embed=embed)

    embed = discord.Embed(
        title="⚙️ Tùy chỉnh trạng thái Bot",
        description="Chọn một nút bên dưới để thay đổi trạng thái hoạt động của bot:",
        color=discord.Color.blurple()
    )
    embed.set_footer(text="Bot điều khiển trạng thái real-time")

    view = StatusView()
    await interaction.response.send_message(embed=embed, view=view)

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot đã online với tên: {bot.user}")
    print("Slash command đã được sync thành công!")



admin_id = 1452664189628973202

bot.run(TOKEN)

COLORS = {'vang': ''}