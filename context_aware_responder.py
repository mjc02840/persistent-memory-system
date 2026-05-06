#!/usr/bin/env python3
"""
Context-Aware Responder
Automatically searches audit log when generating responses
Integrates historical context seamlessly into conversation flow
"""

import re
from typing import Optional, List, Dict, Tuple
from query_builder import AuditLogQuery
from datetime import datetime

class ContextAwareResponder:
    def __init__(self, db_path: str = "audit.db"):
        self.query = AuditLogQuery(db_path)
        self.context_threshold = 0.3  # Confidence threshold for auto-searching
        self.recent_searches = []  # Track what we've searched for

    def analyze_content_for_context_needs(self, text: str) -> List[str]:
        """
        Analyze text to identify what context might be needed
        Looks for:
        - References to past work ("remember when...", "we discussed...")
        - Uncertain phrases ("I'm not sure...", "I don't recall...")
        - Project/feature names that might need historical context
        - Technical terms that appeared in historical sessions

        Returns:
            List of search queries to execute
        """
        context_triggers = []

        # Trigger 1: Explicit memory references
        memory_patterns = [
            r"remember when",
            r"we discussed",
            r"earlier.*said",
            r"previously",
            r"last.*session",
            r"was working on",
            r"did we.*before",
        ]
        for pattern in memory_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                context_triggers.append("memory_reference")
                break

        # Trigger 2: Uncertainty indicators
        uncertainty_patterns = [
            r"i.*not.*sure",
            r"i.*don't.*know",
            r"i.*can't.*remember",
            r"what.*was",
            r"where.*did",
        ]
        for pattern in uncertainty_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                context_triggers.append("uncertainty")
                break

        # Trigger 3: Project/feature names that need context
        known_entities = ['quintrix', 'demo', 'voice', 'database', 'persistence', 'syncthing', 'fossil', 'vps']
        for entity in known_entities:
            if entity.lower() in text.lower():
                context_triggers.append(f"entity_{entity}")

        # Trigger 4: Technical operations that might have history
        operation_patterns = [
            (r"ssh|connect.*vps", "ssh_operations"),
            (r"git|fossil|commit|branch", "version_control"),
            (r"database|sql|query", "database_operations"),
            (r"api|endpoint|request", "api_operations"),
        ]
        for pattern, trigger_name in operation_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                context_triggers.append(trigger_name)
                break

        return list(set(context_triggers))  # Remove duplicates

    def extract_search_keywords(self, text: str) -> List[str]:
        """
        Extract keyword suggestions from text for searching audit log

        Returns:
            List of search keywords
        """
        keywords = []

        # Extract quoted phrases
        quoted = re.findall(r'"([^"]+)"', text)
        keywords.extend(quoted)

        # Extract project identifiers (e.g., PROJECT-001, PROJ-123)
        projects = re.findall(r'\b([A-Z]+-\d+|[A-Z]{2,}\d+)\b', text)
        keywords.extend(projects)

        # Extract common technical terms
        tech_terms = re.findall(r'\b(voice|demo|database|api|database|persistence|memory|audit)\b', text, re.IGNORECASE)
        keywords.extend(tech_terms)

        return list(set(keywords))

    def search_for_context(self, user_input: str, search_keywords: Optional[List[str]] = None) -> List[Dict]:
        """
        Search audit log for relevant context

        Args:
            user_input: User's message/query
            search_keywords: Explicit keywords to search for

        Returns:
            List of relevant historical results
        """
        if not search_keywords:
            search_keywords = self.extract_search_keywords(user_input)

        if not search_keywords:
            return []

        all_results = []

        # Search for each keyword
        for keyword in search_keywords[:3]:  # Limit to top 3 to avoid overwhelming results
            try:
                results = self.query.search_text(keyword, limit=3)
                all_results.extend(results)
            except:
                pass

        # Deduplicate by ID
        seen_ids = set()
        unique_results = []
        for result in all_results:
            if result['id'] not in seen_ids:
                unique_results.append(result)
                seen_ids.add(result['id'])

        return unique_results[:5]  # Top 5 results

    def format_context_for_response(self, results: List[Dict], context_type: str = "search") -> str:
        """
        Format search results for inclusion in response

        Args:
            results: Search results from audit log
            context_type: Type of context (search, memory, reference)

        Returns:
            Formatted context string for response
        """
        if not results:
            return ""

        lines = []

        if context_type == "search":
            lines.append("\n**[Searching audit log for context...]**")
        elif context_type == "memory":
            lines.append("\n**[Found in memory...]**")
        elif context_type == "reference":
            lines.append("\n**[Related historical context...]**")

        for i, result in enumerate(results, 1):
            citation = self.query.format_citation(result)
            lines.append(f"  {i}. {citation}")

        return '\n'.join(lines)

    def should_search_context(self, text: str) -> bool:
        """
        Decide if we should search for context before responding

        Uses heuristics:
        - Explicit memory references (high confidence)
        - Uncertainty indicators (medium confidence)
        - Entity mentions (low confidence, only if recent)

        Returns:
            True if we should search
        """
        triggers = self.analyze_content_for_context_needs(text)

        # High confidence triggers
        high_confidence = ['memory_reference', 'uncertainty']
        if any(trigger in high_confidence for trigger in triggers):
            return True

        # Medium confidence: only search for entities if they're mentioned multiple times
        entity_mentions = sum(1 for t in triggers if t.startswith('entity_'))
        if entity_mentions >= 2:
            return True

        return False

    def create_context_aware_response(self, user_input: str, draft_response: str) -> Tuple[str, List[Dict]]:
        """
        Take a draft response and enhance it with historical context if needed

        Args:
            user_input: User's original input
            draft_response: Initial response draft

        Returns:
            Tuple of (enhanced_response, context_results)
        """
        context_results = []

        # Decide if we should search
        if self.should_search_context(user_input):
            # Search for relevant context
            context_results = self.search_for_context(user_input)

            # If we found something, add it to response
            if context_results:
                context_block = self.format_context_for_response(context_results, "search")
                enhanced = draft_response + context_block
                return enhanced, context_results

        return draft_response, context_results


