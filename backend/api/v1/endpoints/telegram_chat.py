"""
API endpoints для работы с историей сообщений Telegram
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from models import User, TelegramUser, TelegramMessage
from api.v1.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

class TelegramMessageResponse(BaseModel):
    id: int
    telegram_user_id: int
    message_text: str
    message_type: str
    is_from_bot: bool
    created_at: datetime
    telegram_user: Optional[dict] = None

class ChatHistoryResponse(BaseModel):
    telegram_user: dict
    messages: List[TelegramMessageResponse]
    unread_count: int

@router.get("/chat-history/{telegram_user_id}")
async def get_chat_history(
    telegram_user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение истории переписки с пользователем Telegram"""
    
    try:
        # Проверяем права доступа (только админ, менеджер или HR)
        if current_user.role not in ["admin", "manager", "hr"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для просмотра истории переписки"
            )
        
        # Получаем пользователя Telegram
        telegram_user = db.query(TelegramUser).filter(TelegramUser.id == telegram_user_id).first()
        if not telegram_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь Telegram не найден"
            )
        
        # Получаем все сообщения с этим пользователем
        messages = db.query(TelegramMessage).filter(
            TelegramMessage.telegram_user_id == telegram_user_id
        ).order_by(TelegramMessage.created_at.desc()).limit(100).all()
        
        # Подсчитываем непрочитанные сообщения (от пользователя к боту)
        unread_count = db.query(TelegramMessage).filter(
            TelegramMessage.telegram_user_id == telegram_user_id,
            TelegramMessage.is_from_bot == False,
            TelegramMessage.is_read == False
        ).count()
        
        # Формируем ответ
        telegram_user_data = {
            "id": telegram_user.id,
            "telegram_id": telegram_user.telegram_id,
            "username": telegram_user.username,
            "first_name": telegram_user.first_name,
            "last_name": telegram_user.last_name,
            "is_active": telegram_user.is_active,
            "user_id": telegram_user.user_id
        }
        
        messages_data = []
        for message in messages:
            messages_data.append(TelegramMessageResponse(
                id=message.id,
                telegram_user_id=message.telegram_user_id,
                message_text=message.message_text,
                message_type=message.message_type,
                is_from_bot=message.is_from_bot,
                created_at=message.created_at
            ))
        
        logger.info(f"✅ Получена история переписки с пользователем {telegram_user.username}")
        
        return ChatHistoryResponse(
            telegram_user=telegram_user_data,
            messages=messages_data,
            unread_count=unread_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка получения истории переписки: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения истории переписки"
        )

@router.post("/mark-messages-read/{telegram_user_id}")
async def mark_messages_read(
    telegram_user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отметить сообщения как прочитанные"""
    
    try:
        # Проверяем права доступа
        if current_user.role not in ["admin", "manager", "hr"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для изменения статуса сообщений"
            )
        
        # Отмечаем все непрочитанные сообщения от пользователя как прочитанные
        updated_count = db.query(TelegramMessage).filter(
            TelegramMessage.telegram_user_id == telegram_user_id,
            TelegramMessage.is_from_bot == False,
            TelegramMessage.is_read == False
        ).update({"is_read": True})
        
        db.commit()
        
        logger.info(f"✅ Отмечено {updated_count} сообщений как прочитанные для пользователя {telegram_user_id}")
        
        return {"message": f"Отмечено {updated_count} сообщений как прочитанные"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка отметки сообщений как прочитанных: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка отметки сообщений как прочитанных"
        )

@router.get("/unread-counts")
async def get_unread_counts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение количества непрочитанных сообщений для всех пользователей"""
    
    try:
        # Проверяем права доступа
        if current_user.role not in ["admin", "manager", "hr"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для просмотра статистики сообщений"
            )
        
        # Получаем всех пользователей Telegram с количеством непрочитанных сообщений
        telegram_users = db.query(TelegramUser).filter(TelegramUser.is_active == True).all()
        
        unread_counts = []
        for user in telegram_users:
            unread_count = db.query(TelegramMessage).filter(
                TelegramMessage.telegram_user_id == user.id,
                TelegramMessage.is_from_bot == False,
                TelegramMessage.is_read == False
            ).count()
            
            if unread_count > 0:
                unread_counts.append({
                    "telegram_user_id": user.id,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "unread_count": unread_count
                })
        
        return {"unread_counts": unread_counts}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Ошибка получения статистики непрочитанных сообщений: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка получения статистики непрочитанных сообщений"
        )
