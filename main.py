import asyncio
import aiohttp
from typing import Dict
import requests

BOT_API_KEY="7650654842:AAGrOcw8gzQEJYU3xAndobck7woDkcxQbV4"
ADMINS = [
    6301828522,
    1435333610,
    7532221096,
    776071518
]


def send_telegram_message(message:str, account:str):
    url = f"https://api.telegram.org/bot{BOT_API_KEY}/sendMessage"

    for admin in ADMINS:
        if account:
            name_str = f" | <code>{account}</code>"
        else:
            name_str = ""
        payload = {
            "chat_id": admin,
            "text": f"<b>{message}</b>{name_str}",
            "parse_mode": "HTML"
        }
        try:
            requests.post(url, json=payload)
        except Exception as e:
            pass


class AsyncTokenBalanceMonitor:
    def __init__(self, accounts: Dict[str, str], check_interval: int = 300):
        self.accounts = accounts
        self.check_interval = check_interval
        self.base_url = "https://chaturbate.com/statsapi/"

    async def get_token_balance(self, session: aiohttp.ClientSession, username: str, token: str) -> dict:
        try:
            async with session.get(self.base_url, params={
                "username": username,
                "token": token
            }, timeout=10) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            send_telegram_message("❌ Проблема с получением данных", username)
            return None

    async def check_account_balance(self, session: aiohttp.ClientSession, username: str, token: str):
        data = await self.get_token_balance(session, username, token)
                
        if data is None:
            send_telegram_message("❌ Проблема с получением данных", username)
            return
                
        token_balance = data.get('token_balance', -1)
                
        if token_balance == 0:
            send_telegram_message("🔔 Аренда закончилась!", username)

    async def monitor_balances(self):
        async with aiohttp.ClientSession() as session:
            while True:
                tasks = [
                    self.check_account_balance(session, username, token) 
                    for username, token in self.accounts.items()
                ]
                
                await asyncio.gather(*tasks)
                
                await asyncio.sleep(self.check_interval)


async def main():
    ACCOUNTS = {
        'wavewithme': 'iG8H3W07G7NaiqoqI0tajeUn',
    }

    monitor = AsyncTokenBalanceMonitor(ACCOUNTS)
    
    try:
        await monitor.monitor_balances()
    except KeyboardInterrupt:
        print("\nМониторинг остановлен пользователем.")

if __name__ == "__main__":
    asyncio.run(main())