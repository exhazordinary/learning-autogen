-- Migration script to upgrade database schema to v2
-- Adds: token tracking, user authentication, performance indexes

-- Add user_id column to research_tasks (nullable for backward compatibility)
ALTER TABLE research_tasks ADD COLUMN IF NOT EXISTS user_id VARCHAR(100);

-- Add token tracking to agent_messages
ALTER TABLE agent_messages ADD COLUMN IF NOT EXISTS token_count INTEGER;

-- Add enhanced token tracking to task_metrics
ALTER TABLE task_metrics ADD COLUMN IF NOT EXISTS input_tokens INTEGER DEFAULT 0;
ALTER TABLE task_metrics ADD COLUMN IF NOT EXISTS output_tokens INTEGER DEFAULT 0;
ALTER TABLE task_metrics ADD COLUMN IF NOT EXISTS total_tokens INTEGER DEFAULT 0;
ALTER TABLE task_metrics ADD COLUMN IF NOT EXISTS estimated_cost REAL DEFAULT 0.0;

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_status_created ON research_tasks(status, created_at);
CREATE INDEX IF NOT EXISTS idx_user_created ON research_tasks(user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_task_order ON agent_messages(task_id, "order");

-- Note: For SQLite, the above commands should work.
-- For PostgreSQL, use DOUBLE PRECISION instead of REAL for estimated_cost:
-- ALTER TABLE task_metrics ADD COLUMN estimated_cost DOUBLE PRECISION DEFAULT 0.0;
