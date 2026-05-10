import requests
import random
import re
import time
import json
from typing import List, Dict, Optional

class FacebookNicknameChanger:
    def __init__(self, cookie: str, nicknames: List[str], delay: int):
        self.cookie = cookie
        self.nicknames = nicknames
        self.delay = delay
        self.fb_dtsg = ''
        self.jazoest = ''
        self.session = requests.Session()
        self.user_id = self.cookie.split('c_user=')[1].split(';')[0]
        
        self.headers = {
            'authority': 'www.facebook.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'accept-language': 'vi',
            'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'none',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
            'Cookie': self.cookie
        }
        self._initialize_tokens()

    def _initialize_tokens(self):
        """Khởi tạo fb_dtsg và jazoest tokens"""
        try:
            url = self.session.get(f'https://www.facebook.com/{self.user_id}', headers=self.headers).url
            response = self.session.get(url, headers=self.headers).text
            
            # Lấy fb_dtsg và jazoest
            fb_dtsg_match = re.findall(r'\["DTSGInitialData",\[\],\{"token":"(.*?)"\}', response)
            if fb_dtsg_match:
                self.fb_dtsg = fb_dtsg_match[0]
            
            jazoest_match = re.findall(r'jazoest=(.*?)\"', response)
            if jazoest_match:
                self.jazoest = jazoest_match[0]

            if not self.fb_dtsg or not self.jazoest:
                raise Exception("Không thể lấy fb_dtsg hoặc jazoest")
                

        except Exception as e:
            raise e

    def get_thread_members(self, thread_id: str) -> List[Dict]:
        """Lấy danh sách thành viên trong nhóm"""
        try:
            form = {
                "o0": {
                    "doc_id": "3449967031715030",
                    "query_params": {
                        "id": thread_id,
                        "message_limit": 0,
                        "load_messages": False,
                        "load_read_receipts": False,
                        "before": None
                    }
                }
            }
            
            submit_data = {
                "queries": json.dumps(form),
                "batch_name": "MessengerGraphQLThreadFetcher",
                "fb_dtsg": self.fb_dtsg,
                "jazoest": self.jazoest
            }
            
            post_headers = self.headers.copy()
            post_headers.update({
                'content-type': 'application/x-www-form-urlencoded',
                'origin': 'https://www.facebook.com',
                'referer': 'https://www.facebook.com/',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'same-origin',
            })
            
            
            response = self.session.post(
                "https://www.facebook.com/api/graphqlbatch/",
                data=submit_data,
                headers=post_headers,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"HTTP Error: {response.status_code}")
            
            # Parse response
            response_text = response.text
            lines = response_text.strip().split('\n')
            if lines and lines[-1].startswith('{"batch_name"'):
                lines = lines[:-1]
            
            for line in lines:
                if line.strip():
                    try:
                        data = json.loads(line)
                        
                        for key in data:
                            if key.startswith('o') and key in data and 'data' in data[key]:
                                thread_data = data[key]['data']
                                message_thread = thread_data.get('message_thread')
                                
                                if not message_thread:
                                    continue
                                
                                all_participants = message_thread.get('all_participants', {})
                                participants = all_participants.get('edges', [])
                                
                                members = []
                                for participant in participants:
                                    if not participant:
                                        continue
                                    
                                    node = participant.get('node', {})
                                    actor = node.get('messaging_actor', {})
                                    
                                    if actor and actor.get('id'):
                                        member_data = {
                                            'id': actor.get('id'),
                                            'name': actor.get('name', 'Unknown'),
                                            'firstName': actor.get('short_name', ''),
                                            'vanity': actor.get('username', ''),
                                            'isFriend': bool(actor.get('is_viewer_friend', False))
                                        }
                                        members.append(member_data)
                                
                                return members
                    except json.JSONDecodeError:
                        continue
            
            return []
            
        except Exception as e:
            return []

    def get_nicknames(self) -> List[str]:
        """Lấy danh sách biệt danh đã nhập"""
        return self.nicknames

    def change_nickname(self, thread_id: str, user_id: str, new_nickname: str) -> bool:
        """Thay đổi biệt danh cho một user"""
        try:
            data = {
                'nickname': new_nickname,
                'participant_id': user_id,
                'thread_or_other_fbid': thread_id,
                'fb_dtsg': self.fb_dtsg,
                'jazoest': self.jazoest,
            }

            url = f'https://www.facebook.com/messaging/save_thread_nickname/?source=thread_settings&dpr=1'
            response = self.session.post(url, data=data, headers=self.headers)

            if response.status_code == 200:
                return True
            else:
                return False
        
        except Exception as e:
            print(f"❌ Lỗi khi thay đổi biệt danh cho {user_id}: {e}")
            return False

    def change_nicknames_for_all_members(self, thread_id: str, exclude_self: bool = True):
        """Thay đổi biệt danh cho tất cả thành viên trong nhóm (1 lần cho mỗi người)"""
        # Lấy danh sách thành viên
        members = self.get_thread_members(thread_id)
        if not members:
            return
        
        # Loại bỏ bản thân khỏi danh sách nếu cần
        if exclude_self:
            members = [member for member in members if member['id'] != self.user_id]
        
        # Lấy danh sách biệt danh
        nicknames = self.get_nicknames()
        if not nicknames:
            return
        

        
        success_count = 0
        total_members = len(members)
        
        for i, member in enumerate(members, 1):
            # Lấy biệt danh ngẫu nhiên hoặc theo thứ tự
            current_nickname = nicknames[(i-1) % len(nicknames)]
            
            member_name = member.get('name', 'Unknown')
            member_id = member.get('id')
            
            
            # Thay đổi biệt danh
            if self.change_nickname(thread_id, member_id, current_nickname):
                success_count += 1
            
            # Delay trước khi thay đổi tiếp (trừ lần cuối)
            if i < total_members and self.delay > 0:
                time.sleep(self.delay)
            
            print("-" * 40)
        

    def display_members(self, thread_id: str):
        """Hiển thị danh sách thành viên trong nhóm"""
        members = self.get_thread_members(thread_id)
        if not members:
            return
        
        
        for i, member in enumerate(members, 1):
            name = member.get('name', 'Unknown')
            member_id = member.get('id', '')
            is_friend = "✅" if member.get('isFriend') else "❌"
            is_self = "👤 (Bạn)" if member_id == self.user_id else ""
            
        

