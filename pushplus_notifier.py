import logging
import requests
from typing import Optional
from config import Config

logger = logging.getLogger(__name__)


class PushPlusNotifier:
    """PushPlus 推送器"""

    API_URL = "http://www.pushplus.plus/send"

    def __init__(self):
        self.token = Config.PUSHPLUS.token
        self.topic = Config.PUSHPLUS.topic
        self.template = Config.PUSHPLUS.template
        self.channel = Config.PUSHPLUS.channel

    def send(self, title: str, content: str) -> bool:
        """发送推送消息"""

        if not self.token:
            logger.error("PushPlus Token 未配置")
            return False

        try:
            data = self._build_payload(title, content)

            logger.info(f"📤 正在发送到 PushPlus...")

            response = requests.post(self.API_URL, json=data, timeout=30)

            result = response.json()

            if result.get('code') == 200:
                logger.info(f"PushPlus 发送成功")
                logger.info(f"   消息ID: {result.get('data', 'N/A')}")
                return True
            else:
                logger.error(f"PushPlus 发送失败")
                logger.error(f"   错误码: {result.get('code')}")
                logger.error(f"   错误信息: {result.get('msg')}")
                return False

        except requests.exceptions.Timeout:
            logger.error(" PushPlus 请求超时")
            return False
        except Exception as e:
            logger.error(f" PushPlus 发送异常: {e}")
            return False

    def _build_payload(self, title: str, content: str) -> dict:
        """构建请求数据"""

        payload = {
            "token": self.token,
            "title": title,
            "content": self._format_content(content),
            "template": self.template,
            "channel": self.channel
        }

        if self.topic:
            payload["topic"] = self.topic

        return payload

    def _format_content(self, content: str) -> str:
        """格式化内容"""

        if self.template == "html":
            return self._markdown_to_html(content)
        elif self.template == "markdown":
            return content
        else:
            return content.replace('#', '').replace('*', '')

    @staticmethod
    def _markdown_to_html(markdown_text: str) -> str:
        """Markdown 转 HTML（简化版）"""

        html = markdown_text

        # 标题转换
        html = html.replace('# ', '<h1>').replace('\n', '</h1>\n',
                                                  html.count('# '))
        html = html.replace('## ', '<h2>').replace('\n', '</h2>\n',
                                                   html.count('## '))
        html = html.replace('### ', '<h3>').replace('\n', '</h3>\n',
                                                    html.count('### '))

        # 加粗
        import re
        html = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html)

        # 链接
        html = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', html)

        # 换行
        html = html.replace('\n', '<br>')

        # 列表项
        html = re.sub(r'- (.*?)<br>', r'<li>\1</li>', html)

        return f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1 {{
                    color: #1a1a1a;
                    border-bottom: 2px solid #e0e0e0;
                    padding-bottom: 10px;
                }}
                h2 {{
                    color: #2c3e50;
                    margin-top: 30px;
                }}
                h3 {{
                    color: #34495e;
                }}
                a {{
                    color: #3498db;
                    text-decoration: none;
                }}
                a:hover {{
                    text-decoration: underline;
                }}
                li {{
                    margin-bottom: 8px;
                }}
                .emoji {{
                    font-size: 1.2em;
                }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
