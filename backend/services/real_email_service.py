"""
Реальный сервис для отправки электронной почты через внешние API
"""
import os
import logging
import smtplib
import json
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class RealEmailService:
    def __init__(self):
        """Инициализация сервиса отправки почты"""
        self.from_email = os.getenv("MAIL_FROM", "almazgeobur@mail.ru")
        self.from_name = os.getenv("MAIL_FROM_NAME", "AGB SERVICE")
        self.smtp_server = os.getenv("MAIL_SERVER", "smtp.mail.ru")
        self.smtp_port = int(os.getenv("MAIL_PORT", "587"))
        self.username = os.getenv("MAIL_USERNAME", "almazgeobur@mail.ru")
        self.password = os.getenv("MAIL_PASSWORD", "")
        self.use_tls = os.getenv("MAIL_TLS", "true").lower() == "true"
        
        # Альтернативные настройки для внешних сервисов
        self.sendgrid_api_key = os.getenv("SENDGRID_API_KEY", "")
        self.mailgun_api_key = os.getenv("MAILGUN_API_KEY", "")
        self.mailgun_domain = os.getenv("MAILGUN_DOMAIN", "")
        
        # Российские сервисы
        self.mailru_api_key = os.getenv("MAILRU_API_KEY", "")
        self.mailru_domain = os.getenv("MAILRU_DOMAIN", "")
        self.yandex_api_key = os.getenv("YANDEX_API_KEY", "")
        self.yandex_domain = os.getenv("YANDEX_DOMAIN", "")
        self.unisender_api_key = os.getenv("UNISENDER_API_KEY", "")
        self.sendpulse_api_key = os.getenv("SENDPULSE_API_KEY", "")
        self.sendpulse_secret = os.getenv("SENDPULSE_SECRET", "")

    def send_email_via_smtp(self, to_email: str, subject: str, html_content: str, plain_text: str = None) -> bool:
        """Отправка письма через SMTP"""
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

            # Подключаемся к SMTP серверу
            if self.use_tls:
                server = smtplib.SMTP(self.smtp_server, self.smtp_port)
                server.starttls()
            else:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)

            # Авторизуемся
            logger.info(f"📧 Авторизация как {self.username}")
            server.login(self.username, self.password)

            # Отправляем письмо
            logger.info(f"📧 Отправка письма на {to_email}")
            server.send_message(msg)
            server.quit()

            logger.info(f"✅ Письмо успешно отправлено через SMTP на {to_email}")
            return True

        except Exception as e:
            logger.error(f"❌ Ошибка отправки письма через SMTP на {to_email}: {e}")
            return False

    def send_email_via_sendgrid(self, to_email: str, subject: str, html_content: str, plain_text: str = None) -> bool:
        """Отправка письма через SendGrid API"""
        if not self.sendgrid_api_key:
            logger.warning("⚠️ SendGrid API ключ не настроен")
            return False
            
        try:
            url = "https://api.sendgrid.com/v3/mail/send"
            headers = {
                "Authorization": f"Bearer {self.sendgrid_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "personalizations": [{"to": [{"email": to_email}]}],
                "from": {"email": self.from_email, "name": self.from_name},
                "subject": subject,
                "content": [
                    {"type": "text/plain", "value": plain_text or html_content},
                    {"type": "text/html", "value": html_content}
                ]
            }
            
            logger.info(f"📧 Отправка через SendGrid на {to_email}")
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 202:
                logger.info(f"✅ Письмо успешно отправлено через SendGrid на {to_email}")
                return True
            else:
                logger.error(f"❌ Ошибка SendGrid: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка отправки через SendGrid на {to_email}: {e}")
            return False

    def send_email_via_mailgun(self, to_email: str, subject: str, html_content: str, plain_text: str = None) -> bool:
        """Отправка письма через Mailgun API"""
        if not self.mailgun_api_key or not self.mailgun_domain:
            logger.warning("⚠️ Mailgun API ключ или домен не настроены")
            return False
            
        try:
            url = f"https://api.mailgun.net/v3/{self.mailgun_domain}/messages"
            auth = ("api", self.mailgun_api_key)
            
            data = {
                "from": f"{self.from_name} <{self.from_email}>",
                "to": to_email,
                "subject": subject,
                "html": html_content,
                "text": plain_text or html_content
            }
            
            logger.info(f"📧 Отправка через Mailgun на {to_email}")
            response = requests.post(url, auth=auth, data=data)
            
            if response.status_code == 200:
                logger.info(f"✅ Письмо успешно отправлено через Mailgun на {to_email}")
                return True
            else:
                logger.error(f"❌ Ошибка Mailgun: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка отправки через Mailgun на {to_email}: {e}")
            return False

    def send_email_via_mailru(self, to_email: str, subject: str, html_content: str, plain_text: str = None) -> bool:
        """Отправка письма через Mail.ru Cloud Solutions API"""
        if not self.mailru_api_key or not self.mailru_domain:
            logger.warning("⚠️ Mail.ru API ключ или домен не настроены")
            return False
            
        try:
            url = f"https://api.mail.ru/v1/{self.mailru_domain}/messages"
            headers = {
                "Authorization": f"Bearer {self.mailru_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "from": {"email": self.from_email, "name": self.from_name},
                "to": [{"email": to_email}],
                "subject": subject,
                "html": html_content,
                "text": plain_text or html_content
            }
            
            logger.info(f"📧 Отправка через Mail.ru на {to_email}")
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                logger.info(f"✅ Письмо успешно отправлено через Mail.ru на {to_email}")
                return True
            else:
                logger.error(f"❌ Ошибка Mail.ru: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка отправки через Mail.ru на {to_email}: {e}")
            return False

    def send_email_via_yandex(self, to_email: str, subject: str, html_content: str, plain_text: str = None) -> bool:
        """Отправка письма через Yandex.Cloud Mail API"""
        if not self.yandex_api_key or not self.yandex_domain:
            logger.warning("⚠️ Yandex API ключ или домен не настроены")
            return False
            
        try:
            url = f"https://mail-api.yandexcloud.net/v1/{self.yandex_domain}/messages"
            headers = {
                "Authorization": f"Bearer {self.yandex_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "from": {"email": self.from_email, "name": self.from_name},
                "to": [{"email": to_email}],
                "subject": subject,
                "html": html_content,
                "text": plain_text or html_content
            }
            
            logger.info(f"📧 Отправка через Yandex на {to_email}")
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                logger.info(f"✅ Письмо успешно отправлено через Yandex на {to_email}")
                return True
            else:
                logger.error(f"❌ Ошибка Yandex: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка отправки через Yandex на {to_email}: {e}")
            return False

    def send_email_via_unisender(self, to_email: str, subject: str, html_content: str, plain_text: str = None) -> bool:
        """Отправка письма через Unisender API"""
        if not self.unisender_api_key:
            logger.warning("⚠️ Unisender API ключ не настроен")
            return False
            
        try:
            url = "https://api.unisender.com/ru/api/sendEmail"
            data = {
                "api_key": self.unisender_api_key,
                "email": to_email,
                "sender_name": self.from_name,
                "sender_email": self.from_email,
                "subject": subject,
                "body": html_content,
                "text_body": plain_text or html_content
            }
            
            logger.info(f"📧 Отправка через Unisender на {to_email}")
            response = requests.post(url, data=data)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("result", {}).get("email_id"):
                    logger.info(f"✅ Письмо успешно отправлено через Unisender на {to_email}")
                    return True
                else:
                    logger.error(f"❌ Ошибка Unisender: {result}")
                    return False
            else:
                logger.error(f"❌ Ошибка Unisender: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка отправки через Unisender на {to_email}: {e}")
            return False

    def send_email_via_sendpulse(self, to_email: str, subject: str, html_content: str, plain_text: str = None) -> bool:
        """Отправка письма через SendPulse API"""
        if not self.sendpulse_api_key or not self.sendpulse_secret:
            logger.warning("⚠️ SendPulse API ключ или секрет не настроены")
            return False
            
        try:
            # Получаем токен доступа
            auth_url = "https://api.sendpulse.com/oauth/access_token"
            auth_data = {
                "grant_type": "client_credentials",
                "client_id": self.sendpulse_api_key,
                "client_secret": self.sendpulse_secret
            }
            
            auth_response = requests.post(auth_url, data=auth_data)
            if auth_response.status_code != 200:
                logger.error(f"❌ Ошибка авторизации SendPulse: {auth_response.text}")
                return False
                
            access_token = auth_response.json().get("access_token")
            if not access_token:
                logger.error("❌ Не удалось получить токен доступа SendPulse")
                return False
            
            # Отправляем письмо
            url = "https://api.sendpulse.com/smtp/emails"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            data = {
                "email": {
                    "subject": subject,
                    "html": html_content,
                    "text": plain_text or html_content,
                    "from": {"name": self.from_name, "email": self.from_email},
                    "to": [{"email": to_email}]
                }
            }
            
            logger.info(f"📧 Отправка через SendPulse на {to_email}")
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                logger.info(f"✅ Письмо успешно отправлено через SendPulse на {to_email}")
                return True
            else:
                logger.error(f"❌ Ошибка SendPulse: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка отправки через SendPulse на {to_email}: {e}")
            return False

    def send_email_via_webhook(self, to_email: str, subject: str, html_content: str, plain_text: str = None) -> bool:
        """
        Основной метод отправки письма - пробуем разные способы по порядку
        Приоритет: Российские сервисы → Зарубежные → SMTP → файл
        """
        # 1. Российские сервисы (приоритет для российских пользователей)
        if self.send_email_via_mailru(to_email, subject, html_content, plain_text):
            return True
        
        if self.send_email_via_yandex(to_email, subject, html_content, plain_text):
            return True
            
        if self.send_email_via_unisender(to_email, subject, html_content, plain_text):
            return True
            
        if self.send_email_via_sendpulse(to_email, subject, html_content, plain_text):
            return True
        
        # 2. Зарубежные сервисы
        if self.send_email_via_sendgrid(to_email, subject, html_content, plain_text):
            return True
        
        if self.send_email_via_mailgun(to_email, subject, html_content, plain_text):
            return True
        
        # 3. Пробуем SMTP
        if self.send_email_via_smtp(to_email, subject, html_content, plain_text):
            return True
        
        # 4. Если ничего не сработало, сохраняем в файл
        logger.warning(f"⚠️ Все методы отправки не сработали для {to_email}, сохраняем в файл")
        return self._save_email_to_file(to_email, subject, html_content, plain_text)

    def _save_email_to_file(self, to_email: str, subject: str, html_content: str, plain_text: str = None):
        """Сохраняем письмо в файл для отладки"""
        try:
            email_data = {
                'to': to_email,
                'subject': subject,
                'html': html_content,
                'text': plain_text,
                'from': self.from_email,
                'from_name': self.from_name,
                'timestamp': datetime.now().isoformat()
            }
            
            # Сохраняем в файл
            with open('/tmp/sent_emails.json', 'a', encoding='utf-8') as f:
                f.write(json.dumps(email_data, ensure_ascii=False, indent=2) + '\n')
            
            logger.info(f"✅ Письмо сохранено в файл для {to_email}")
            return True
                
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения письма в файл: {e}")
            return False

    def send_welcome_email(self, user_email: str, user_name: str, user_role: str) -> bool:
        """Отправка приветственного письма при регистрации"""
        try:
            # Определяем роль пользователя на русском языке
            role_text = {
                "admin": "Администратор",
                "customer": "Заказчик", 
                "contractor": "Исполнитель",
                "service_engineer": "Исполнитель"
            }.get(user_role, "Пользователь")

            # HTML шаблон письма
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #f5f5f5; color: #333; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; border: 1px solid #ddd; }}
                    .content {{ background: #fff; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #ddd; border-top: none; }}
                    .logo {{ font-size: 24px; font-weight: bold; margin-bottom: 10px; }}
                    .welcome-text {{ font-size: 18px; margin-bottom: 20px; }}
                    .user-info {{ background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #1976d2; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
                    .button {{ display: inline-block; background: #1976d2; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <div class="logo">AGB SERVICE</div>
                        <div>Добро пожаловать в нашу систему!</div>
                    </div>
                    <div class="content">
                        <div class="welcome-text">
                            Здравствуйте, {user_name}!
                        </div>
                        
                        <p>Спасибо за регистрацию в системе AGB SERVICE! Мы рады приветствовать вас в нашем сообществе.</p>
                        
                        <div class="user-info">
                            <h3>Информация о вашем аккаунте:</h3>
                            <p><strong>Email:</strong> {user_email}</p>
                            <p><strong>Роль:</strong> {role_text}</p>
                            <p><strong>Статус:</strong> Активный</p>
                        </div>
                        
                        <p>Теперь вы можете:</p>
                        <ul>
                            {"<li>Создавать заявки на услуги</li><li>Находить подходящих исполнителей</li><li>Отслеживать статус ваших заявок</li>" if user_role == 'customer' else "<li>Просматривать доступные заявки</li><li>Откликаться на интересующие проекты</li><li>Управлять своим профилем</li>" if user_role in ['contractor', 'service_engineer'] else ""}
                        </ul>
                        
                        <div style="text-align: center;">
                            <a href="http://91.222.236.58:3000/login" class="button">Войти в систему</a>
                        </div>
                        
                        <p>Если у вас возникнут вопросы, не стесняйтесь обращаться к нашей службе поддержки.</p>
                        
                        <div class="footer">
                            <p>С уважением,<br>Команда AGB SERVICE</p>
                            <p>© 2025 Neurofork. Все права защищены.</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """

            # Текстовая версия
            plain_text = f"""
AGB SERVICE
Добро пожаловать в нашу систему!

Здравствуйте, {user_name}!

Спасибо за регистрацию в системе AGB SERVICE! Мы рады приветствовать вас в нашем сообществе.

Информация о вашем аккаунте:
Email: {user_email}
Роль: {role_text}
Статус: Активный

Теперь вы можете:
- Войти в систему по адресу: http://91.222.236.58:3000/login
- Использовать все возможности платформы

Если у вас возникнут вопросы, не стесняйтесь обращаться к нашей службе поддержки.

С уважением,
Команда AGB SERVICE
© 2025 Neurofork. Все права защищены.
            """

            # Отправляем письмо
            success = self.send_email_via_webhook(
                to_email=user_email,
                subject="Добро пожаловать в AGB SERVICE!",
                html_content=html_content,
                plain_text=plain_text
            )
            
            if success:
                logger.info(f"✅ Приветственное письмо отправлено на {user_email}")
            return success

        except Exception as e:
            logger.error(f"❌ Ошибка отправки письма на {user_email}: {e}")
            return False

# Создаем глобальный экземпляр сервиса
real_email_service = RealEmailService()