import os
import logging
from .python_email_service import python_email_service

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        """Инициализация сервиса отправки почты"""
        self.python_service = python_email_service

    async def send_email_verification(self, user_email: str, user_name: str, verification_token: str) -> bool:
        """Отправка письма подтверждения email"""
        try:
            logger.info(f"📧 Отправка письма подтверждения на {user_email}")
            return self.python_service.send_email_verification(user_email, user_name, verification_token)
        except Exception as e:
            logger.error(f"❌ Ошибка отправки письма подтверждения: {e}")
            return False

    async def send_welcome_email(self, user_email: str, user_name: str, user_role: str) -> bool:
        """Отправка приветственного письма при регистрации"""
        try:
            logger.info(f"📧 Отправка приветственного письма на {user_email}")
            # Для простоты используем тот же метод, что и для подтверждения
            return self.python_service.send_email_verification(user_email, user_name, "welcome")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки приветственного письма: {e}")
            return False

    async def send_notification_email(self, user_email: str, subject: str, message: str) -> bool:
        """Отправка уведомительного письма"""
        try:
            logger.info(f"📧 Отправка уведомления на {user_email}")
            return self.python_service.send_email(user_email, subject, message, message)
        except Exception as e:
            logger.error(f"❌ Ошибка отправки уведомления: {e}")
            return False

# Создаем экземпляр сервиса
email_service = EmailService()