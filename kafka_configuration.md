# ⚙️ Конфигурация Apache Kafka

## 🐳 Docker Compose для Kafka кластера

### `docker-compose.kafka.yml`
```yaml
version: '3.8'

services:
  # Zookeeper (требуется для Kafka < 2.8)
  zookeeper-1:
    image: confluentinc/cp-zookeeper:7.4.0
    hostname: zookeeper-1
    container_name: zookeeper-1
    ports:
      - "2181:2181"
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
      ZOOKEEPER_SERVER_ID: 1
      ZOOKEEPER_SERVERS: zookeeper-1:2888:3888;zookeeper-2:2888:3888;zookeeper-3:2888:3888
    volumes:
      - zookeeper-1-data:/var/lib/zookeeper/data
      - zookeeper-1-logs:/var/lib/zookeeper/log
    networks:
      - kafka-network

  zookeeper-2:
    image: confluentinc/cp-zookeeper:7.4.0
    hostname: zookeeper-2
    container_name: zookeeper-2
    ports:
      - "2182:2181"
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
      ZOOKEEPER_SERVER_ID: 2
      ZOOKEEPER_SERVERS: zookeeper-1:2888:3888;zookeeper-2:2888:3888;zookeeper-3:2888:3888
    volumes:
      - zookeeper-2-data:/var/lib/zookeeper/data
      - zookeeper-2-logs:/var/lib/zookeeper/log
    networks:
      - kafka-network

  zookeeper-3:
    image: confluentinc/cp-zookeeper:7.4.0
    hostname: zookeeper-3
    container_name: zookeeper-3
    ports:
      - "2183:2181"
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
      ZOOKEEPER_SERVER_ID: 3
      ZOOKEEPER_SERVERS: zookeeper-1:2888:3888;zookeeper-2:2888:3888;zookeeper-3:2888:3888
    volumes:
      - zookeeper-3-data:/var/lib/zookeeper/data
      - zookeeper-3-logs:/var/lib/zookeeper/log
    networks:
      - kafka-network

  # Kafka Brokers
  kafka-1:
    image: confluentinc/cp-kafka:7.4.0
    hostname: kafka-1
    container_name: kafka-1
    ports:
      - "9092:9092"
      - "19092:19092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper-1:2181,zookeeper-2:2181,zookeeper-3:2181
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-1:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:29092,PLAINTEXT_HOST://0.0.0.0:9092
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 2
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_NUM_PARTITIONS: 3
      KAFKA_DEFAULT_REPLICATION_FACTOR: 3
      KAFKA_MIN_INSYNC_REPLICAS: 2
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'false'
      KAFKA_LOG_RETENTION_HOURS: 168  # 7 дней
      KAFKA_LOG_SEGMENT_BYTES: 1073741824  # 1GB
      KAFKA_LOG_CLEANUP_POLICY: delete
      KAFKA_COMPRESSION_TYPE: snappy
      KAFKA_MESSAGE_MAX_BYTES: 10485760  # 10MB
      KAFKA_REPLICA_FETCH_MAX_BYTES: 10485760  # 10MB
      KAFKA_LOG_FLUSH_INTERVAL_MESSAGES: 10000
      KAFKA_LOG_FLUSH_INTERVAL_MS: 1000
    volumes:
      - kafka-1-data:/var/lib/kafka/data
    networks:
      - kafka-network
    depends_on:
      - zookeeper-1
      - zookeeper-2
      - zookeeper-3

  kafka-2:
    image: confluentinc/cp-kafka:7.4.0
    hostname: kafka-2
    container_name: kafka-2
    ports:
      - "9093:9092"
      - "19093:19092"
    environment:
      KAFKA_BROKER_ID: 2
      KAFKA_ZOOKEEPER_CONNECT: zookeeper-1:2181,zookeeper-2:2181,zookeeper-3:2181
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-2:29092,PLAINTEXT_HOST://localhost:9093
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:29092,PLAINTEXT_HOST://0.0.0.0:9092
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 2
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_NUM_PARTITIONS: 3
      KAFKA_DEFAULT_REPLICATION_FACTOR: 3
      KAFKA_MIN_INSYNC_REPLICAS: 2
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'false'
      KAFKA_LOG_RETENTION_HOURS: 168
      KAFKA_LOG_SEGMENT_BYTES: 1073741824
      KAFKA_LOG_CLEANUP_POLICY: delete
      KAFKA_COMPRESSION_TYPE: snappy
      KAFKA_MESSAGE_MAX_BYTES: 10485760
      KAFKA_REPLICA_FETCH_MAX_BYTES: 10485760
      KAFKA_LOG_FLUSH_INTERVAL_MESSAGES: 10000
      KAFKA_LOG_FLUSH_INTERVAL_MS: 1000
    volumes:
      - kafka-2-data:/var/lib/kafka/data
    networks:
      - kafka-network
    depends_on:
      - zookeeper-1
      - zookeeper-2
      - zookeeper-3

  kafka-3:
    image: confluentinc/cp-kafka:7.4.0
    hostname: kafka-3
    container_name: kafka-3
    ports:
      - "9094:9092"
      - "19094:19092"
    environment:
      KAFKA_BROKER_ID: 3
      KAFKA_ZOOKEEPER_CONNECT: zookeeper-1:2181,zookeeper-2:2181,zookeeper-3:2181
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka-3:29092,PLAINTEXT_HOST://localhost:9094
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:29092,PLAINTEXT_HOST://0.0.0.0:9092
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 3
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 2
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 3
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_NUM_PARTITIONS: 3
      KAFKA_DEFAULT_REPLICATION_FACTOR: 3
      KAFKA_MIN_INSYNC_REPLICAS: 2
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: 'false'
      KAFKA_LOG_RETENTION_HOURS: 168
      KAFKA_LOG_SEGMENT_BYTES: 1073741824
      KAFKA_LOG_CLEANUP_POLICY: delete
      KAFKA_COMPRESSION_TYPE: snappy
      KAFKA_MESSAGE_MAX_BYTES: 10485760
      KAFKA_REPLICA_FETCH_MAX_BYTES: 10485760
      KAFKA_LOG_FLUSH_INTERVAL_MESSAGES: 10000
      KAFKA_LOG_FLUSH_INTERVAL_MS: 1000
    volumes:
      - kafka-3-data:/var/lib/kafka/data
    networks:
      - kafka-network
    depends_on:
      - zookeeper-1
      - zookeeper-2
      - zookeeper-3

  # Kafka UI для мониторинга
  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    container_name: kafka-ui
    ports:
      - "8080:8080"
    environment:
      KAFKA_CLUSTERS_0_NAME: local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka-1:29092,kafka-2:29092,kafka-3:29092
      KAFKA_CLUSTERS_0_ZOOKEEPER: zookeeper-1:2181,zookeeper-2:2181,zookeeper-3:2181
    networks:
      - kafka-network
    depends_on:
      - kafka-1
      - kafka-2
      - kafka-3

  # Schema Registry (опционально)
  schema-registry:
    image: confluentinc/cp-schema-registry:7.4.0
    hostname: schema-registry
    container_name: schema-registry
    ports:
      - "8081:8081"
    environment:
      SCHEMA_REGISTRY_HOST_NAME: schema-registry
      SCHEMA_REGISTRY_KAFKASTORE_BOOTSTRAP_SERVERS: kafka-1:29092,kafka-2:29092,kafka-3:29092
      SCHEMA_REGISTRY_KAFKASTORE_CONNECTION_URL: zookeeper-1:2181,zookeeper-2:2181,zookeeper-3:2181
      SCHEMA_REGISTRY_LISTENERS: http://0.0.0.0:8081
    networks:
      - kafka-network
    depends_on:
      - kafka-1
      - kafka-2
      - kafka-3

volumes:
  zookeeper-1-data:
  zookeeper-1-logs:
  zookeeper-2-data:
  zookeeper-2-logs:
  zookeeper-3-data:
  zookeeper-3-logs:
  kafka-1-data:
  kafka-2-data:
  kafka-3-data:

networks:
  kafka-network:
    driver: bridge
```

