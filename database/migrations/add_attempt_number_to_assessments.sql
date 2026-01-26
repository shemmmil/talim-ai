-- Миграция: Добавление поля attempt_number в таблицу assessments
-- Выполните этот скрипт в SQL Editor в Supabase Dashboard

-- Добавляем поле attempt_number, если его еще нет
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'assessments' 
        AND column_name = 'attempt_number'
    ) THEN
        ALTER TABLE assessments 
        ADD COLUMN attempt_number INTEGER DEFAULT 1;
        
        -- Обновляем существующие записи: устанавливаем attempt_number = 1 для всех существующих assessments
        UPDATE assessments 
        SET attempt_number = 1 
        WHERE attempt_number IS NULL;
        
        -- Устанавливаем NOT NULL после обновления всех записей
        ALTER TABLE assessments 
        ALTER COLUMN attempt_number SET NOT NULL;
        
        RAISE NOTICE 'Column attempt_number added successfully';
    ELSE
        RAISE NOTICE 'Column attempt_number already exists';
    END IF;
END $$;

-- Создаем индекс для оптимизации запросов по user_id, direction_id, technology_id
CREATE INDEX IF NOT EXISTS idx_assessments_user_direction_technology 
ON assessments(user_id, direction_id, technology_id);