class ResponseEnhancer:
    """
    High-level interface for enhancing responses with audit log context
    This is what gets called from the actual response generation pipeline
    """

    def __init__(self, db_path: str = "audit.db"):
        self.responder = ContextAwareResponder(db_path)
        self.query = AuditLogQuery(db_path)

    def enhance_response(self, user_input: str, claude_draft: str) -> Dict:
        """
        Main entry point: enhance a Claude response with audit log context

        Args:
            user_input: What the user asked
            claude_draft: Draft response from Claude

        Returns:
            Dictionary with:
            - 'response': Enhanced response text
            - 'context_added': Boolean, was context added?
            - 'context_sources': List of cited sources
            - 'search_executed': List of searches performed
        """
        enhanced, context_results = self.responder.create_context_aware_response(user_input, claude_draft)

        return {
            'response': enhanced,
            'context_added': len(context_results) > 0,
            'context_sources': context_results,
            'search_executed': self.responder.extract_search_keywords(user_input),
            'timestamp': datetime.now().isoformat()
        }

    def search_and_cite(self, query: str) -> str:
        """
        Simple search and cite interface
        User: "What did we do with voice demo last time?"
        System: searches for 'voice demo', returns citations
        """
        results = self.responder.search_for_context(query)

        if not results:
            return f"No results found for '{query}' in audit log."

        return self.responder.format_context_for_response(results, "search")


if __name__ == '__main__':
    # Test the context-aware responder
    enhancer = ResponseEnhancer()

    print("=== CONTEXT-AWARE RESPONSE ENHANCEMENT TEST ===\n")

    # Test 1: Response with memory reference
    print("Test 1: User mentions past voice work")
    user_input = "Remember when we discussed the voice demo architecture?"
    draft = "Yes, I can help you with that."
    result = enhancer.enhance_response(user_input, draft)
    print(f"User: {user_input}")
    print(f"Enhanced Response:\n{result['response']}")
    print(f"Context Added: {result['context_added']}")
    if result['context_sources']:
        print(f"Sources: {len(result['context_sources'])} found")
    print()

    # Test 2: Direct search
    print("Test 2: Direct search for 'database design'")
    citations = enhancer.search_and_cite("database design")
    print(citations)
    print()

    # Test 3: Uncertainty trigger
    print("Test 3: User expresses uncertainty")
    user_input = "I'm not sure how we set up the persistence system last time"
    draft = "Let me help you recall the details."
    result = enhancer.enhance_response(user_input, draft)
    print(f"User: {user_input}")
    print(f"Enhanced Response:\n{result['response']}")
    print(f"Context Added: {result['context_added']}")
    print()

    print("✅ Context-aware responder ready for integration")
