from dataclasses import dataclass
from typing import Dict, List
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()


@dataclass
class TavilyConfig:
    api_key: str = os.getenv('TAVILY_API_KEY', '')
    search_depth: str = 'advanced'  # 改为 advanced 获取更多内容
    max_results: int = 5  # 每个查询 5 条结果
    days: int = 1  # 最近 1 天


@dataclass
class OpenAIConfig:
    api_key: str = os.getenv('OPENAI_API_KEY', '')
    base_url: str = os.getenv('OPENAI_BASE_URL', '').strip()
    model: str = os.getenv('OPENAI_MODEL', 'gemini-3-pro-all').strip()
    max_tokens: int = 15000
    temperature: float = 0.2


@dataclass
class EmailConfig:
    sender: str = os.getenv('EMAIL_SENDER', '').strip()
    password: str = os.getenv('EMAIL_PASSWORD', '').strip()
    receiver: str = os.getenv('EMAIL_RECEIVER', '').strip()
    smtp_server: str = os.getenv('EMAIL_SMTP_SERVER', 'smtp.126.com').strip()
    smtp_port: int = int(os.getenv('EMAIL_SMTP_PORT', '465'))


class Config:
    TAVILY = TavilyConfig()
    OPENAI = OpenAIConfig()
    EMAIL = EmailConfig()
    SCHEDULE_TIME = '08:00'

    # 优化后的搜索关键词（更具体的查询）
    @staticmethod
    def get_search_queries() -> dict:
        """动态生成搜索关键词"""
        today = datetime.now().strftime('%B %d %Y')

        return {
            '科技': [
                f'AI breakthrough {today}', f'technology innovation {today}',
                'latest tech news today'
            ],
            '军事': [
                f'military conflict {today}', f'defense news {today}',
                'latest military updates today'
            ],
            '政治': [
                f'world politics {today}', f'government policy {today}',
                'latest political news today'
            ],
            '足球': [
                f'Premier League match result {today}',
                f'Champions League news {today}',
                'football transfer rumor today'
            ],
            '篮球': [
                f'NBA game result {today}', f'basketball highlights {today}',
                'NBA trade news today'
            ]
        }
