"""
API endpoints для работы с Telegram ботом
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User
from api.v1.dependencies import get_current_user
from services.telegram_bot_service import get_telegram_bot_service, TelegramBotService

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/send-request/{request_id}")
async def send_request_to_contractors(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отправка заявки исполнителям в Telegram чат"""
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только менеджеры могут отправлять заявки в Telegram"
        )
    
    telegram_service = get_telegram_bot_service(db)
    
    try:
        success = await telegram_service.send_request_to_contractors(request_id)
        
        if success:
            return {
                "message": f"Заявка {request_id} отправлена в Telegram чат",
                "success": True
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось отправить заявку в Telegram чат"
            )
            
    except Exception as e:
        logger.error(f"❌ Ошибка отправки заявки {request_id} в Telegram: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка отправки в Telegram: {str(e)}"
        )

@router.post("/notify-contractor/{contractor_id}")
async def send_notification_to_contractor(
    contractor_id: int,
    notification_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отправка уведомления конкретному исполнителю"""
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только менеджеры могут отправлять уведомления исполнителям"
        )
    
    message = notification_data.get("message")
    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Сообщение обязательно"
        )
    
    telegram_service = get_telegram_bot_service(db)
    
    try:
        success = await telegram_service.send_notification_to_contractor(
            contractor_id=contractor_id,
            message=message,
            request_id=notification_data.get("request_id")
        )
        
        if success:
            return {
                "message": f"Уведомление отправлено исполнителю {contractor_id}",
                "success": True
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось отправить уведомление исполнителю"
            )
            
    except Exception as e:
        logger.error(f"❌ Ошибка отправки уведомления исполнителю {contractor_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка отправки уведомления: {str(e)}"
        )

@router.post("/assign-notification/{contractor_id}/{request_id}")
async def send_assignment_notification(
    contractor_id: int,
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отправка уведомления о назначении на заявку"""
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только менеджеры могут отправлять уведомления о назначении"
        )
    
    telegram_service = get_telegram_bot_service(db)
    
    try:
        success = await telegram_service.send_request_assignment_notification(
            contractor_id=contractor_id,
            request_id=request_id
        )
        
        if success:
            return {
                "message": f"Уведомление о назначении отправлено исполнителю {contractor_id}",
                "success": True
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось отправить уведомление о назначении"
            )
            
    except Exception as e:
        logger.error(f"❌ Ошибка отправки уведомления о назначении: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка отправки уведомления: {str(e)}"
        )

@router.post("/status-update/{contractor_id}/{request_id}")
async def send_status_update_notification(
    contractor_id: int,
    request_id: int,
    status_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Отправка уведомления об изменении статуса заявки"""
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только менеджеры могут отправлять уведомления об изменении статуса"
        )
    
    status = status_data.get("status")
    if not status:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Статус обязателен"
        )
    
    telegram_service = get_telegram_bot_service(db)
    
    try:
        success = await telegram_service.send_request_status_update(
            contractor_id=contractor_id,
            request_id=request_id,
            status=status
        )
        
        if success:
            return {
                "message": f"Уведомление об изменении статуса отправлено исполнителю {contractor_id}",
                "success": True
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Не удалось отправить уведомление об изменении статуса"
            )
            
    except Exception as e:
        logger.error(f"❌ Ошибка отправки уведомления об изменении статуса: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка отправки уведомления: {str(e)}"
        )

@router.post("/bulk-notification")
async def send_bulk_notification(
    notification_data: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Массовая отправка уведомлений исполнителям"""
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только менеджеры могут отправлять массовые уведомления"
        )
    
    message = notification_data.get("message")
    contractor_ids = notification_data.get("contractor_ids")
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Сообщение обязательно"
        )
    
    telegram_service = get_telegram_bot_service(db)
    
    try:
        results = await telegram_service.send_bulk_notification_to_contractors(
            message=message,
            contractor_ids=contractor_ids
        )
        
        return {
            "message": "Массовая отправка завершена",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка массовой отправки: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка массовой отправки: {str(e)}"
        )

@router.get("/verified-contractors")
async def get_verified_contractors_for_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение проверенных исполнителей с Telegram username"""
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только менеджеры могут просматривать исполнителей для уведомлений"
        )
    
    telegram_service = get_telegram_bot_service(db)
    
    try:
        contractors = await telegram_service.get_verified_contractors_for_notifications()
        
        result = []
        for contractor in contractors:
            result.append({
                "contractor_id": contractor.id,
                "name": f"{contractor.first_name} {contractor.last_name}",
                "telegram_username": contractor.telegram_username,
                "phone": contractor.phone,
                "email": contractor.email,
                "specializations": contractor.specializations or [],
                "availability_status": contractor.availability_status
            })
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения исполнителей для уведомлений: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка получения данных: {str(e)}"
        )

@router.get("/test-connection")
async def test_telegram_bot_connection(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Тестирование подключения к Telegram боту"""
    if current_user.role not in ["admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только администраторы могут тестировать подключение к боту"
        )
    
    telegram_service = get_telegram_bot_service(db)
    
    try:
        result = await telegram_service.test_bot_connection()
        return result
        
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования подключения к боту: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка тестирования: {str(e)}"
        )

@router.get("/bot-info")
async def get_bot_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Получение информации о боте"""
    if current_user.role not in ["manager", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Только менеджеры и администраторы могут просматривать информацию о боте"
        )
    
    telegram_service = get_telegram_bot_service(db)
    
    try:
        result = await telegram_service.test_bot_connection()
        
        if result.get("success"):
            return {
                "bot_configured": True,
                "bot_info": result.get("bot_info"),
                "chat_configured": bool(telegram_service.chat_id)
            }
        else:
            return {
                "bot_configured": False,
                "error": result.get("error"),
                "chat_configured": bool(telegram_service.chat_id)
            }
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения информации о боте: {e}")
        return {
            "bot_configured": False,
            "error": str(e),
            "chat_configured": bool(telegram_service.chat_id)
        }
