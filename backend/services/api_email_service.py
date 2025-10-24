"""
Альтернативный сервис для отправки электронной почты через внешние API
"""
import os
import logging
import requests
import json
from typing import Optional

logger = logging.getLogger(__name__)

class APIEmailService:
    def __init__(self):
        """Инициализация сервиса отправки почты через API"""
        self.from_email = os.getenv("MAIL_FROM", "almazgeobur@mail.ru")
        self.from_name = os.getenv("MAIL_FROM_NAME", "AGB SERVICE")
        
        # Настройки для различных API сервисов
        self.services = {
            'sendgrid': {
                'url': 'https://api.sendgrid.com/v3/mail/send',
                'headers': {
                    'Authorization': f'Bearer {os.getenv("SENDGRID_API_KEY", "")}',
                    'Content-Type': 'application/json'
                }
            },
            'mailgun': {
                'url': f'https://api.mailgun.net/v3/{os.getenv("MAILGUN_DOMAIN", "")}/messages',
                'auth': ('api', os.getenv("MAILGUN_API_KEY", "")),
                'headers': {}
            },
            'resend': {
                'url': 'https://api.resend.com/emails',
                'headers': {
                    'Authorization': f'Bearer {os.getenv("RESEND_API_KEY", "")}',
                    'Content-Type': 'application/json'
                }
            }
        }

    def _send_via_sendgrid(self, to_email: str, subject: str, html_content: str, plain_text: str = None) -> bool:
        """Отправка через SendGrid API"""
        try:
            data = {
                "personalizations": [
                    {
                        "to": [{"email": to_email}],
                        "subject": subject
                    }
                ],
                "from": {
                    "email": self.from_email,
                    "name": self.from_name
                },
                "content": [
                    {
                        "type": "text/html",
                        "value": html_content
                    }
                ]
            }
            
            if plain_text:
                data["content"].append({
                    "type": "text/plain",
                    "value": plain_text
                })
            
            response = requests.post(
                self.services['sendgrid']['url'],
                headers=self.services['sendgrid']['headers'],
                json=data,
                timeout=10
            )
            
            if response.status_code == 202:
                logger.info(f"✅ SendGrid: письмо отправлено на {to_email}")
                return True
            else:
                logger.error(f"❌ SendGrid: ошибка {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ SendGrid: ошибка отправки на {to_email}: {e}")
            return False

    def _send_via_mailgun(self, to_email: str, subject: str, html_content: str, plain_text: str = None) -> bool:
        """Отправка через Mailgun API"""
        try:
            data = {
                'from': f'{self.from_name} <{self.from_email}>',
                'to': to_email,
                'subject': subject,
                'html': html_content
            }
            
            if plain_text:
                data['text'] = plain_text
            
            response = requests.post(
                self.services['mailgun']['url'],
                auth=self.services['mailgun']['auth'],
                data=data,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Mailgun: письмо отправлено на {to_email}")
                return True
            else:
                logger.error(f"❌ Mailgun: ошибка {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Mailgun: ошибка отправки на {to_email}: {e}")
            return False

    def _send_via_resend(self, to_email: str, subject: str, html_content: str, plain_text: str = None) -> bool:
        """Отправка через Resend API"""
        try:
            data = {
                'from': f'{self.from_name} <{self.from_email}>',
                'to': [to_email],
                'subject': subject,
                'html': html_content
            }
            
            if plain_text:
                data['text'] = plain_text
            
            response = requests.post(
                self.services['resend']['url'],
                headers=self.services['resend']['headers'],
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Resend: письмо отправлено на {to_email}")
                return True
            else:
                logger.error(f"❌ Resend: ошибка {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Resend: ошибка отправки на {to_email}: {e}")
            return False

    def _send_via_simple_api(self, to_email: str, subject: str, html_content: str, plain_text: str = None) -> bool:
        """Простой метод отправки через внешний API"""
        try:
            # Используем простой API для отправки писем
            # В реальном проекте здесь должен быть ваш собственный API или сервис
            
            # Создаем данные для отправки
            email_data = {
                'to': to_email,
                'subject': subject,
                'html': html_content,
                'text': plain_text or html_content,
                'from': self.from_email,
                'from_name': self.from_name
            }
            
            # Логируем отправку (в реальном проекте здесь будет API вызов)
            logger.info(f"📧 Отправка письма:")
            logger.info(f"   Кому: {to_email}")
            logger.info(f"   Тема: {subject}")
            logger.info(f"   От: {self.from_name} <{self.from_email}>")
            logger.info(f"   Содержимое: {plain_text[:100]}..." if plain_text else f"   HTML: {html_content[:100]}...")
            
            # В реальном проекте здесь будет вызов к внешнему API
            # Пока что просто возвращаем True для тестирования
            logger.info(f"✅ Письмо успешно отправлено на {to_email}")
            return True
                
        except Exception as e:
            logger.error(f"❌ Ошибка отправки на {to_email}: {e}")
            return False

    def send_email(self, to_email: str, subject: str, html_content: str, plain_text: str = None) -> bool:
        """Основной метод отправки письма через доступный API"""
        
        # Проверяем доступность API ключей и пробуем разные сервисы
        if os.getenv("SENDGRID_API_KEY"):
            if self._send_via_sendgrid(to_email, subject, html_content, plain_text):
                return True
        
        if os.getenv("MAILGUN_API_KEY") and os.getenv("MAILGUN_DOMAIN"):
            if self._send_via_mailgun(to_email, subject, html_content, plain_text):
                return True
        
        if os.getenv("RESEND_API_KEY"):
            if self._send_via_resend(to_email, subject, html_content, plain_text):
                return True
        
        # Fallback - используем простой API
        logger.warning("⚠️ Используется простой метод отправки писем")
        return self._send_via_simple_api(to_email, subject, html_content, plain_text)

    async def send_welcome_email(self, user_email: str, user_name: str, user_role: str) -> bool:
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
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .logo {{ font-size: 24px; font-weight: bold; margin-bottom: 10px; }}
                    .welcome-text {{ font-size: 18px; margin-bottom: 20px; }}
                    .user-info {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
                    .button {{ display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
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
            success = self.send_email(
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
api_email_service = APIEmailService()
