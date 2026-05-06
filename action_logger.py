#!/usr/bin/env python3
"""
Unified Action Logger for Persistent Memory System
Captures all actions: conversations, tool calls, file operations, system events
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any

class ActionLogger:
    def __init__(self, db_path: str = "audit.db"):
        self.db_path = db_path
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.conversation_id = None
        self.init_db()

    def init_db(self):
        """Initialize database with schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Read and execute schema
        schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
        with open(schema_path, 'r') as f:
            schema = f.read()

        cursor.executescript(schema)
        conn.commit()
        conn.close()

    def log_action(self,
                   action_type: str,
                   content: str,
                   actor: str = "claude",
                   metadata: Optional[Dict[str, Any]] = None,
                   result_status: str = "success",
                   duration_ms: Optional[int] = None) -> int:
        """
        Log an action to the audit log

        Args:
            action_type: Type of action (user_message, claude_response, tool_call, bash_cmd, file_op, fossil_op, system_event)
            content: The main content/text of the action
            actor: Who performed the action (user, claude, system)
            metadata: Additional structured data (JSON-serializable dict)
            result_status: success, error, pending
            duration_ms: How long the action took (milliseconds)

        Returns:
            action_id (primary key in database)
        """
        timestamp = datetime.now().isoformat()
        metadata_json = json.dumps(metadata) if metadata else None

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO action_log
            (timestamp, session_id, conversation_id, action_type, actor, content, metadata, result_status, duration_ms)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, self.session_id, self.conversation_id, action_type, actor, content, metadata_json, result_status, duration_ms))

        action_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return action_id

    def log_user_message(self, content: str, metadata: Optional[Dict] = None) -> int:
        """Log a user message"""
        return self.log_action("user_message", content, actor="user", metadata=metadata)

    def log_claude_response(self, content: str, token_count: Optional[int] = None, metadata: Optional[Dict] = None) -> int:
        """Log a Claude response"""
        if metadata is None:
            metadata = {}
        metadata['token_count'] = token_count
        return self.log_action("claude_response", content, actor="claude", metadata=metadata)

    def log_tool_call(self, tool_name: str, params: Dict, result: str, duration_ms: int, metadata: Optional[Dict] = None) -> int:
        """Log a tool call (Read, Write, Edit, Bash, etc.)"""
        if metadata is None:
            metadata = {}
        metadata['tool_name'] = tool_name
        metadata['params'] = params

        content = f"Tool: {tool_name} | Params: {json.dumps(params)}"
        return self.log_action("tool_call", content, metadata=metadata, duration_ms=duration_ms)

    def log_bash_command(self, command: str, exit_code: int, stdout: str, stderr: str, duration_ms: int, metadata: Optional[Dict] = None) -> int:
        """Log a bash command execution"""
        if metadata is None:
            metadata = {}
        metadata['command'] = command
        metadata['exit_code'] = exit_code
        metadata['stdout_lines'] = len(stdout.split('\n'))
        metadata['stderr'] = stderr if stderr else None

        result_status = "success" if exit_code == 0 else "error"
        content = f"Bash: {command}\nExit Code: {exit_code}\nOutput: {stdout[:200]}..."

        return self.log_action("bash_cmd", content, metadata=metadata, result_status=result_status, duration_ms=duration_ms)

    def log_file_operation(self, operation: str, file_path: str, content_snippet: Optional[str] = None, metadata: Optional[Dict] = None) -> int:
        """Log file operations (write, edit, read, delete)"""
        if metadata is None:
            metadata = {}
        metadata['operation'] = operation
        metadata['file_path'] = file_path

        content = f"File Op: {operation} | Path: {file_path}"
        if content_snippet:
            content += f"\nContent: {content_snippet[:200]}..."

        return self.log_action("file_op", content, metadata=metadata)

    def log_fossil_operation(self, operation: str, commit_msg: Optional[str] = None, files_changed: Optional[list] = None, metadata: Optional[Dict] = None) -> int:
        """Log fossil operations (commit, push, pull)"""
        if metadata is None:
            metadata = {}
        metadata['operation'] = operation
        metadata['files_changed'] = files_changed

        content = f"Fossil: {operation}\nMessage: {commit_msg}"
        return self.log_action("fossil_op", content, metadata=metadata)

    def log_system_event(self, event_type: str, description: str, metadata: Optional[Dict] = None) -> int:
        """Log system events (errors, warnings, state changes)"""
        return self.log_action("system_event", description, actor="system", metadata=metadata)

    def search(self, query: str, limit: int = 10) -> list:
        """
        Search the audit log using FTS5

        Args:
            query: Search query (FTS5 syntax)
            limit: Maximum number of results

        Returns:
            List of matching actions with metadata
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT a.id, a.timestamp, a.action_type, a.actor, a.content, a.metadata
            FROM action_log a
            JOIN action_log_fts fts ON a.id = fts.rowid
            WHERE action_log_fts MATCH ?
            ORDER BY a.timestamp DESC
            LIMIT ?
        """, (query, limit))

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return results

    def get_recent_actions(self, action_type: Optional[str] = None, limit: int = 20) -> list:
        """Get recent actions, optionally filtered by type"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if action_type:
            cursor.execute("""
                SELECT id, timestamp, action_type, actor, content, metadata
                FROM action_log
                WHERE action_type = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (action_type, limit))
        else:
            cursor.execute("""
                SELECT id, timestamp, action_type, actor, content, metadata
                FROM action_log
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()

        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the audit log"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM action_log")
        total_records = cursor.fetchone()[0]

        cursor.execute("""
            SELECT action_type, COUNT(*) as count
            FROM action_log
            GROUP BY action_type
        """)
        type_breakdown = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute("""
            SELECT actor, COUNT(*) as count
            FROM action_log
            GROUP BY actor
        """)
        actor_breakdown = {row[0]: row[1] for row in cursor.fetchall()}

        conn.close()

        return {
            'total_records': total_records,
            'by_type': type_breakdown,
            'by_actor': actor_breakdown
        }


if __name__ == "__main__":
    # Test the logger
    logger = ActionLogger()

    print("Testing ActionLogger...")

    # Log some test actions
    logger.log_user_message("What time is it?")
    logger.log_claude_response("It is currently 11:20 AM.", token_count=12)
    logger.log_tool_call("Bash", {"command": "date"}, "Tue May 6 11:20:00 UTC 2026", 150)
    logger.log_bash_command("ls -la", 0, "total 8\ndrwxr-sr-x 2 aaa www 4096", "", 45)
    logger.log_file_operation("write", "/tmp/test.txt", "Test content here")

    # Show stats
    stats = logger.get_stats()
    print(f"\nStats: {json.dumps(stats, indent=2)}")

    # Test search
    results = logger.search("test", limit=5)
    print(f"\nSearch results for 'test': {len(results)} matches")
    for r in results:
        print(f"  [{r['timestamp']}] {r['action_type']}: {r['content'][:60]}...")
