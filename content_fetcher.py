'''
Author: Wang Zikang zikangwang@sohu-inc.com
Date: 2026-01-19 17:18:08
LastEditors: Wang Zikang zikangwang@sohu-inc.com
LastEditTime: 2026-01-19 17:19:49
FilePath: /news_push/content_fetcher.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
import logging
import requests
from typing import Optional
from bs4 import BeautifulSoup
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class ContentFetcher:
    """网页内容抓取器"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.headers = {
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    def fetch(self, url: str) -> Optional[str]:
        """抓取网页正文"""
        try:
            response = requests.get(url,
                                    headers=self.headers,
                                    timeout=self.timeout)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            for tag in soup(['script', 'style', 'nav', 'footer', 'aside']):
                tag.decompose()

            article = soup.find('article') or soup.find('main') or soup.find(
                'body')

            if not article:
                return None

            paragraphs = article.find_all(['p', 'h1', 'h2', 'h3'])
            content = ' '.join([p.get_text().strip() for p in paragraphs])

            content = ' '.join(content.split())

            if len(content) < 100:
                return None

            return content[:2000]

        except Exception as e:
            logger.debug(f"抓取失败 {url}: {e}")
            return None
