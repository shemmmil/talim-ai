-- SQL схема для Supabase PostgreSQL
-- Выполните этот скрипт в SQL Editor в Supabase Dashboard

-- Включение расширения для UUID
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Таблица: users
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  email VARCHAR(255) UNIQUE NOT NULL,
  full_name VARCHAR(255),
  profile_picture_url TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  last_login TIMESTAMP
);

-- Таблица: roles
CREATE TABLE IF NOT EXISTS roles (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  name VARCHAR(255) NOT NULL,
  description TEXT,
  category VARCHAR(100),
  level VARCHAR(50),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Таблица: user_roles (связь many-to-many)
CREATE TABLE IF NOT EXISTS user_roles (
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
  PRIMARY KEY (user_id, role_id)
);

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

-- Таблица: competencies
CREATE TABLE IF NOT EXISTS competencies (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  category VARCHAR(100),
  importance_weight INTEGER CHECK (importance_weight BETWEEN 1 AND 5),
  order_index INTEGER,
  created_at TIMESTAMP DEFAULT NOW()
);

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

-- Таблица: direction_competencies (связь направлений и компетенций - общие компетенции)
CREATE TABLE IF NOT EXISTS direction_competencies (
  direction_id UUID REFERENCES directions(id) ON DELETE CASCADE,
  competency_id UUID REFERENCES competencies(id) ON DELETE CASCADE,
  order_index INTEGER,
  PRIMARY KEY (direction_id, competency_id)
);

-- Таблица: technology_competencies (связь технологий и компетенций - специфичные компетенции)
CREATE TABLE IF NOT EXISTS technology_competencies (
  technology_id UUID REFERENCES technologies(id) ON DELETE CASCADE,
  competency_id UUID REFERENCES competencies(id) ON DELETE CASCADE,
  order_index INTEGER,
  PRIMARY KEY (technology_id, competency_id)
);

-- Таблица: assessments
CREATE TABLE IF NOT EXISTS assessments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  role_id UUID REFERENCES roles(id),
  direction_id UUID REFERENCES directions(id),
  technology_id UUID REFERENCES technologies(id),
  status VARCHAR(50) CHECK (status IN ('in_progress', 'completed', 'abandoned')),
  overall_score FLOAT,
  attempt_number INTEGER DEFAULT 1,
  started_at TIMESTAMP DEFAULT NOW(),
  completed_at TIMESTAMP
);

-- Таблица: competency_assessments
CREATE TABLE IF NOT EXISTS competency_assessments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  assessment_id UUID REFERENCES assessments(id) ON DELETE CASCADE,
  competency_id UUID REFERENCES competencies(id),
  ai_assessed_score INTEGER CHECK (ai_assessed_score BETWEEN 1 AND 5),
  confidence_level VARCHAR(20) CHECK (confidence_level IN ('low', 'medium', 'high')),
  gap_analysis JSONB,
  test_session_data JSONB,
  completed_at TIMESTAMP
);

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

-- Таблица: question_history
CREATE TABLE IF NOT EXISTS question_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  competency_assessment_id UUID REFERENCES competency_assessments(id) ON DELETE CASCADE,
  question_id UUID REFERENCES questions(id) ON DELETE SET NULL,
  question_text TEXT NOT NULL,
  question_type VARCHAR(50),
  difficulty_level INTEGER CHECK (difficulty_level BETWEEN 1 AND 5),
  user_answer_transcript TEXT,
  audio_duration_seconds INTEGER,
  transcription_confidence FLOAT,
  is_correct BOOLEAN,
  ai_evaluation JSONB,
  time_spent_seconds INTEGER,
  asked_at TIMESTAMP DEFAULT NOW(),
  answered_at TIMESTAMP
);


-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_directions_name ON directions(name);
CREATE INDEX IF NOT EXISTS idx_technologies_name ON technologies(name);
CREATE INDEX IF NOT EXISTS idx_direction_technologies_direction_id ON direction_technologies(direction_id);
CREATE INDEX IF NOT EXISTS idx_direction_technologies_technology_id ON direction_technologies(technology_id);
CREATE INDEX IF NOT EXISTS idx_direction_competencies_direction_id ON direction_competencies(direction_id);
CREATE INDEX IF NOT EXISTS idx_direction_competencies_competency_id ON direction_competencies(competency_id);
CREATE INDEX IF NOT EXISTS idx_technology_competencies_technology_id ON technology_competencies(technology_id);
CREATE INDEX IF NOT EXISTS idx_technology_competencies_competency_id ON technology_competencies(competency_id);
CREATE INDEX IF NOT EXISTS idx_assessments_user_id ON assessments(user_id);
CREATE INDEX IF NOT EXISTS idx_assessments_role_id ON assessments(role_id);
CREATE INDEX IF NOT EXISTS idx_assessments_direction_id ON assessments(direction_id);
CREATE INDEX IF NOT EXISTS idx_assessments_technology_id ON assessments(technology_id);
CREATE INDEX IF NOT EXISTS idx_competency_assessments_assessment_id ON competency_assessments(assessment_id);
CREATE INDEX IF NOT EXISTS idx_competency_assessments_competency_id ON competency_assessments(competency_id);
CREATE INDEX IF NOT EXISTS idx_questions_competency_id ON questions(competency_id);
CREATE INDEX IF NOT EXISTS idx_questions_competency_difficulty ON questions(competency_id, difficulty);
CREATE INDEX IF NOT EXISTS idx_question_history_competency_assessment_id ON question_history(competency_assessment_id);
CREATE INDEX IF NOT EXISTS idx_question_history_question_id ON question_history(question_id);
CREATE INDEX IF NOT EXISTS idx_assessments_user_direction_technology ON assessments(user_id, direction_id, technology_id);
