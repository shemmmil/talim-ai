-- Миграция: Добавление таблицы questions для хранения предварительно сгенерированных вопросов
-- Дата: 2024
-- Описание: Создает таблицу для хранения вопросов, чтобы избежать дорогой генерации через OpenAI

-- Включение расширения для UUID (если еще не включено)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Таблица: questions (предварительно сгенерированные вопросы)
CREATE TABLE IF NOT EXISTS questions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  competency_id UUID REFERENCES competencies(id) ON DELETE CASCADE,
  question_text TEXT NOT NULL,
  difficulty INTEGER CHECK (difficulty BETWEEN 1 AND 5) NOT NULL,
  question_number INTEGER CHECK (question_number BETWEEN 1 AND 5),
  expected_key_points JSONB,
  estimated_answer_time VARCHAR(100),
  used_count INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Добавляем колонку question_id в question_history для связи с сохраненными вопросами
ALTER TABLE question_history 
ADD COLUMN IF NOT EXISTS question_id UUID REFERENCES questions(id) ON DELETE SET NULL;

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_questions_competency_id ON questions(competency_id);
CREATE INDEX IF NOT EXISTS idx_questions_competency_difficulty ON questions(competency_id, difficulty);
CREATE INDEX IF NOT EXISTS idx_question_history_question_id ON question_history(question_id);