## 🔧 Конфигурационные файлы Kafka

### `server.properties` (для каждого брокера)
```properties
# Базовые настройки
broker.id=1
listeners=PLAINTEXT://0.0.0.0:9092,PLAINTEXT_HOST://0.0.0.0:9092
advertised.listeners=PLAINTEXT://kafka-1:29092,PLAINTEXT_HOST://localhost:9092
inter.broker.listener.name=PLAINTEXT

# Zookeeper
zookeeper.connect=zookeeper-1:2181,zookeeper-2:2181,zookeeper-3:2181
zookeeper.connection.timeout.ms=18000

# Логирование
log.dirs=/var/lib/kafka/data
log.retention.hours=168
log.retention.bytes=1073741824
log.segment.bytes=1073741824
log.cleanup.policy=delete
log.flush.interval.messages=10000
log.flush.interval.ms=1000

# Репликация
default.replication.factor=3
min.insync.replicas=2
offsets.topic.replication.factor=3
transaction.state.log.replication.factor=3
transaction.state.log.min.isr=2

# Производительность
num.network.threads=8
num.io.threads=8
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600
num.partitions=3

# Сжатие
compression.type=snappy

# Размеры сообщений
message.max.bytes=10485760
replica.fetch.max.bytes=10485760

# Топики
auto.create.topics.enable=false
delete.topic.enable=true

# Группы потребителей
group.initial.rebalance.delay.ms=0
offsets.retention.minutes=10080

# Безопасность (для продакшена)
# security.inter.broker.protocol=PLAINTEXT
# listeners=SSL://0.0.0.0:9093
# advertised.listeners=SSL://kafka-1:29093
# ssl.keystore.location=/var/ssl/private/kafka.server.keystore.jks
# ssl.keystore.password=test1234
# ssl.key.password=test1234
# ssl.truststore.location=/var/ssl/private/kafka.server.truststore.jks
# ssl.truststore.password=test1234
# ssl.client.auth=required
```

