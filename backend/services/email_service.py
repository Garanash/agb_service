"""
Сервис для отправки электронной почты
"""
import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from .real_email_service import real_email_service

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        """Инициализация сервиса отправки почты"""
        self.smtp_server = os.getenv("MAIL_SERVER", "smtp.mail.ru")
        self.smtp_port = int(os.getenv("MAIL_PORT", 465))
        self.username = os.getenv("MAIL_USERNAME", "test@example.com")
        self.password = os.getenv("MAIL_PASSWORD", "test_password")
        self.from_email = os.getenv("MAIL_FROM", "test@example.com")
        self.from_name = os.getenv("MAIL_FROM_NAME", "AGB SERVICE")

    def _send_email(self, to_email: str, subject: str, html_content: str, plain_text: str = None) -> bool:
        """Базовый метод отправки письма через API"""
        try:
            # Используем реальный сервис отправки писем
            success = real_email_service.send_email_via_webhook(
                to_email=to_email,
                subject=subject,
                html_content=html_content,
                plain_text=plain_text
            )
            
            if success:
                logger.info(f"✅ Письмо отправлено на {to_email}")
            else:
                logger.error(f"❌ Не удалось отправить письмо на {to_email}")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки письма на {to_email}: {e}")
            return False

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
                            <a href="http://localhost:3000/login" class="button">Войти в систему</a>
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
- Войти в систему по адресу: http://localhost:3000/login
- Использовать все возможности платформы

Если у вас возникнут вопросы, не стесняйтесь обращаться к нашей службе поддержки.

С уважением,
Команда AGB SERVICE
© 2025 Neurofork. Все права защищены.
            """

            # Отправляем письмо
            success = self._send_email(
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

    async def send_email_verification(self, user_email: str, user_name: str, verification_token: str) -> bool:
        """Отправка письма подтверждения email"""
        try:
            # HTML версия
            html_content = f"""
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f4f4f4;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f4f4f4;">
        <tr>
            <td align="center" style="padding: 20px;">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border: 1px solid #ddd;">
                    <tr>
                        <td style="background: #667eea; color: white; padding: 30px; text-align: center;">
                            <h1 style="font-size: 24px; margin: 0;">AGB SERVICE</h1>
                            <p style="font-size: 14px; margin: 10px 0 0 0;">Подтверждение email адреса</p>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 30px;">
                            <h2 style="font-size: 18px; margin: 0 0 20px 0; color: #333;">Здравствуйте, {user_name}!</h2>
                            
                            <p style="color: #333; line-height: 1.5; margin: 0 0 20px 0;">Спасибо за регистрацию в системе AGB SERVICE! Для завершения регистрации необходимо подтвердить ваш email адрес.</p>
                            
                            <table width="100%" cellpadding="0" cellspacing="0" style="background: #f8f9fa; border: 1px solid #e9ecef; margin: 20px 0;">
                                <tr>
                                    <td style="padding: 20px; text-align: center;">
                                        <h3 style="font-size: 16px; margin: 0 0 15px 0; color: #333;">Подтвердите ваш email</h3>
                                        <p style="color: #333; margin: 0 0 15px 0;">Нажмите на кнопку ниже:</p>
                                        <a href="http://localhost:3000/verify-email?token={verification_token}" style="display: inline-block; background: #667eea; color: white; padding: 12px 30px; text-decoration: none; border-radius: 4px; font-weight: bold;">Подтвердить email</a>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="color: #333; margin: 20px 0 10px 0;">Если кнопка не работает, скопируйте ссылку:</p>
                            <p style="background: #f0f0f0; padding: 10px; font-family: monospace; font-size: 12px; word-break: break-all; margin: 0 0 20px 0;">
                                http://localhost:3000/verify-email?token={verification_token}
                            </p>
                            
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
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
            """

            # Текстовая версия
            plain_text = f"""
AGB SERVICE
Подтверждение email адреса

Здравствуйте, {user_name}!

Спасибо за регистрацию в системе AGB SERVICE! Для завершения регистрации необходимо подтвердить ваш email адрес.

Подтвердите ваш email:
Нажмите на ссылку ниже, чтобы подтвердить ваш email адрес:

http://localhost:3000/verify-email?token={verification_token}

Если ссылка не работает, скопируйте и вставьте её в браузер.

ВАЖНО: Эта ссылка действительна в течение 24 часов.

---
С уважением,
Команда AGB SERVICE
© 2025 Neurofork. Все права защищены.
            """

            # Отправляем письмо
            success = self._send_email(
                to_email=user_email,
                subject="Подтверждение email - AGB SERVICE",
                html_content=html_content,
                plain_text=plain_text
            )
            
            if success:
                logger.info(f"✅ Письмо подтверждения отправлено на {user_email}")
            return success

        except Exception as e:
            logger.error(f"❌ Ошибка отправки письма подтверждения на {user_email}: {e}")
            return False

    async def send_notification_email(self, user_email: str, subject: str, message_text: str) -> bool:
        """Отправка уведомительного письма"""
        try:
            success = self._send_email(
                to_email=user_email,
                subject=subject,
                html_content=f"<html><body><p>{message_text}</p></body></html>",
                plain_text=message_text
            )
            
            if success:
                logger.info(f"✅ Уведомление отправлено на {user_email}")
            return success

        except Exception as e:
            logger.error(f"❌ Ошибка отправки уведомления на {user_email}: {e}")
            return False

# Создаем глобальный экземпляр сервиса
email_service = EmailService()