-- Миграция: Добавление таблиц для хранения направлений разработки
-- Дата: 2024
-- Описание: Создает таблицы для хранения направлений (Frontend, Backend и т.д.) и их связи с компетенциями

-- Включение расширения для UUID (если еще не включено)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Таблица: directions (направления разработки)
CREATE TABLE IF NOT EXISTS directions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL UNIQUE,
  description TEXT,
  technologies TEXT,  -- Например: "React|Vue" или "Go, PHP"
  display_name VARCHAR(255),  -- Отображаемое название, например "Frontend(React|Vue)"
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Таблица: direction_competencies (связь направлений и компетенций)
CREATE TABLE IF NOT EXISTS direction_competencies (
  direction_id UUID REFERENCES directions(id) ON DELETE CASCADE,
  competency_id UUID REFERENCES competencies(id) ON DELETE CASCADE,
  order_index INTEGER,
  PRIMARY KEY (direction_id, competency_id)
);

-- Добавляем колонку direction_id в assessments
ALTER TABLE assessments 
ADD COLUMN IF NOT EXISTS direction_id UUID REFERENCES directions(id);

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_directions_name ON directions(name);
CREATE INDEX IF NOT EXISTS idx_direction_competencies_direction_id ON direction_competencies(direction_id);
CREATE INDEX IF NOT EXISTS idx_direction_competencies_competency_id ON direction_competencies(competency_id);
CREATE INDEX IF NOT EXISTS idx_assessments_direction_id ON assessments(direction_id);

-- Примеры данных для направлений (опционально, можно добавить через API)
-- INSERT INTO directions (name, display_name, technologies, description) VALUES
-- ('frontend', 'Frontend', 'React|Vue|Angular', 'Frontend разработка'),
-- ('backend', 'Backend', 'Go|PHP|Python|Node.js', 'Backend разработка'),
-- ('fullstack', 'Fullstack', 'React|Node.js|PostgreSQL', 'Fullstack разработка'),
-- ('mobile', 'Mobile', 'React Native|Flutter|Swift|Kotlin', 'Мобильная разработка'),
-- ('devops', 'DevOps', 'Docker|Kubernetes|CI/CD', 'DevOps и инфраструктура');
