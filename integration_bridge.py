#!/usr/bin/env python3
"""
Integration Bridge
Connects audit log context system to Claude response generation
This module logs ALL conversations and automatically enriches responses with context

Usage:
  from integration_bridge import AuditBridge

  bridge = AuditBridge()

  # Log user input
  bridge.log_user_input("What time is it?")

  # Generate response (this could be from Claude API)
  draft_response = "It is currently 3:45 PM."

  # Enhance with context and log
  final_response = bridge.finalize_response(draft_response)
"""

import time
from typing import Optional, Dict, Any
from action_logger import ActionLogger
from context_aware_responder import ResponseEnhancer
from datetime import datetime


class AuditBridge:
    """
    Main integration point between conversation flow and audit log system
    Handles:
    1. Logging all user inputs
    2. Enriching responses with historical context
    3. Logging all responses
    4. Tracking session metadata
    """

    def __init__(self, db_path: str = "audit.db"):
        self.logger = ActionLogger(db_path)
        self.enhancer = ResponseEnhancer(db_path)
        self.current_user_input = None
        self.current_draft_response = None
        self.start_time = None

    def log_user_input(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Log a user input message
        Called at the START of a user turn

        Args:
            text: User's message
            metadata: Optional metadata (source, user_id, etc.)

        Returns:
            action_id (for tracking)
        """
        self.current_user_input = text
        self.start_time = time.time()

        return self.logger.log_user_message(text, metadata=metadata)

    def enrich_response(self, draft_response: str) -> Dict:
        """
        Take a draft response and enrich it with audit log context
        This is where the "magic" happens

        Args:
            draft_response: Initial response from Claude (or wherever)

        Returns:
            Dictionary with enhancement results
        """
        if not self.current_user_input:
            return {
                'response': draft_response,
                'context_added': False,
                'error': 'No user input logged'
            }

        # Call the context enhancer
        result = self.enhancer.enhance_response(self.current_user_input, draft_response)

        self.current_draft_response = draft_response
        return result

    def finalize_response(self, draft_response: str, token_count: Optional[int] = None) -> str:
        """
        Finalize response: enrich it with context, then log it

        Args:
            draft_response: Initial response from Claude
            token_count: Optional token count from Claude API

        Returns:
            Final response (enriched with context if applicable)
        """
        # Enrich the response
        enrichment = self.enrich_response(draft_response)
        final_response = enrichment['response']

        # Calculate duration
        duration_ms = int((time.time() - self.start_time) * 1000) if self.start_time else None

        # Log the response
        metadata = {
            'context_added': enrichment['context_added'],
            'context_sources_count': len(enrichment.get('context_sources', [])),
            'searches_executed': enrichment.get('search_executed', []),
        }

        self.logger.log_claude_response(
            final_response,
            token_count=token_count,
            metadata=metadata
        )

        return final_response

    def log_tool_call(self, tool_name: str, params: Dict, result: str, duration_ms: int) -> int:
        """
        Log a tool call (Read, Write, Bash, etc.)

        Args:
            tool_name: Name of the tool (e.g., 'Bash', 'Read', 'Write')
            params: Parameters passed to the tool
            result: Result/output from the tool
            duration_ms: How long it took

        Returns:
            action_id
        """
        return self.logger.log_tool_call(tool_name, params, result, duration_ms)

    def get_session_stats(self) -> Dict:
        """Get statistics for current session"""
        return self.logger.get_stats()


def example_conversation_flow():
    """
    Example showing how the audit bridge integrates into a conversation
    This demonstrates the full flow: input → process → context search → output → log
    """
    print("=== EXAMPLE CONVERSATION FLOW ===\n")

    bridge = AuditBridge()

    # Turn 1: User asks about past work
    print("TURN 1: User asks about voice demo")
    print("-" * 50)
    user_msg = "Can you remind me about the voice demo architecture we discussed?"
    print(f"User: {user_msg}\n")

    bridge.log_user_input(user_msg)

    # Simulate Claude draft response (normally this comes from Claude API)
    draft = "I'd be happy to help. Let me recall the details of the voice demo architecture."

    # Finalize (this enriches with context and logs both input and response)
    final = bridge.finalize_response(draft, token_count=22)

    print(f"Final Response:\n{final}\n")

    # Turn 2: Tool call
    print("\nTURN 2: Claude calls a tool")
    print("-" * 50)
    user_msg2 = "Can you check the demo files we created?"
    print(f"User: {user_msg2}\n")

    bridge.log_user_input(user_msg2)

    # Simulate a tool call
    bridge.log_tool_call(
        tool_name='Read',
        params={'file_path': '/path/to/demo.html'},
        result='<html>...</html> (2.3KB)',
        duration_ms=45
    )

    draft2 = "I found the voice demo file. It contains the Web Speech API integration."
    final2 = bridge.finalize_response(draft2, token_count=18)

    print(f"Final Response:\n{final2}\n")

    # Show stats
    print("\nSESSION STATISTICS:")
    print("-" * 50)
    stats = bridge.get_session_stats()
    print(f"Total records logged: {stats['total_records']}")
    print(f"By type: {stats['by_type']}")


if __name__ == '__main__':
    example_conversation_flow()

    print("\n✅ Integration bridge ready for production use")
