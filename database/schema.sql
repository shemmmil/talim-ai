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

-- Таблица: assessments
CREATE TABLE IF NOT EXISTS assessments (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  role_id UUID REFERENCES roles(id),
  status VARCHAR(50) CHECK (status IN ('in_progress', 'completed', 'abandoned')),
  overall_score FLOAT,
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

-- Таблица: question_history
CREATE TABLE IF NOT EXISTS question_history (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  competency_assessment_id UUID REFERENCES competency_assessments(id) ON DELETE CASCADE,
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

-- Таблица: roadmaps
CREATE TABLE IF NOT EXISTS roadmaps (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  assessment_id UUID REFERENCES assessments(id) ON DELETE CASCADE,
  title VARCHAR(255),
  description TEXT,
  estimated_duration_weeks INTEGER,
  difficulty_level INTEGER,
  priority_order JSONB,
  generated_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  status VARCHAR(50) CHECK (status IN ('active', 'completed', 'abandoned'))
);

-- Таблица: roadmap_sections
CREATE TABLE IF NOT EXISTS roadmap_sections (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  roadmap_id UUID REFERENCES roadmaps(id) ON DELETE CASCADE,
  competency_id UUID REFERENCES competencies(id),
  title VARCHAR(255),
  description TEXT,
  order_index INTEGER,
  estimated_duration_hours INTEGER,
  status VARCHAR(50) CHECK (status IN ('not_started', 'in_progress', 'completed')),
  completed_at TIMESTAMP
);

-- Таблица: learning_materials
CREATE TABLE IF NOT EXISTS learning_materials (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  roadmap_section_id UUID REFERENCES roadmap_sections(id) ON DELETE CASCADE,
  type VARCHAR(50) CHECK (type IN ('article', 'video', 'book', 'course', 'documentation', 'tutorial')),
  title VARCHAR(255),
  description TEXT,
  url TEXT,
  author VARCHAR(255),
  duration_minutes INTEGER,
  difficulty VARCHAR(50),
  language VARCHAR(10),
  is_free BOOLEAN DEFAULT true,
  order_index INTEGER,
  rating FLOAT
);

-- Таблица: practice_tasks
CREATE TABLE IF NOT EXISTS practice_tasks (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  roadmap_section_id UUID REFERENCES roadmap_sections(id) ON DELETE CASCADE,
  title VARCHAR(255),
  description TEXT,
  task_type VARCHAR(50) CHECK (task_type IN ('coding', 'quiz', 'project', 'case_study')),
  difficulty INTEGER CHECK (difficulty BETWEEN 1 AND 5),
  estimated_time_minutes INTEGER,
  requirements JSONB,
  hints JSONB,
  solution_example TEXT,
  order_index INTEGER
);

-- Таблица: self_check_questions
CREATE TABLE IF NOT EXISTS self_check_questions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  roadmap_section_id UUID REFERENCES roadmap_sections(id) ON DELETE CASCADE,
  question_text TEXT,
  question_type VARCHAR(50),
  options JSONB,
  correct_answer TEXT,
  explanation TEXT,
  difficulty INTEGER CHECK (difficulty BETWEEN 1 AND 5),
  order_index INTEGER
);

-- Таблица: user_progress
CREATE TABLE IF NOT EXISTS user_progress (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  roadmap_section_id UUID REFERENCES roadmap_sections(id) ON DELETE CASCADE,
  status VARCHAR(50) CHECK (status IN ('not_started', 'in_progress', 'completed')),
  progress_percentage INTEGER CHECK (progress_percentage BETWEEN 0 AND 100),
  notes TEXT,
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  last_activity_at TIMESTAMP DEFAULT NOW()
);

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_assessments_user_id ON assessments(user_id);
CREATE INDEX IF NOT EXISTS idx_assessments_role_id ON assessments(role_id);
CREATE INDEX IF NOT EXISTS idx_competency_assessments_assessment_id ON competency_assessments(assessment_id);
CREATE INDEX IF NOT EXISTS idx_competency_assessments_competency_id ON competency_assessments(competency_id);
CREATE INDEX IF NOT EXISTS idx_question_history_competency_assessment_id ON question_history(competency_assessment_id);
CREATE INDEX IF NOT EXISTS idx_roadmaps_assessment_id ON roadmaps(assessment_id);
CREATE INDEX IF NOT EXISTS idx_roadmap_sections_roadmap_id ON roadmap_sections(roadmap_id);
CREATE INDEX IF NOT EXISTS idx_learning_materials_roadmap_section_id ON learning_materials(roadmap_section_id);
CREATE INDEX IF NOT EXISTS idx_practice_tasks_roadmap_section_id ON practice_tasks(roadmap_section_id);
CREATE INDEX IF NOT EXISTS idx_self_check_questions_roadmap_section_id ON self_check_questions(roadmap_section_id);
CREATE INDEX IF NOT EXISTS idx_user_progress_user_id ON user_progress(user_id);
