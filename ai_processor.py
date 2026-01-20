import logging
from typing import List, Dict
from openai import OpenAI
from config import Config

logger = logging.getLogger(__name__)


class AIProcessor:
    """AI 新闻处理器"""

    def __init__(self):
        if not Config.OPENAI.api_key:
            raise ValueError("OpenAI API Key 未配置")

        self.client = OpenAI(api_key=Config.OPENAI.api_key,
                             base_url=Config.OPENAI.base_url)
        logger.info("OpenAI 客户端初始化成功")

    def analyze_and_summarize(self, news_items: List[Dict]) -> str:
        """分析新闻并生成简报"""

        if not news_items:
            return "暂无新闻数据"

        categories = self._group_by_category(news_items)
        prompt = self._build_prompt(categories)

        try:
            logger.info("开始生成新闻简报")

            response = self.client.chat.completions.create(
                model=Config.OPENAI.model,
                messages=[{
                    "role":
                    "system",
                    "content": ("你是一位专业的新闻编辑。你的任务是从提供的新闻数据中提取有价值的内容并生成简报。\n\n"
                                "严格要求:\n"
                                "1. 直接输出最终简报,不要输出任何思考过程\n"
                                "2. 只使用 content 字段中的内容,忽略无效数据\n"
                                "3. 如果某条新闻的 content 为空或只是网站首页描述,直接跳过\n"
                                "4. 每个分类至少需要 2 条有效新闻才输出该分类\n"
                                "5. 每条新闻必须包含: 标题(加粗)、2-3句核心摘要、原文链接\n"
                                "6. 使用 Markdown 格式,语言为中文\n"
                                "7. 示例输出格式:\n"
                                "**标题**: 这是新闻标题\n"
                                "**摘要**: 这是新闻摘要\n"
                                "**链接**: http://example.com/news-article\n")
                }, {
                    "role": "user",
                    "content": prompt
                }],
                max_tokens=Config.OPENAI.max_tokens,
                temperature=Config.OPENAI.temperature)

            result = response.choices[0].message.content.strip()
            logger.info("新闻简报生成完成")

            return result

        except Exception as e:
            logger.error(f"新闻分析失败: {e}")
            return f"分析失败: {str(e)}"

    def _group_by_category(self,
                           news_items: List[Dict]) -> Dict[str, List[Dict]]:
        """按分类分组并过滤无效数据"""

        categories = {}

        for item in news_items:
            content = item.get('content', '').strip()

            # 过滤条件
            if not content or len(content) < 50:
                logger.debug(f"过滤无效新闻: {item.get('title', '无标题')}")
                continue

            # 过滤首页描述特征
            invalid_keywords = [
                'welcome to', 'homepage', 'official website', 'latest updates',
                'follow us', 'subscribe'
            ]

            if any(kw in content.lower() for kw in invalid_keywords):
                logger.debug(f"过滤首页链接: {item.get('url', '')}")
                continue

            category = item.get('category', '其他')
            if category not in categories:
                categories[category] = []
            categories[category].append(item)

        return categories

    def _build_prompt(self, categories: Dict[str, List[Dict]]) -> str:
        """构建 Prompt"""

        prompt = "请从以下新闻数据中提取有价值的内容生成每日简报。\n\n"
        prompt += "要求:\n"
        prompt += "1. 只处理 content 字段有实质内容的新闻\n"
        prompt += "2. 如果 content 是网站首页描述或宣传文案,直接跳过\n"
        prompt += "3. 每个分类至少需要 2 条有效新闻才输出\n"
        prompt += "4. 每条新闻包含: 标题(加粗)、核心内容摘要(2-3句)、原文链接\n"
        prompt += "5. 如果某个分类没有足够有效新闻,直接跳过该分类\n\n"
        prompt += "---\n\n"

        for category, items in categories.items():
            if len(items) < 2:
                continue

            prompt += f"## {category}\n\n"

            for idx, item in enumerate(items[:10], 1):
                title = item.get('title', '无标题')
                content = item.get('content', '')
                url = item.get('url', '')

                prompt += f"{idx}. 标题: {title}\n"
                prompt += f"   内容摘要: {content[:500]}\n"

                if url:
                    prompt += f"   原文链接: {url}\n"

                prompt += "\n"

        return prompt