## 📝 Скрипты для управления топиками

### `create_topics.sh`
```bash
#!/bin/bash

# Конфигурация
KAFKA_HOME="/opt/kafka"
BOOTSTRAP_SERVERS="localhost:9092,localhost:9093,localhost:9094"

# Функция создания топика
create_topic() {
    local topic_name=$1
    local partitions=$2
    local replication_factor=$3
    local retention_ms=$4
    
    echo "Создание топика: $topic_name"
    
    $KAFKA_HOME/bin/kafka-topics.sh \
        --bootstrap-server $BOOTSTRAP_SERVERS \
        --create \
        --topic $topic_name \
        --partitions $partitions \
        --replication-factor $replication_factor \
        --config retention.ms=$retention_ms \
        --config compression.type=snappy \
        --config min.insync.replicas=2 \
        --if-not-exists
    
    if [ $? -eq 0 ]; then
        echo "✅ Топик $topic_name создан успешно"
    else
        echo "❌ Ошибка создания топика $topic_name"
        exit 1
    fi
}

# Создание всех топиков
echo "🚀 Создание топиков Kafka для агрегатора услуг"

create_topic "request-events" 6 3 604800000      # 7 дней
create_topic "workflow-events" 3 3 2592000000    # 30 дней
create_topic "notification-events" 3 3 259200000 # 3 дня
create_topic "security-events" 3 3 7776000000    # 90 дней
create_topic "hr-events" 3 3 31536000000        # 365 дней
create_topic "audit-events" 6 3 31536000000     # 365 дней

# Создание Dead Letter Queues
create_topic "request-events-dlq" 3 3 604800000
create_topic "workflow-events-dlq" 3 3 2592000000
create_topic "notification-events-dlq" 3 3 259200000
create_topic "security-events-dlq" 3 3 7776000000
create_topic "hr-events-dlq" 3 3 31536000000
create_topic "audit-events-dlq" 6 3 31536000000

echo "🎉 Все топики созданы успешно!"

# Показать список топиков
echo "📋 Список созданных топиков:"
$KAFKA_HOME/bin/kafka-topics.sh --bootstrap-server $BOOTSTRAP_SERVERS --list
```

### `delete_topics.sh`
```bash
#!/bin/bash

# Конфигурация
KAFKA_HOME="/opt/kafka"
BOOTSTRAP_SERVERS="localhost:9092,localhost:9093,localhost:9094"

# Список топиков для удаления
TOPICS=(
    "request-events"
    "workflow-events"
    "notification-events"
    "security-events"
    "hr-events"
    "audit-events"
    "request-events-dlq"
    "workflow-events-dlq"
    "notification-events-dlq"
    "security-events-dlq"
    "hr-events-dlq"
    "audit-events-dlq"
)

echo "🗑️ Удаление топиков Kafka"

for topic in "${TOPICS[@]}"; do
    echo "Удаление топика: $topic"
    
    $KAFKA_HOME/bin/kafka-topics.sh \
        --bootstrap-server $BOOTSTRAP_SERVERS \
        --delete \
        --topic $topic
    
    if [ $? -eq 0 ]; then
        echo "✅ Топик $topic удален успешно"
    else
        echo "❌ Ошибка удаления топика $topic"
    fi
done

echo "🎉 Удаление топиков завершено!"
```

## 🔍 Мониторинг и алерты

