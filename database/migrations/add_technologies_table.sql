-- Миграция: Добавление таблиц для хранения технологий
-- Дата: 2024
-- Описание: Создает таблицы для хранения технологий (Go, PHP, Python и т.д.) и их связи с направлениями и компетенциями

-- Включение расширения для UUID (если еще не включено)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Таблица: technologies (технологии/стек)
CREATE TABLE IF NOT EXISTS technologies (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL UNIQUE,
  description TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Таблица: direction_technologies (связь направлений и технологий)
CREATE TABLE IF NOT EXISTS direction_technologies (
  direction_id UUID REFERENCES directions(id) ON DELETE CASCADE,
  technology_id UUID REFERENCES technologies(id) ON DELETE CASCADE,
  order_index INTEGER,
  PRIMARY KEY (direction_id, technology_id)
);

-- Таблица: technology_competencies (связь технологий и компетенций)
CREATE TABLE IF NOT EXISTS technology_competencies (
  technology_id UUID REFERENCES technologies(id) ON DELETE CASCADE,
  competency_id UUID REFERENCES competencies(id) ON DELETE CASCADE,
  order_index INTEGER,
  PRIMARY KEY (technology_id, competency_id)
);

-- Добавляем колонку technology_id в assessments
ALTER TABLE assessments 
ADD COLUMN IF NOT EXISTS technology_id UUID REFERENCES technologies(id);

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_technologies_name ON technologies(name);
CREATE INDEX IF NOT EXISTS idx_direction_technologies_direction_id ON direction_technologies(direction_id);
CREATE INDEX IF NOT EXISTS idx_direction_technologies_technology_id ON direction_technologies(technology_id);
CREATE INDEX IF NOT EXISTS idx_technology_competencies_technology_id ON technology_competencies(technology_id);
CREATE INDEX IF NOT EXISTS idx_technology_competencies_competency_id ON technology_competencies(competency_id);
CREATE INDEX IF NOT EXISTS idx_assessments_technology_id ON assessments(technology_id);
