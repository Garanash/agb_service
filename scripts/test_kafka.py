#!/usr/bin/env python3
"""
Скрипт для тестирования Kafka интеграции
"""
import asyncio
import logging
import sys
import os
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from kafka import kafka_producer
from kafka.kafka_events import (
    RequestCreatedEvent, WorkflowContractorAssignedEvent,
    NotificationTelegramSentEvent, AuditUserActionEvent
)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_request_created_event():
    """Тест создания события заявки"""
    logger.info("🧪 Тестирование события создания заявки")
    
    event = RequestCreatedEvent(
        request_id=12345,
        customer_id=67890,
        title="Тестовая заявка на ремонт",
        description="Тестовое описание проблемы",
        urgency="high",
        region="Москва",
        city="Москва",
        address="ул. Тестовая, 1",
        equipment_type="Холодильник",
        priority="high"
    )
    
    success = kafka_producer.publish_event("request-events", event)
    
    if success:
        logger.info("✅ Событие создания заявки успешно отправлено")
    else:
        logger.error("❌ Ошибка отправки события создания заявки")
    
    return success

async def test_contractor_assigned_event():
    """Тест события назначения исполнителя"""
    logger.info("🧪 Тестирование события назначения исполнителя")
    
    event = WorkflowContractorAssignedEvent(
        request_id=12345,
        contractor_id=11111,
        manager_id=22222,
        previous_status="NEW",
        new_status="ASSIGNED",
        assignment_reason="Тестовое назначение"
    )
    
    success = kafka_producer.publish_event("workflow-events", event)
    
    if success:
        logger.info("✅ Событие назначения исполнителя успешно отправлено")
    else:
        logger.error("❌ Ошибка отправки события назначения исполнителя")
    
    return success

async def test_notification_event():
    """Тест события уведомления"""
    logger.info("🧪 Тестирование события уведомления")
    
    event = NotificationTelegramSentEvent(
        recipient_id=11111,
        recipient_telegram_username="@test_user",
        message_type="assignment",
        request_id=12345,
        message_content="Тестовое уведомление о назначении",
        delivery_status="sent",
        telegram_message_id=99999
    )
    
    success = kafka_producer.publish_event("notification-events", event)
    
    if success:
        logger.info("✅ Событие уведомления успешно отправлено")
    else:
        logger.error("❌ Ошибка отправки события уведомления")
    
    return success

async def test_audit_event():
    """Тест события аудита"""
    logger.info("🧪 Тестирование события аудита")
    
    event = AuditUserActionEvent(
        user_id=22222,
        user_role="manager",
        action="assign_contractor",
        resource_type="request",
        resource_id=12345,
        ip_address="192.168.1.100",
        user_agent="Test Agent",
        success=True,
        additional_data={"test": "data"}
    )
    
    success = kafka_producer.publish_event("audit-events", event)
    
    if success:
        logger.info("✅ Событие аудита успешно отправлено")
    else:
        logger.error("❌ Ошибка отправки события аудита")
    
    return success

async def test_batch_events():
    """Тест пакетной отправки событий"""
    logger.info("🧪 Тестирование пакетной отправки событий")
    
    events = [
        ("request-events", RequestCreatedEvent(
            request_id=99999,
            customer_id=88888,
            title="Пакетная заявка 1",
            description="Тест пакетной отправки",
            urgency="medium",
            region="СПб",
            city="Санкт-Петербург",
            address="ул. Пакетная, 1"
        ), "99999"),
        
        ("request-events", RequestCreatedEvent(
            request_id=99998,
            customer_id=88887,
            title="Пакетная заявка 2",
            description="Тест пакетной отправки",
            urgency="low",
            region="Москва",
            city="Москва",
            address="ул. Пакетная, 2"
        ), "99998"),
        
        ("workflow-events", WorkflowContractorAssignedEvent(
            request_id=99999,
            contractor_id=77777,
            manager_id=66666,
            previous_status="NEW",
            new_status="ASSIGNED",
            assignment_reason="Пакетное назначение"
        ), "99999")
    ]
    
    results = kafka_producer.publish_batch(events)
    
    logger.info(f"📊 Результаты пакетной отправки: {results}")
    
    return results["success"] > 0

async def main():
    """Главная функция тестирования"""
    logger.info("🚀 Начало тестирования Kafka интеграции")
    
    try:
        # Тестируем различные типы событий
        tests = [
            test_request_created_event(),
            test_contractor_assigned_event(),
            test_notification_event(),
            test_audit_event(),
            test_batch_events()
        ]
        
        results = await asyncio.gather(*tests, return_exceptions=True)
        
        # Анализируем результаты
        success_count = sum(1 for result in results if result is True)
        total_tests = len(tests)
        
        logger.info(f"📊 Результаты тестирования: {success_count}/{total_tests} тестов прошли успешно")
        
        if success_count == total_tests:
            logger.info("🎉 Все тесты прошли успешно!")
            return True
        else:
            logger.error("❌ Некоторые тесты не прошли")
            return False
            
    except Exception as e:
        logger.error(f"❌ Ошибка во время тестирования: {e}")
        return False
    finally:
        # Закрываем producer
        kafka_producer.close()

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
