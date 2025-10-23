"""
Сервис для работы с Telegram ботом
Отправляет заявки исполнителям и управляет уведомлениями
"""

import logging
import os
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import aiohttp
from sqlalchemy.orm import Session
from sqlalchemy import and_
from models import (
    RepairRequest, ContractorProfile, User, SecurityVerification
)

logger = logging.getLogger(__name__)

class TelegramBotService:
    """Сервис для работы с Telegram ботом"""
    
    def __init__(self, db: Session):
        self.db = db
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")  # ID чата для отправки заявок
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        if not self.bot_token:
            logger.warning("⚠️ TELEGRAM_BOT_TOKEN не установлен")
        if not self.chat_id:
            logger.warning("⚠️ TELEGRAM_CHAT_ID не установлен")
    
    async def send_request_to_contractors(self, request_id: int) -> bool:
        """Отправка заявки исполнителям в Telegram чат"""
        if not self.bot_token or not self.chat_id:
            logger.error("❌ Telegram бот не настроен")
            return False
        
        try:
            # Получаем информацию о заявке
            request = self.db.query(RepairRequest).filter(RepairRequest.id == request_id).first()
            if not request:
                logger.error(f"❌ Заявка {request_id} не найдена")
                return False
            
            # Формируем сообщение для отправки
            message = self._format_request_message(request)
            
            # Отправляем сообщение в чат
            success = await self._send_message(self.chat_id, message)
            
            if success:
                # Обновляем время отправки в бот
                request.sent_to_bot_at = datetime.now(timezone.utc)
                self.db.commit()
                logger.info(f"✅ Заявка {request_id} отправлена в Telegram чат")
            else:
                logger.error(f"❌ Не удалось отправить заявку {request_id} в Telegram чат")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки заявки {request_id} в Telegram: {e}")
            return False
    
    async def send_notification_to_contractor(
        self, 
        contractor_id: int, 
        message: str, 
        request_id: Optional[int] = None
    ) -> bool:
        """Отправка уведомления конкретному исполнителю"""
        if not self.bot_token or self.bot_token == "dummy_token_for_testing":
            logger.warning("⚠️ Telegram бот не настроен или использует тестовый токен")
            return False
        
        try:
            # Получаем информацию об исполнителе
            contractor = self.db.query(ContractorProfile).filter(
                ContractorProfile.id == contractor_id
            ).first()
            
            if not contractor or not contractor.telegram_username:
                logger.warning(f"⚠️ Исполнитель {contractor_id} не найден или не указан Telegram username")
                return False
            
            # Отправляем сообщение исполнителю
            success = await self._send_message_to_user(contractor.telegram_username, message)
            
            if success:
                logger.info(f"✅ Уведомление отправлено исполнителю {contractor_id}")
            else:
                logger.warning(f"⚠️ Не удалось отправить уведомление исполнителю {contractor_id} (возможно, пользователь не взаимодействовал с ботом)")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки уведомления исполнителю {contractor_id}: {e}")
            return False
    
    async def send_request_assignment_notification(
        self, 
        contractor_id: int, 
        request_id: int
    ) -> bool:
        """Отправка уведомления о назначении на заявку"""
        try:
            request = self.db.query(RepairRequest).filter(RepairRequest.id == request_id).first()
            if not request:
                return False
            
            message = f"""
🎯 **Вам назначена новая заявка!**

📋 **Заявка #{request_id}**
🔧 **Оборудование:** {request.equipment_type or 'Не указано'}
📍 **Местоположение:** {request.address or 'Не указано'}
⏰ **Предпочтительная дата:** {request.preferred_date.strftime('%d.%m.%Y %H:%M') if request.preferred_date else 'Не указана'}

📝 **Описание:**
{request.description}

💬 **Уточнения менеджера:**
{request.clarification_details or 'Нет уточнений'}

Для получения дополнительной информации обратитесь к менеджеру.
"""
            
            return await self.send_notification_to_contractor(contractor_id, message, request_id)
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки уведомления о назначении: {e}")
            return False
    
    async def send_request_status_update(
        self, 
        contractor_id: int, 
        request_id: int, 
        status: str
    ) -> bool:
        """Отправка уведомления об изменении статуса заявки"""
        try:
            request = self.db.query(RepairRequest).filter(RepairRequest.id == request_id).first()
            if not request:
                return False
            
            status_texts = {
                'assigned': 'назначена',
                'in_progress': 'в работе',
                'completed': 'завершена',
                'cancelled': 'отменена'
            }
            
            status_text = status_texts.get(status, status)
            
            message = f"""
📢 **Обновление статуса заявки**

📋 **Заявка #{request_id}** - статус изменен на: **{status_text}**

🔧 **Оборудование:** {request.equipment_type or 'Не указано'}
📍 **Местоположение:** {request.address or 'Не указано'}

{'✅ Заявка успешно завершена!' if status == 'completed' else ''}
{'❌ Заявка отменена' if status == 'cancelled' else ''}
"""
            
            return await self.send_notification_to_contractor(contractor_id, message, request_id)
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки уведомления об изменении статуса: {e}")
            return False
    
    async def get_verified_contractors_for_notifications(self) -> List[ContractorProfile]:
        """Получение проверенных исполнителей с Telegram username для уведомлений"""
        verified_contractors = self.db.query(ContractorProfile).join(SecurityVerification).filter(
            and_(
                SecurityVerification.verification_status == "approved",
                ContractorProfile.telegram_username.isnot(None),
                ContractorProfile.telegram_username != ""
            )
        ).all()
        
        return verified_contractors
    
    async def send_bulk_notification_to_contractors(
        self, 
        message: str, 
        contractor_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """Массовая отправка уведомлений исполнителям"""
        if not self.bot_token:
            return {"success": False, "error": "Telegram бот не настроен"}
        
        try:
            if contractor_ids:
                contractors = self.db.query(ContractorProfile).filter(
                    ContractorProfile.id.in_(contractor_ids)
                ).all()
            else:
                contractors = await self.get_verified_contractors_for_notifications()
            
            results = {
                "total": len(contractors),
                "successful": 0,
                "failed": 0,
                "errors": []
            }
            
            for contractor in contractors:
                if contractor.telegram_username:
                    success = await self._send_message_to_user(contractor.telegram_username, message)
                    if success:
                        results["successful"] += 1
                    else:
                        results["failed"] += 1
                        results["errors"].append(f"Исполнитель {contractor.id}: {contractor.telegram_username}")
                else:
                    results["failed"] += 1
                    results["errors"].append(f"Исполнитель {contractor.id}: нет Telegram username")
            
            logger.info(f"✅ Массовая отправка завершена: {results['successful']}/{results['total']} успешно")
            return results
            
        except Exception as e:
            logger.error(f"❌ Ошибка массовой отправки: {e}")
            return {"success": False, "error": str(e)}
    
    def _format_request_message(self, request: RepairRequest) -> str:
        """Форматирование сообщения о заявке для отправки в чат"""
        # Скрываем имя заказчика и точную стоимость для конфиденциальности
        message = f"""
🔧 **НОВАЯ ЗАЯВКА НА СЕРВИС**

📋 **Заявка #{request.id}**
🏢 **Компания:** [Скрыто]
🔧 **Тип оборудования:** {request.equipment_type or 'Не указано'}
🏭 **Бренд:** {request.equipment_brand or 'Не указан'}
📍 **Местоположение:** {request.address or 'Не указано'}
🌍 **Регион:** {request.region or 'Не указан'}

📝 **Описание проблемы:**
{request.problem_description or request.description}

⏰ **Предпочтительная дата:** {request.preferred_date.strftime('%d.%m.%Y %H:%M') if request.preferred_date else 'Не указана'}
⚡ **Срочность:** {self._get_urgency_text(request.urgency)}
🎯 **Приоритет:** {self._get_priority_text(request.priority)}

💬 **Уточнения менеджера:**
{request.clarification_details or 'Нет уточнений'}

💰 **Примерная стоимость:** [Уточняется менеджером]

---
👥 **Откликнуться могут только проверенные исполнители**
📞 **Для отклика обратитесь к менеджеру**
"""
        return message
    
    def _get_urgency_text(self, urgency: Optional[str]) -> str:
        """Получение текста срочности"""
        urgency_texts = {
            'low': 'Низкая',
            'medium': 'Средняя', 
            'high': 'Высокая',
            'critical': 'Критическая'
        }
        return urgency_texts.get(urgency, 'Не указана')
    
    def _get_priority_text(self, priority: Optional[str]) -> str:
        """Получение текста приоритета"""
        priority_texts = {
            'low': 'Низкий',
            'normal': 'Обычный',
            'high': 'Высокий',
            'urgent': 'Срочный'
        }
        return priority_texts.get(priority, 'Обычный')
    
    async def _send_message(self, chat_id: str, text: str) -> bool:
        """Отправка сообщения в чат"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/sendMessage"
                data = {
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "Markdown"
                }
                
                async with session.post(url, json=data) as response:
                    if response.status == 200:
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Ошибка отправки в Telegram: {error_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"❌ Ошибка HTTP запроса к Telegram: {e}")
            return False
    
    async def _send_message_to_user(self, username: str, text: str) -> bool:
        """Отправка сообщения пользователю по username"""
        try:
            # Сначала получаем chat_id пользователя
            chat_id = await self._get_user_chat_id(username)
            if not chat_id:
                return False
            
            return await self._send_message(chat_id, text)
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки сообщения пользователю {username}: {e}")
            return False
    
    async def _get_user_chat_id(self, username: str) -> Optional[str]:
        """Получение chat_id пользователя по username"""
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/getUpdates"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Ищем пользователя в последних обновлениях
                        for update in data.get("result", []):
                            if "message" in update:
                                message = update["message"]
                                if "from" in message:
                                    user = message["from"]
                                    if user.get("username") == username.replace("@", ""):
                                        return str(user["id"])
                        
                        logger.warning(f"⚠️ Пользователь {username} не найден в обновлениях бота")
                        return None
                    else:
                        logger.warning(f"⚠️ Ошибка получения обновлений: {response.status}")
                        return None
                        
        except Exception as e:
            logger.warning(f"⚠️ Ошибка получения chat_id для {username}: {e}")
            return None
    
    async def test_bot_connection(self) -> Dict[str, Any]:
        """Тестирование подключения к Telegram боту"""
        if not self.bot_token:
            return {"success": False, "error": "TELEGRAM_BOT_TOKEN не установлен"}
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/getMe"
                
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        bot_info = data.get("result", {})
                        return {
                            "success": True,
                            "bot_info": {
                                "id": bot_info.get("id"),
                                "username": bot_info.get("username"),
                                "first_name": bot_info.get("first_name"),
                                "can_join_groups": bot_info.get("can_join_groups"),
                                "can_read_all_group_messages": bot_info.get("can_read_all_group_messages")
                            }
                        }
                    else:
                        error_text = await response.text()
                        return {"success": False, "error": f"Ошибка API: {error_text}"}
                        
        except Exception as e:
            return {"success": False, "error": f"Ошибка подключения: {e}"}

def get_telegram_bot_service(db: Session) -> TelegramBotService:
    """Получение экземпляра сервиса Telegram бота"""
    return TelegramBotService(db)
