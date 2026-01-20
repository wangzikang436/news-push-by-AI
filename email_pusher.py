import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)


class EmailPusher:
    """邮件推送"""

    def __init__(self):
        if not all([
                Config.EMAIL.sender, Config.EMAIL.password,
                Config.EMAIL.receiver
        ]):
            raise ValueError("邮件配置不完整")

        logger.info(f"邮件配置: {Config.EMAIL.sender} -> {Config.EMAIL.receiver}")

    def send(self, content: str, subject: str = None) -> bool:
        """发送邮件"""

        if not content:
            logger.warning("邮件内容为空")
            return False

        subject = subject or f"每日新闻简报 - {datetime.now():%Y-%m-%d}"

        try:
            message = self._create_message(subject, content)
            self._send_via_smtp(message)

            logger.info(f"邮件发送成功: {Config.EMAIL.receiver}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"认证失败: {e}")
            return False
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            return False

    def _create_message(self, subject: str, content: str) -> MIMEMultipart:
        """创建邮件消息"""

        message = MIMEMultipart('alternative')
        message['From'] = Config.EMAIL.sender
        message['To'] = Config.EMAIL.receiver
        message['Subject'] = subject

        html_content = self._markdown_to_html(content)

        message.attach(MIMEText(content, 'plain', 'utf-8'))
        message.attach(MIMEText(html_content, 'html', 'utf-8'))

        return message

    def _send_via_smtp(self, message: MIMEMultipart):
        """通过 SMTP 发送邮件"""

        with smtplib.SMTP_SSL(Config.EMAIL.smtp_server,
                              Config.EMAIL.smtp_port,
                              timeout=30) as server:
            server.login(Config.EMAIL.sender, Config.EMAIL.password)
            server.send_message(message)

    def _markdown_to_html(self, markdown_text: str) -> str:
        """Markdown 转 HTML"""

        html = markdown_text

        import re
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)

        html = html.replace('\n\n', '</p><p>')
        html = f'<html><body style="font-family: Arial, sans-serif; line-height: 1.6; padding: 20px;"><p>{html}</p></body></html>'

        return html
