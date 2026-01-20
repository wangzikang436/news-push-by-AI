import logging
from typing import List, Dict
from datetime import datetime, timedelta
from tavily import TavilyClient
from config import Config

logger = logging.getLogger(__name__)


class TavilySearcher:
    """Tavily 搜索器"""

    def __init__(self):
        if not Config.TAVILY.api_key:
            raise ValueError("Tavily API Key 未配置")

        self.client = TavilyClient(api_key=Config.TAVILY.api_key)
        logger.info("Tavily 客户端初始化成功")

    def search_category(self, category: str, queries: List[str]) -> List[Dict]:
        """搜索单个分类"""

        results = []

        for query in queries:
            try:
                logger.info(f"搜索: [{category}] {query}")

                response = self.client.search(
                    query=query,
                    search_depth=Config.TAVILY.search_depth,
                    max_results=Config.TAVILY.max_results,
                    days=Config.TAVILY.days,
                    include_domains=None,
                    exclude_domains=None)

                if response and 'results' in response:
                    for item in response['results']:
                        content = item.get('content', '').strip()

                        # 跳过无效内容
                        if not content or len(content) < 50:
                            continue

                        results.append({
                            'category':
                            category,
                            'title':
                            item.get('title', ''),
                            'url':
                            item.get('url', ''),
                            'content':
                            content,
                            'score':
                            item.get('score', 0.0),
                            'published_date':
                            item.get('published_date', '')
                        })

                    logger.info(f"获取 {len(response['results'])} 条结果")
                else:
                    logger.warning(f"搜索无结果: {query}")

            except Exception as e:
                logger.error(f"搜索失败 [{query}]: {e}")

        filtered_results = self._filter_recent_news(results)
        logger.info(f"[{category}] 有效新闻: {len(filtered_results)} 条")

        return filtered_results

    def _filter_recent_news(self, news_list: List[Dict]) -> List[Dict]:
        """过滤 24 小时内的新闻"""

        cutoff_time = datetime.now() - timedelta(days=1)
        filtered = []

        for news in news_list:
            pub_date = news.get('published_date', '')

            if not pub_date:
                filtered.append(news)
                continue

            try:
                news_time = datetime.fromisoformat(
                    pub_date.replace('Z', '+00:00'))

                if news_time >= cutoff_time:
                    filtered.append(news)
                else:
                    logger.debug(f"过滤旧新闻: {news['title']} ({pub_date})")

            except Exception as e:
                logger.warning(f"时间解析失败: {pub_date} - {e}")
                filtered.append(news)

        return filtered

    def search_all_categories(self) -> List[Dict]:
        """搜索所有分类"""

        all_results = []
        search_queries = Config.get_search_queries()

        for category, queries in search_queries.items():
            logger.info(f"开始搜索 [{category}] 类新闻")
            category_results = self.search_category(category, queries)

            if category_results:
                all_results.extend(category_results)
                logger.info(f"[{category}] 获取 {len(category_results)} 条")
            else:
                logger.warning(f"[{category}] 未获取到任何新闻")

        logger.info(f"总计获取 {len(all_results)} 条新闻")
        return all_results
