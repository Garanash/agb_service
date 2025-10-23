"""
Конфигурация Kafka
"""
import os
from typing import Dict, Any
from pydantic import BaseSettings

class KafkaConfig(BaseSettings):
    """Конфигурация Kafka"""
    
    # Включение/отключение Kafka
    enabled: bool = False
    
    # Брокеры Kafka
    bootstrap_servers: str = "localhost:9092,localhost:9093,localhost:9094"
    
    # Настройки безопасности
    security_protocol: str = "PLAINTEXT"  # PLAINTEXT, SASL_PLAINTEXT, SASL_SSL, SSL
    sasl_mechanism: str = "PLAIN"
    sasl_username: str = ""
    sasl_password: str = ""
    
    # Настройки producer
    producer_acks: str = "all"  # all, 1, 0
    producer_retries: int = 3
    producer_batch_size: int = 16384
    producer_linger_ms: int = 10
    producer_compression_type: str = "snappy"
    
    # Настройки consumer
    consumer_group_id: str = "agregator-service"
    consumer_auto_offset_reset: str = "earliest"  # earliest, latest
    consumer_enable_auto_commit: bool = True
    consumer_auto_commit_interval_ms: int = 1000
    consumer_max_poll_records: int = 500
    
    # Топики
    topics: Dict[str, Dict[str, Any]] = {
        "request-events": {
            "partitions": 6,
            "replication_factor": 3,
            "retention_ms": 604800000  # 7 дней
        },
        "workflow-events": {
            "partitions": 3,
            "replication_factor": 3,
            "retention_ms": 2592000000  # 30 дней
        },
        "notification-events": {
            "partitions": 3,
            "replication_factor": 3,
            "retention_ms": 259200000  # 3 дня
        },
        "security-events": {
            "partitions": 3,
            "replication_factor": 3,
            "retention_ms": 7776000000  # 90 дней
        },
        "hr-events": {
            "partitions": 3,
            "replication_factor": 3,
            "retention_ms": 31536000000  # 365 дней
        },
        "audit-events": {
            "partitions": 6,
            "replication_factor": 3,
            "retention_ms": 31536000000  # 365 дней
        }
    }
    
    class Config:
        env_file = ".env"
        env_prefix = "KAFKA_"

# Глобальная конфигурация
kafka_config = KafkaConfig()
