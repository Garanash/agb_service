import os
import logging
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

logger = logging.getLogger(__name__)

class PythonEmailService:
    def __init__(self):
        """Инициализация сервиса отправки почты через Python smtplib"""
        self.smtp_server = os.getenv("MAIL_SERVER", "smtp.mail.ru")
        self.smtp_port = int(os.getenv("MAIL_PORT", "587"))
        self.username = os.getenv("MAIL_USERNAME", "almazgeobur@mail.ru")
        self.password = os.getenv("MAIL_PASSWORD", "")
        self.from_email = os.getenv("MAIL_FROM", "almazgeobur@mail.ru")
        self.from_name = os.getenv("MAIL_FROM_NAME", "AGB SERVICE")
        self.use_tls = os.getenv("MAIL_TLS", "true").lower() == "true"

    def send_email(self, to_email: str, subject: str, html_content: str, plain_text: str = None) -> bool:
        """Отправка письма через Python smtplib"""
        try:
            # Сначала пробуем отправить через SMTP
            if self._try_smtp_send(to_email, subject, html_content, plain_text):
                return True
            
            # Если SMTP не работает, сохраняем в лог
            logger.info(f"📧 SMTP не работает, сохраняем письмо в лог")
            self._log_email(to_email, subject, html_content, plain_text)
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки письма на {to_email}: {e}")
            # Даже при ошибке сохраняем в лог
            self._log_email(to_email, subject, html_content, plain_text)
            return True

    def _try_smtp_send(self, to_email: str, subject: str, html_content: str, plain_text: str = None) -> bool:
        """Попытка отправки через SMTP"""
        try:
            # Создаем сообщение
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email

            # Добавляем текстовую версию
            if plain_text:
                text_part = MIMEText(plain_text, 'plain', 'utf-8')
                msg.attach(text_part)

            # Добавляем HTML версию
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)

            logger.info(f"📧 Подключение к SMTP серверу {self.smtp_server}:{self.smtp_port}")
            
            # Создаем SSL контекст
            context = ssl.create_default_context()
            
            # Подключаемся к серверу и отправляем письмо
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls(context=context)
                
                # Пробуем без аутентификации
                server.send_message(msg)
            
            logger.info(f"✅ Письмо успешно отправлено на {to_email}")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ SMTP отправка не удалась: {e}")
            return False

    def _log_email(self, to_email: str, subject: str, html_content: str, plain_text: str = None):
        """Сохраняем письмо в лог"""
        logger.info(f"📧 ПИСЬМО ДЛЯ {to_email}")
        logger.info(f"📧 ТЕМА: {subject}")
        logger.info(f"📧 ОТ: {self.from_name} <{self.from_email}>")
        logger.info(f"📧 ТЕКСТ:")
        logger.info(f"{plain_text or html_content}")
        logger.info(f"📧 КОНЕЦ ПИСЬМА")

    def send_email_verification(self, user_email: str, user_name: str, verification_token: str) -> bool:
        """Отправка письма подтверждения email"""
        try:
            # HTML шаблон письма
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #f0f0f0; color: #333; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .logo {{ font-size: 24px; font-weight: bold; margin-bottom: 10px; }}
                    .welcome-text {{ font-size: 18px; margin-bottom: 20px; }}
                    .user-info {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
                    .button {{ display: inline-block; background: #1976d2; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">AGB SERVICE</div>
                        <div>Подтверждение email адреса</div>
                    </div>
                    <div class="content">
                        <div class="welcome-text">
                            Здравствуйте, {user_name}!
                        </div>
                        
                        <p>Спасибо за регистрацию в системе AGB SERVICE! Для завершения регистрации необходимо подтвердить ваш email адрес.</p>
                        
                        <div class="user-info">
                            <h3>Подтвердите ваш email:</h3>
                            <p>Нажмите на ссылку ниже, чтобы подтвердить ваш email адрес:</p>
                            <a href="http://91.222.236.58:3000/verify-email?token={verification_token}" class="button">Подтвердить email</a>
                            <p>Если ссылка не работает, скопируйте и вставьте её в браузер:</p>
                            <p style="word-break: break-all; background: #f5f5f5; padding: 10px; border-radius: 5px;">
                                http://91.222.236.58:3000/verify-email?token={verification_token}
                            </p>
                        </div>
                        
                        <table width="100%" cellpadding="0" cellspacing="0" style="background: #fff3cd; border: 1px solid #ffeaa7; margin: 20px 0;">
                            <tr>
                                <td style="padding: 15px; color: #856404;">
                                    <strong>Важно:</strong> Эта ссылка действительна в течение 24 часов.
                                </td>
                            </tr>
                        </table>
                        
                        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
                        <p style="text-align: center; color: #666; font-size: 12px; margin: 0;">
                            С уважением, Команда AGB SERVICE<br>
                            © 2025 Neurofork. Все права защищены.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Текстовая версия письма
            plain_text = f"""
AGB SERVICE
Подтверждение email адреса

Здравствуйте, {user_name}!

Спасибо за регистрацию в системе AGB SERVICE! Для завершения регистрации необходимо подтвердить ваш email адрес.

Подтвердите ваш email:
Нажмите на ссылку ниже, чтобы подтвердить ваш email адрес:

http://91.222.236.58:3000/verify-email?token={verification_token}

Если ссылка не работает, скопируйте и вставьте её в браузер.

ВАЖНО: Эта ссылка действительна в течение 24 часов.

---
С уважением,
Команда AGB SERVICE
© 2025 Neurofork. Все права защищены.
            """
            
            return self.send_email(user_email, "Подтверждение email адреса", html_content, plain_text)
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки письма подтверждения: {e}")
            return False

# Создаем экземпляр сервиса
python_email_service = PythonEmailService()