### `kafka_monitoring_config.yml`
```yaml
# Конфигурация для Prometheus + Grafana мониторинга Kafka

# Prometheus targets
prometheus_targets:
  - job_name: 'kafka-jmx'
    static_configs:
      - targets: 
        - 'kafka-1:9092'
        - 'kafka-2:9092'
        - 'kafka-3:9092'
    metrics_path: /metrics
    scrape_interval: 15s

# Grafana dashboards
grafana_dashboards:
  - name: "Kafka Cluster Overview"
    panels:
      - title: "Messages In/Out per Second"
        type: "graph"
        targets:
          - "kafka_server_brokertopicmetrics_messagesinpersec"
          - "kafka_server_brokertopicmetrics_messagesoutpersec"
      
      - title: "Consumer Lag"
        type: "graph"
        targets:
          - "kafka_consumer_consumer_lag_sum"
      
      - title: "Disk Usage"
        type: "graph"
        targets:
          - "kafka_log_size_bytes"

# Алерты
alerts:
  - alert: "KafkaConsumerLagHigh"
    expr: "kafka_consumer_consumer_lag_sum > 10000"
    for: "5m"
    labels:
      severity: "warning"
    annotations:
      summary: "High consumer lag detected"
      description: "Consumer lag is {{ $value }} messages"

  - alert: "KafkaBrokerDown"
    expr: "up{job='kafka-jmx'} == 0"
    for: "1m"
    labels:
      severity: "critical"
    annotations:
      summary: "Kafka broker is down"
      description: "Kafka broker {{ $labels.instance }} is not responding"

  - alert: "KafkaDiskSpaceLow"
    expr: "kafka_log_size_bytes / kafka_log_size_bytes_max > 0.8"
    for: "5m"
    labels:
      severity: "warning"
    annotations:
      summary: "Kafka disk space is low"
      description: "Disk usage is {{ $value }}% on {{ $labels.instance }}"
```

## 🔐 Безопасность (для продакшена)

### `kafka_security_setup.sh`
```bash
#!/bin/bash

# Настройка SSL/TLS для Kafka (для продакшена)

KAFKA_HOME="/opt/kafka"
SSL_DIR="/var/ssl/private"
PASSWORD="your_secure_password"

# Создание директории для SSL сертификатов
mkdir -p $SSL_DIR
cd $SSL_DIR

# Создание CA (Certificate Authority)
keytool -keystore kafka.server.truststore.jks \
    -alias CARoot \
    -import \
    -file ca-cert \
    -storepass $PASSWORD \
    -keypass $PASSWORD \
    -noprompt

# Создание keystore для каждого брокера
for i in 1 2 3; do
    # Создание keystore
    keytool -keystore kafka.server.keystore.jks \
        -alias localhost \
        -validity 365 \
        -genkey \
        -keyalg RSA \
        -storepass $PASSWORD \
        -keypass $PASSWORD \
        -dname "CN=kafka-$i, OU=IT, O=Company, L=City, S=State, C=US"
    
    # Создание Certificate Signing Request
    keytool -keystore kafka.server.keystore.jks \
        -alias localhost \
        -certreq \
        -file cert-file \
        -storepass $PASSWORD \
        -keypass $PASSWORD
    
    # Подписание сертификата CA
    keytool -keystore kafka.server.truststore.jks \
        -alias CARoot \
        -import \
        -file cert-file \
        -storepass $PASSWORD \
        -keypass $PASSWORD \
        -noprompt
done

echo "✅ SSL сертификаты созданы для всех брокеров"
```

### `server_ssl.properties`
```properties
# SSL конфигурация для продакшена
security.inter.broker.protocol=SSL
listeners=SSL://0.0.0.0:9093
advertised.listeners=SSL://kafka-1:29093
inter.broker.listener.name=SSL

# SSL настройки
ssl.keystore.location=/var/ssl/private/kafka.server.keystore.jks
ssl.keystore.password=your_secure_password
ssl.key.password=your_secure_password
ssl.truststore.location=/var/ssl/private/kafka.server.truststore.jks
ssl.truststore.password=your_secure_password
ssl.client.auth=required

# SASL настройки (дополнительно)
sasl.enabled.mechanisms=PLAIN
sasl.mechanism.inter.broker.protocol=PLAIN
listener.name.ssl.plain.sasl.jaas.config=org.apache.kafka.common.security.plain.PlainLoginModule required \
    username="admin" \
    password="admin-secret" \
    user_admin="admin-secret" \
    user_client="client-secret";
```

## 📊 JMX метрики

