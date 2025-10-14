-- Инициализация базы данных для agregator-service

-- Создание расширений
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Создание таблиц будет выполнено через SQLAlchemy модели
-- Этот файл используется для дополнительных настроек

-- Создание индексов для оптимизации
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

CREATE INDEX IF NOT EXISTS idx_customer_profiles_user_id ON customer_profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_contractor_profiles_user_id ON contractor_profiles(user_id);

CREATE INDEX IF NOT EXISTS idx_repair_requests_customer_id ON repair_requests(customer_id);
CREATE INDEX IF NOT EXISTS idx_repair_requests_status ON repair_requests(status);
CREATE INDEX IF NOT EXISTS idx_repair_requests_created_at ON repair_requests(created_at);

CREATE INDEX IF NOT EXISTS idx_contractor_responses_request_id ON contractor_responses(request_id);
CREATE INDEX IF NOT EXISTS idx_contractor_responses_contractor_id ON contractor_responses(contractor_id);

CREATE INDEX IF NOT EXISTS idx_article_mappings_contractor_article ON article_mappings(contractor_article);
CREATE INDEX IF NOT EXISTS idx_article_mappings_agb_article ON article_mappings(agb_article);

CREATE INDEX IF NOT EXISTS idx_contractor_requests_request_number ON contractor_requests(request_number);
CREATE INDEX IF NOT EXISTS idx_contractor_requests_status ON contractor_requests(status);

CREATE INDEX IF NOT EXISTS idx_contractor_request_items_request_id ON contractor_request_items(request_id);
CREATE INDEX IF NOT EXISTS idx_contractor_request_items_contractor_article ON contractor_request_items(contractor_article);

CREATE INDEX IF NOT EXISTS idx_telegram_users_telegram_id ON telegram_users(telegram_id);
CREATE INDEX IF NOT EXISTS idx_telegram_users_user_id ON telegram_users(user_id);

-- Комментарии к таблицам
COMMENT ON TABLE users IS 'Пользователи системы агрегатора';
COMMENT ON TABLE customer_profiles IS 'Профили заказчиков (компании)';
COMMENT ON TABLE contractor_profiles IS 'Профили исполнителей (физлица)';
COMMENT ON TABLE repair_requests IS 'Заявки на ремонт и услуги';
COMMENT ON TABLE contractor_responses IS 'Отклики исполнителей на заявки';
COMMENT ON TABLE article_mappings IS 'Сопоставление артикулов';
COMMENT ON TABLE contractor_requests IS 'Заявки от контрагентов на сопоставление артикулов';
COMMENT ON TABLE contractor_request_items IS 'Позиции в заявках контрагентов';
COMMENT ON TABLE telegram_users IS 'Telegram пользователи для уведомлений';
