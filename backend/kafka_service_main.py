"""
Главный файл для запуска Kafka сервисов
"""
import logging
import asyncio
from database import get_db
from services.notification_service_consumer import NotificationServiceConsumer

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Главная функция"""
    logger.info("🚀 Запуск Kafka сервисов")
    
    # Получаем подключение к БД
    db = next(get_db())
    
    try:
        # Создаем и запускаем consumer
        notification_consumer = NotificationServiceConsumer(db)
        notification_consumer.start()
        
    except KeyboardInterrupt:
        logger.info("🛑 Получен сигнал прерывания")
    except Exception as e:
        logger.error(f"❌ Ошибка запуска сервисов: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