### `jmx_config.yml`
```yaml
# Конфигурация JMX метрик для Kafka

jmx_config:
  # Основные метрики производительности
  performance_metrics:
    - "kafka.server:type=BrokerTopicMetrics,name=MessagesInPerSec"
    - "kafka.server:type=BrokerTopicMetrics,name=MessagesOutPerSec"
    - "kafka.server:type=BrokerTopicMetrics,name=BytesInPerSec"
    - "kafka.server:type=BrokerTopicMetrics,name=BytesOutPerSec"
  
  # Метрики репликации
  replication_metrics:
    - "kafka.server:type=ReplicaManager,name=UnderReplicatedPartitions"
    - "kafka.server:type=ReplicaManager,name=IsrShrinksPerSec"
    - "kafka.server:type=ReplicaManager,name=IsrExpandsPerSec"
  
  # Метрики consumer groups
  consumer_metrics:
    - "kafka.consumer:type=consumer-fetch-manager-metrics,client-id=*"
    - "kafka.consumer:type=consumer-coordinator-metrics,client-id=*"
  
  # Метрики producer
  producer_metrics:
    - "kafka.producer:type=producer-metrics,client-id=*"
    - "kafka.producer:type=producer-topic-metrics,client-id=*,topic=*"
  
  # Системные метрики
  system_metrics:
    - "kafka.server:type=KafkaServer,name=BrokerState"
    - "kafka.server:type=ReplicaManager,name=LeaderCount"
    - "kafka.server:type=ReplicaManager,name=PartitionCount"
```

## 🚀 Скрипты запуска

### `start_kafka_cluster.sh`
```bash
#!/bin/bash

echo "🚀 Запуск Kafka кластера"

# Проверка доступности портов
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
        echo "❌ Порт $port уже занят"
        exit 1
    fi
}

# Проверяем порты
check_port 2181
check_port 2182
check_port 2183
check_port 9092
check_port 9093
check_port 9094
check_port 8080
check_port 8081

echo "✅ Все порты свободны"

# Запускаем кластер
docker-compose -f docker-compose.kafka.yml up -d

# Ждем запуска
echo "⏳ Ожидание запуска кластера..."
sleep 30

# Проверяем статус
echo "📊 Статус сервисов:"
docker-compose -f docker-compose.kafka.yml ps

# Создаем топики
echo "📝 Создание топиков..."
./create_topics.sh

echo "🎉 Kafka кластер запущен и готов к работе!"
echo "📱 Kafka UI доступен по адресу: http://localhost:8080"
echo "📊 Schema Registry доступен по адресу: http://localhost:8081"
```

### `stop_kafka_cluster.sh`
```bash
#!/bin/bash

echo "🛑 Остановка Kafka кластера"

# Останавливаем сервисы
docker-compose -f docker-compose.kafka.yml down

# Удаляем volumes (опционально)
read -p "Удалить данные (volumes)? [y/N]: " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker-compose -f docker-compose.kafka.yml down -v
    echo "🗑️ Данные удалены"
fi

echo "✅ Kafka кластер остановлен"
```

## 📋 Переменные окружения

### `.env.kafka`
```bash
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092,localhost:9093,localhost:9094
KAFKA_SECURITY_PROTOCOL=PLAINTEXT
KAFKA_SASL_MECHANISM=PLAIN
KAFKA_SASL_USERNAME=
KAFKA_SASL_PASSWORD=

# Producer Configuration
KAFKA_PRODUCER_ACKS=all
KAFKA_PRODUCER_RETRIES=3
KAFKA_PRODUCER_BATCH_SIZE=16384
KAFKA_PRODUCER_LINGER_MS=10
KAFKA_PRODUCER_COMPRESSION_TYPE=snappy

# Consumer Configuration
KAFKA_CONSUMER_GROUP_ID=agregator-service
KAFKA_CONSUMER_AUTO_OFFSET_RESET=earliest
KAFKA_CONSUMER_ENABLE_AUTO_COMMIT=true
KAFKA_CONSUMER_AUTO_COMMIT_INTERVAL_MS=1000
KAFKA_CONSUMER_MAX_POLL_RECORDS=500

# Topics Configuration
KAFKA_REQUEST_EVENTS_PARTITIONS=6
KAFKA_WORKFLOW_EVENTS_PARTITIONS=3
KAFKA_NOTIFICATION_EVENTS_PARTITIONS=3
KAFKA_SECURITY_EVENTS_PARTITIONS=3
KAFKA_HR_EVENTS_PARTITIONS=3
KAFKA_AUDIT_EVENTS_PARTITIONS=6

# Monitoring
KAFKA_JMX_PORT=9999
KAFKA_LOG_LEVEL=INFO
```

