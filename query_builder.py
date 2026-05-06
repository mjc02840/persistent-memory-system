#!/usr/bin/env python3
"""
Query Builder and Citation Formatter
Provides high-level search interface for the audit log
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

class AuditLogQuery:
    def __init__(self, db_path: str = "audit.db"):
        self.db_path = db_path

    def search_text(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Full-text search across all action content

        Args:
            query: FTS5 search query (supports AND, OR, phrases, etc.)
            limit: Maximum results to return

        Returns:
            List of action records with relevance ranking
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                action_log.id,
                action_log.timestamp,
                action_log.action_type,
                action_log.actor,
                action_log.content,
                action_log.metadata
            FROM action_log_fts
            JOIN action_log ON action_log_fts.rowid = action_log.id
            WHERE action_log_fts MATCH ?
            ORDER BY action_log.timestamp DESC
            LIMIT ?
        """, (query, limit))

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def search_by_action_type(self, action_type: str, limit: int = 20) -> List[Dict]:
        """Search actions by type (user_message, tool_call, bash_cmd, etc.)"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, timestamp, action_type, actor, content, metadata
            FROM action_log
            WHERE action_type = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (action_type, limit))

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def search_by_time_range(self, start: str, end: str, limit: int = 50) -> List[Dict]:
        """
        Search for actions within a time range

        Args:
            start: ISO 8601 timestamp (e.g., "2026-05-06T10:00:00")
            end: ISO 8601 timestamp
            limit: Maximum results
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, timestamp, action_type, actor, content
            FROM action_log
            WHERE timestamp BETWEEN ? AND ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (start, end, limit))

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def search_combined(self, text_query: str, action_type: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """Search with both text and type filters"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if action_type:
            cursor.execute("""
                SELECT
                    action_log.id,
                    action_log.timestamp,
                    action_log.action_type,
                    action_log.actor,
                    action_log.content,
                    action_log.metadata
                FROM action_log_fts
                JOIN action_log ON action_log_fts.rowid = action_log.id
                WHERE action_log_fts MATCH ? AND action_log.action_type = ?
                ORDER BY action_log.timestamp DESC
                LIMIT ?
            """, (text_query, action_type, limit))
        else:
            cursor.execute("""
                SELECT
                    action_log.id,
                    action_log.timestamp,
                    action_log.action_type,
                    action_log.actor,
                    action_log.content,
                    action_log.metadata
                FROM action_log_fts
                JOIN action_log ON action_log_fts.rowid = action_log.id
                WHERE action_log_fts MATCH ?
                ORDER BY action_log.timestamp DESC
                LIMIT ?
            """, (text_query, limit))

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def get_context_around(self, action_id: int, context_lines: int = 5) -> List[Dict]:
        """Get actions before and after a specific action for context"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Get the timestamp of the target action
        cursor.execute("SELECT timestamp FROM action_log WHERE id = ?", (action_id,))
        target = cursor.fetchone()
        if not target:
            conn.close()
            return []

        timestamp = target['timestamp']

        # Get surrounding actions
        cursor.execute("""
            SELECT id, timestamp, action_type, actor, substr(content, 1, 80) as content
            FROM action_log
            WHERE timestamp BETWEEN datetime(?, '-1 seconds') AND datetime(?, '+1 seconds')
            ORDER BY timestamp
        """, (timestamp, timestamp))

        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results

    def format_citation(self, result: Dict) -> str:
        """
        Format a search result as a citation for inclusion in response

        Args:
            result: Result record from search

        Returns:
            Formatted citation string
        """
        action_id = result.get('id', '')
        timestamp = result.get('timestamp', '')[:19]  # Just date and time
        action_type = result.get('action_type', 'unknown')
        content_preview = result.get('content', '')[:100]

        # Extract metadata if present
        metadata = {}
        if result.get('metadata'):
            try:
                metadata = json.loads(result['metadata'])
            except:
                pass

        # Format based on action type
        if action_type == 'user_message':
            return f"[User message at {timestamp}] {content_preview}"
        elif action_type == 'claude_response':
            return f"[Claude response at {timestamp}] {content_preview}"
        elif action_type == 'tool_call':
            tool_name = metadata.get('tool_name', 'unknown')
            return f"[Tool call: {tool_name} at {timestamp}] {content_preview}"
        elif action_type == 'bash_cmd':
            cmd = metadata.get('command', content_preview)
            return f"[Bash command at {timestamp}] {cmd}"
        elif action_type == 'file_op':
            op = metadata.get('operation', '')
            path = metadata.get('file_path', '')
            return f"[File operation ({op}) at {timestamp}] {path}"
        else:
            return f"[{action_type} at {timestamp}] {content_preview}"

    def format_results(self, results: List[Dict], show_context: bool = True) -> str:
        """
        Format search results for display

        Args:
            results: List of search result records
            show_context: Whether to show surrounding actions

        Returns:
            Formatted string for display/citation
        """
        if not results:
            return "No results found."

        output = []
        output.append(f"Found {len(results)} matching result(s):\n")

        for i, result in enumerate(results, 1):
            citation = self.format_citation(result)
            output.append(f"{i}. {citation}")

            # Show additional metadata
            if result.get('metadata'):
                try:
                    metadata = json.loads(result['metadata'])
                    if 'conversation_name' in metadata:
                        output.append(f"   (from: {metadata['conversation_name']})")
                except:
                    pass

        return '\n'.join(output)


if __name__ == '__main__':
    # Test the query builder
    query = AuditLogQuery()

    print("=== QUERY BUILDER TEST ===\n")

    # Test 1: Text search
    print("Test 1: Search for 'voice'")
    results = query.search_text('voice', limit=3)
    print(query.format_results(results))

    # Test 2: Type search
    print("\nTest 2: Get all bash commands")
    results = query.search_by_action_type('bash_cmd', limit=5)
    for r in results:
        print(f"  [{r['timestamp'][:19]}] {r['action_type']}: {r['content'][:60]}...")

    # Test 3: Combined search
    print("\nTest 3: Search for 'demo' in conversation_transcript type only")
    results = query.search_combined('demo', action_type='conversation_transcript', limit=2)
    print(query.format_results(results))

    print("\n✅ Query builder ready for integration")
