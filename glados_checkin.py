import os
import random
import time
import requests
import datetime
from typing import Tuple, Optional

class GLaDOSChecker:
    API_BASE = "https://glados.cloud/api/user"
    CHECKIN_URL = f"{API_BASE}/checkin"
    STATUS_URL = f"{API_BASE}/status"
    
    def __init__(self):
        self._validate_env()
        self.email = os.environ["GLADOS_EMAIL"]
        self.cookie = os.environ["GLADOS_COOKIE"]
        self.bot_token = os.environ["TG_BOT_TOKEN"]
        self.chat_id = os.environ["TG_CHAT_ID"]
        
    def _validate_env(self):
        required = {"GLADOS_EMAIL", "GLADOS_COOKIE", "TG_BOT_TOKEN", "TG_CHAT_ID"}
        missing = required - set(os.environ)
        if missing:
            raise ValueError(f"Missing environment variables: {', '.join(missing)}")

    @staticmethod
    def _current_time() -> str:
        return (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M")

    def _gen_headers(self) -> dict:
        return {
            "Accept": "application/json",
            "Cookie": self.cookie,
            "User-Agent": os.environ.get(
                "GLADOS_USER_AGENT",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
            ),
            "Content-Type": "application/json;charset=UTF-8",
            "Origin": "https://glados.cloud"
        }

    def _parse_response(self, response: requests.Response) -> dict:
        try:
            return response.json()
        except ValueError:
            return {"message": f"Invalid JSON: {response.text[:50]}"}

    def check_status(self) -> Tuple[bool, str]:
        try:
            resp = requests.get(
                self.STATUS_URL,
                headers=self._gen_headers(),
                timeout=15
            )
            resp.raise_for_status()
            data = self._parse_response(resp)
            if data.get("code") == -2 or not isinstance(data.get("data"), dict):
                return False, f"状态查询失败: {data.get('message', '无效响应')} ❌"
            days = float(data["data"].get("leftDays", 0))
            return True, f"剩余天数: {days:.1f} 🗓️"
        except Exception as e:
            return False, f"状态查询失败: {str(e)} ❌"

    def perform_checkin(self) -> Tuple[bool, str]:
        try:
            resp = requests.post(
                self.CHECKIN_URL,
                headers=self._gen_headers(),
                json={"token": "glados.cloud"},
                timeout=15
            )
            resp.raise_for_status()
            data = self._parse_response(resp)
            return self._handle_checkin_result(data)
        except Exception as e:
            return False, f"签到失败: {str(e)} ❌"

    def _handle_checkin_result(self, data: dict) -> Tuple[bool, str]:
        msg = str(data.get("message", ""))
        normalized = msg.casefold()

        if data.get("code") == -2 or "没有权限" in msg or "permission" in normalized:
            return False, f"认证失败: {msg or 'Cookie 无效或已过期'} ❌"
        if "please try tomorrow" in normalized or "checkin repeats" in normalized:
            return True, "今日已签到 ⏳"
        if "observation logged" in normalized:
            return True, "今日签到记录已更新 ✅"

        match = re.search(r"\bGot\s+([\d.]+)", msg, re.IGNORECASE)
        if match:
            return True, f"获得 {match.group(1)} 积分 🎉"
        if data.get("code") == 0:
            return True, f"{msg or '签到成功'} ✅"
        return False, f"未知响应: {msg or data} ❓"

    def send_notification(self, status: str, checkin_result: str):
        message = (
            f"🕒 北京时间: {self._current_time()}\n"
            f"📧 账户: {self.email}\n\n"
            f"🔔 签到结果: {checkin_result}\n"
            f"📊 账户状态: {status}\n\n"
            "📌 自动签到任务结束"
        )
        
        try:
            resp = requests.post(
                f"https://api.telegram.org/bot{self.bot_token}/sendMessage",
                json={
                    "chat_id": self.chat_id,
                    "text": message,
                    "parse_mode": "Markdown"
                },
                timeout=10
            )
            resp.raise_for_status()
        except Exception as e:
            print(f"⚠️ 通知发送失败: {str(e)}")

    def execute(self):
        print(f"🔍 开始处理账户: {self.email}")
        time.sleep(random.uniform(1, 3))
        
        success, checkin_result = self.perform_checkin()
        status_success, status_result = self.check_status()

        self.send_notification(status_result, checkin_result)
        if not success or not status_success:
            print("❌ 签到或状态查询失败")
            raise SystemExit(1)
        print("🏁 流程执行完毕")

if __name__ == "__main__":
    checker = GLaDOSChecker()
    checker.execute()
