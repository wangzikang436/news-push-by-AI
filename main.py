import logging
import sys
from datetime import datetime
from typing import List, Dict

from config import Config
from tavily_searcher import TavilySearcher
from ai_processor import AIProcessor
from email_pusher import EmailPusher

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'news_{datetime.now():%Y%m%d}.log'),
        logging.StreamHandler(sys.stdout)
    ])

logger = logging.getLogger(__name__)


class NewsAggregator:
    """新闻聚合器"""

    def __init__(self):
        self.searcher = TavilySearcher()
        self.ai_processor = AIProcessor()
        self.email_pusher = EmailPusher()

    def collect_news(self) -> List[Dict]:
        """收集新闻"""
        logger.info("开始使用 Tavily 搜索新闻")

        all_news = self.searcher.search_all_categories()
        logger.info(f"共收集到 {len(all_news)} 条新闻")

        return all_news

    def process_and_send(self, news_items: List[Dict]):
        """AI 处理并推送"""
        if not news_items:
            logger.warning("没有新新闻需要发送")
            return

        logger.info("使用 OpenAI 分析新闻")
        summary = self.ai_processor.analyze_and_summarize(news_items)

        subject = f"今日全球新闻速览 ({datetime.now():%Y-%m-%d})"
        logger.info("发送邮件")

        success = self.email_pusher.send(summary, subject)

        if success:
            logger.info("新闻推送成功")
        else:
            logger.error("新闻推送失败")

    def run(self):
        """执行完整流程"""
        logger.info("=" * 80)
        logger.info("新闻聚合任务启动")
        logger.info("=" * 80)

        try:
            news_items = self.collect_news()
            self.process_and_send(news_items)

        except Exception as e:
            logger.error(f"任务执行失败: {e}", exc_info=True)

        logger.info("=" * 80)
        logger.info("任务完成")
        logger.info("=" * 80)


if __name__ == "__main__":
    aggregator = NewsAggregator()
    aggregator.run()
