-- Unified Audit Log Schema
-- Captures all actions: conversations, tool calls, file operations, system events
-- Full-text searchable via FTS5

CREATE TABLE IF NOT EXISTS action_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    session_id TEXT NOT NULL,
    conversation_id TEXT,
    action_type TEXT NOT NULL,
    actor TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT,
    result_status TEXT,
    duration_ms INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Create FTS5 virtual table for full-text search
CREATE VIRTUAL TABLE IF NOT EXISTS action_log_fts USING fts5(
    content,
    action_type,
    timestamp,
    actor,
    content='action_log',
    content_rowid='id'
);

-- Create indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_action_log_timestamp ON action_log(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_action_log_session ON action_log(session_id);
CREATE INDEX IF NOT EXISTS idx_action_log_type ON action_log(action_type);
CREATE INDEX IF NOT EXISTS idx_action_log_actor ON action_log(actor);

-- Trigger to keep FTS5 index in sync with main table
CREATE TRIGGER IF NOT EXISTS action_log_insert AFTER INSERT ON action_log BEGIN
  INSERT INTO action_log_fts(rowid, content, action_type, timestamp, actor)
  VALUES (new.id, new.content, new.action_type, new.timestamp, new.actor);
END;

CREATE TRIGGER IF NOT EXISTS action_log_delete AFTER DELETE ON action_log BEGIN
  INSERT INTO action_log_fts(action_log_fts, rowid, content, action_type, timestamp, actor)
  VALUES('delete', old.id, old.content, old.action_type, old.timestamp, old.actor);
END;
