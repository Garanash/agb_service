#!/usr/bin/env python3
"""
Скрипт для мониторинга Kafka кластера
"""
import logging
import sys
import os
from typing import Dict, Any

# Добавляем путь к проекту
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from kafka import KafkaAdminClient
from kafka.admin import ConfigResource, ConfigResourceType
from kafka.kafka_config import kafka_config

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KafkaMonitoring:
    """Класс для мониторинга Kafka"""
    
    def __init__(self):
        self.admin_client = None
        self._initialize_admin_client()
    
    def _initialize_admin_client(self):
        """Инициализация admin client"""
        try:
            admin_config = {
                'bootstrap_servers': kafka_config.bootstrap_servers.split(','),
            }
            
            if kafka_config.security_protocol != "PLAINTEXT":
                admin_config.update({
                    'security_protocol': kafka_config.security_protocol,
                    'sasl_mechanism': kafka_config.sasl_mechanism,
                    'sasl_plain_username': kafka_config.sasl_username,
                    'sasl_plain_password': kafka_config.sasl_password,
                })
            
            self.admin_client = KafkaAdminClient(**admin_config)
            logger.info("✅ Kafka Admin Client инициализирован")
            
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации Kafka Admin Client: {e}")
            raise
    
    def get_topic_metrics(self, topic: str) -> Dict[str, Any]:
        """
        Получение метрик топика
        
        Args:
            topic: Название топика
        
        Returns:
            Dict[str, Any]: Метрики топика
        """
        try:
            # Получаем метаданные топика
            metadata = self.admin_client.describe_topics([topic])
            
            if topic not in metadata:
                return {"error": f"Топик {topic} не найден"}
            
            topic_metadata = metadata[topic]
            
            metrics = {
                "topic": topic,
                "partitions": len(topic_metadata.partitions),
                "replication_factor": len(topic_metadata.partitions[0].replicas),
                "partition_details": []
            }
            
            for partition_id, partition_metadata in topic_metadata.partitions.items():
                partition_info = {
                    "partition": partition_id,
                    "leader": partition_metadata.leader,
                    "replicas": partition_metadata.replicas,
                    "isr": partition_metadata.isr  # In-Sync Replicas
                }
                metrics["partition_details"].append(partition_info)
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения метрик топика {topic}: {e}")
            return {"error": str(e)}
    
    def get_consumer_group_metrics(self, group_id: str) -> Dict[str, Any]:
        """
        Получение метрик consumer group
        
        Args:
            group_id: ID consumer group
        
        Returns:
            Dict[str, Any]: Метрики consumer group
        """
        try:
            # Получаем информацию о consumer group
            consumer_groups = self.admin_client.describe_consumer_groups([group_id])
            
            if group_id not in consumer_groups:
                return {"error": f"Consumer group {group_id} не найден"}
            
            group_info = consumer_groups[group_id]
            
            metrics = {
                "group_id": group_id,
                "state": group_info.state,
                "members": len(group_info.members),
                "member_details": []
            }
            
            for member_id, member_info in group_info.members.items():
                member_detail = {
                    "member_id": member_id,
                    "client_id": member_info.client_id,
                    "client_host": member_info.client_host,
                    "assigned_partitions": member_info.assignment.partitions
                }
                metrics["member_details"].append(member_detail)
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения метрик consumer group {group_id}: {e}")
            return {"error": str(e)}
    
    def list_topics(self) -> list:
        """Получение списка всех топиков"""
        try:
            metadata = self.admin_client.list_topics()
            return list(metadata)
        except Exception as e:
            logger.error(f"❌ Ошибка получения списка топиков: {e}")
            return []
    
    def get_cluster_metadata(self) -> Dict[str, Any]:
        """Получение метаданных кластера"""
        try:
            metadata = self.admin_client.describe_cluster()
            
            cluster_info = {
                "cluster_id": metadata.cluster_id,
                "controller": metadata.controller,
                "brokers": []
            }
            
            for broker_id, broker_info in metadata.brokers.items():
                broker_detail = {
                    "broker_id": broker_id,
                    "host": broker_info.host,
                    "port": broker_info.port,
                    "rack": broker_info.rack
                }
                cluster_info["brokers"].append(broker_detail)
            
            return cluster_info
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения метаданных кластера: {e}")
            return {"error": str(e)}
    
    def close(self):
        """Закрытие admin client"""
        if self.admin_client:
            self.admin_client.close()
            logger.info("🔒 Kafka Admin Client закрыт")

def print_metrics(metrics: Dict[str, Any], title: str):
    """Красивый вывод метрик"""
    print(f"\n{'='*50}")
    print(f"📊 {title}")
    print(f"{'='*50}")
    
    if "error" in metrics:
        print(f"❌ Ошибка: {metrics['error']}")
        return
    
    for key, value in metrics.items():
        if isinstance(value, list):
            print(f"📋 {key}:")
            for item in value:
                if isinstance(item, dict):
                    for sub_key, sub_value in item.items():
                        print(f"   {sub_key}: {sub_value}")
                else:
                    print(f"   {item}")
        else:
            print(f"📈 {key}: {value}")

def main():
    """Главная функция мониторинга"""
    logger.info("🚀 Запуск мониторинга Kafka")
    
    monitoring = KafkaMonitoring()
    
    try:
        # Получаем метаданные кластера
        cluster_metrics = monitoring.get_cluster_metadata()
        print_metrics(cluster_metrics, "Метаданные кластера")
        
        # Получаем список топиков
        topics = monitoring.list_topics()
        print(f"\n📋 Всего топиков: {len(topics)}")
        print(f"📝 Список топиков: {', '.join(topics)}")
        
        # Получаем метрики основных топиков
        main_topics = [
            "request-events",
            "workflow-events", 
            "notification-events",
            "security-events",
            "hr-events",
            "audit-events"
        ]
        
        for topic in main_topics:
            if topic in topics:
                topic_metrics = monitoring.get_topic_metrics(topic)
                print_metrics(topic_metrics, f"Метрики топика {topic}")
        
        # Получаем метрики consumer groups
        consumer_groups = [
            "notification-service",
            "agregator-service"
        ]
        
        for group_id in consumer_groups:
            group_metrics = monitoring.get_consumer_group_metrics(group_id)
            print_metrics(group_metrics, f"Метрики consumer group {group_id}")
        
        print(f"\n{'='*50}")
        print("✅ Мониторинг завершен успешно")
        print(f"{'='*50}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка мониторинга: {e}")
        return False
    finally:
        monitoring.close()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
