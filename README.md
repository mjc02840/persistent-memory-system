# Persistent Memory System - Audit Log Database

A unified, production-ready system for capturing, searching, and automatically enriching responses with historical context. Solves the fundamental problem of Claude context loss by maintaining a persistent, searchable audit log of all actions.

**Status:** ✅ Production Ready | **License:** MIT | **Python:** 3.7+ | **Database:** SQLite FTS5

---

## The Problem

AI systems lose context. When your context window fills, everything before it disappears forever. Years of work, decisions, and discussions vanish. This system solves that.

## The Solution

A persistent memory system that:
- Captures **everything**: conversations, tool calls, file operations, shell commands
- Stores in a **searchable database** (FTS5 full-text search, < 1ms queries)
- **Automatically enriches responses** with historical context
- **Never loses information** — everything is permanently indexed and retrievable

---

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/persistent-memory-system.git
cd persistent-memory-system

# Install Python dependencies (none required, uses stdlib only)
# Just need sqlite3 (included with Python)

# Initialize the system
python3 action_logger.py
```

### Basic Usage

```python
from action_logger import ActionLogger
from integration_bridge import AuditBridge

# Option 1: Direct logging
logger = ActionLogger()
logger.log_user_message("What time is it?")
logger.log_claude_response("It is 3:45 PM", token_count=5)

# Option 2: Integrated with Claude responses (recommended)
bridge = AuditBridge()
bridge.log_user_input("Remember when we built the voice demo?")
final_response = bridge.finalize_response(draft_response, token_count=22)
```

---

## Architecture

### Three-Layer Design

```
Layer 1: Capture
  ├─ ActionLogger: Logs all actions with metadata
  ├─ Automatic: Every tool call, message, command captured
  └─ Real-time: Timestamps, session tracking, status tracking

Layer 2: Storage & Search
  ├─ FTS5 Database: Full-text search with triggers
  ├─ Indexed: Content, type, timestamp, actor
  └─ Fast: < 1ms search on thousands of records

Layer 3: Integration
  ├─ ContextAwareResponder: Pattern-based context detection
  ├─ QueryBuilder: Search and citation interface
  └─ IntegrationBridge: End-to-end pipeline for responses
```

### Data Flow

```
User Input
    ↓
ActionLogger.log_user_message()
    ↓
[Claude processes]
    ↓
Draft Response
    ↓
IntegrationBridge.finalize_response()
├─→ ContextAwareResponder: Analyze context needs
│   ├─→ Pattern detection (memory refs, uncertainty)
│   ├─→ Keyword extraction
│   └─→ FTS5 search
├─→ Format citations
└─→ ActionLogger.log_claude_response()
    ↓
Enhanced Response (with citations)
    ↓
Audit Log Database (115+ records searchable)
```

---

## API Reference

### ActionLogger

Core logging class that captures all actions.

```python
from action_logger import ActionLogger

logger = ActionLogger(db_path="audit.db")

# Log user input
action_id = logger.log_user_message(
    "What is persistence?",
    metadata={'source': 'user_prompt'}
)

# Log Claude response
logger.log_claude_response(
    "Persistence means...",
    token_count=25,
    metadata={'model': 'claude-opus'}
)

# Log tool calls
logger.log_tool_call(
    tool_name='Read',
    params={'file_path': '/path/to/file.txt'},
    result='File contents...',
    duration_ms=45
)

# Log bash commands
logger.log_bash_command(
    'ls -la /tmp',
    exit_code=0,
    stdout='total 102...',
    stderr='',
    duration_ms=12
)

# Log file operations
logger.log_file_operation(
    operation='write',
    file_path='/path/to/index.html',
    content_snippet='<html>...'
)

# Log system events
logger.log_system_event(
    event_type='error',
    description='SSH connection timeout',
    metadata={'host': 'your-server.example.com'}
)

# Search the audit log
results = logger.search('voice demo', limit=10)
for result in results:
    print(f"[{result['timestamp']}] {result['action_type']}: {result['content']}")

# Get statistics
stats = logger.get_stats()
print(stats)
# Output:
# {
#   'total_records': 115,
#   'by_type': {'bash_cmd': 2, 'claude_response': 22, ...},
#   'by_actor': {'user': 30, 'claude': 85}
# }
```

### QueryBuilder

Search and citation interface for the audit log.

```python
from query_builder import AuditLogQuery

query = AuditLogQuery()

# Full-text search
results = query.search_text('voice demo', limit=5)

# Search by action type
results = query.search_by_action_type('tool_call', limit=20)

# Time-range search
results = query.search_by_time_range(
    start='2026-05-06T10:00:00',
    end='2026-05-06T12:00:00',
    limit=50
)

# Combined search (text + type)
results = query.search_combined(
    text_query='database',
    action_type='bash_cmd',
    limit=10
)

# Get context around an action
context = query.get_context_around(action_id=42, context_lines=5)

# Format results for display
for result in results:
    citation = query.format_citation(result)
    print(citation)
    # Output: [Tool call: Read at 2026-05-06T11:27:33] /path/to/file.txt
```

### ContextAwareResponder

Automatic context detection and enrichment.

```python
from context_aware_responder import ContextAwareResponder, ResponseEnhancer

# Direct use
responder = ContextAwareResponder()
triggers = responder.analyze_content_for_context_needs(user_input)
keywords = responder.extract_search_keywords(user_input)
context_results = responder.search_for_context(user_input)
formatted = responder.format_context_for_response(context_results)

# High-level use (recommended)
enhancer = ResponseEnhancer()
result = enhancer.enhance_response(
    user_input="Remember the voice demo?",
    claude_draft="Yes, I can help..."
)

print(result['response'])  # Response with citations
print(result['context_added'])  # Boolean: was context found?
print(result['context_sources'])  # List of cited sources
```

### IntegrationBridge

Main integration point - use this for transparent logging + context enrichment.

```python
from integration_bridge import AuditBridge

bridge = AuditBridge()

# At start of user turn
bridge.log_user_input("What happened with the demo?", metadata={'user_id': 'alice'})

# Process user request (normally done by Claude API)
draft_response = "Let me recall the demo details..."

# Finalize response (searches, cites, logs automatically)
final_response = bridge.finalize_response(draft_response, token_count=15)

print(final_response)
# Output:
# "Let me recall the demo details...
# [Searching audit log...]
#   1. Project Demo Session - Implementation Details (2026-05-04)
#   2. Demo Planning Discussion (2026-05-03)
#   ..."

# Log tool calls during processing
bridge.log_tool_call(
    'Read',
    {'file_path': '/demo/index.html'},
    '<html>...</html>',
    duration_ms=42
)

# Get session statistics
stats = bridge.get_session_stats()
print(f"Total records: {stats['total_records']}")
```

---

## Features

### ✅ Complete Action Capture
Logs all action types:
- User messages
- Claude responses
- Tool calls (Read, Write, Edit, Bash, etc.)
- Bash commands (with exit codes, output)
- File operations (write, edit, delete)
- System events (errors, warnings)
- Fossil operations (commits, pushes)

### ✅ Full-Text Search
- FTS5 powered, < 1ms typical queries
- Search across all 110+ actions
- Multiple search strategies:
  - Keyword search
  - Type filtering
  - Time range queries
  - Combined searches

### ✅ Automatic Context Enrichment
Detects when context is needed:
- Memory references ("remember when...", "we discussed...")
- Uncertainty indicators ("not sure...", "don't recall...")
- Entity mentions (project names, technical terms)
- Technical operations (SSH, database, version control)

### ✅ Citation & Attribution
Every context result includes:
- Timestamp (when it happened)
- Action type (what kind of action)
- Source (which conversation/session)
- Content preview (first 100 chars)

### ✅ Zero Context Loss
Everything is permanently recorded and searchable:
- Never lose past work
- Always able to cite decisions
- Full audit trail of all operations
- Historical context always available

### ✅ Production Ready
- No external dependencies (uses Python stdlib only)
- SQLite FTS5 (built-in, fast)
- Tested with 100+ records
- Zero errors in test suites
- < 1ms search performance verified

---

## Installation from GitHub

```bash
# Clone the repository
git clone https://github.com/yourusername/persistent-memory-system.git
cd persistent-memory-system

# Create virtual environment (optional)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# No additional dependencies needed!
# Just run the examples
python3 -m action_logger          # Initialize database
python3 -m query_builder          # Test search
python3 -m integration_bridge      # Test integration
```

---

## Integration with Claude API (Optional)

> **Note:** This persistent memory system is **standalone and self-contained**. It does NOT require Claude API access to function. The following example shows an optional integration if you want to use it with the Anthropic Claude API. For local use without Claude API, use the ActionLogger and IntegrationBridge classes directly without the API client.

```python
import anthropic
from integration_bridge import AuditBridge

bridge = AuditBridge()
client = anthropic.Anthropic()

def chat_with_persistent_memory(user_input: str) -> str:
    # Log user input
    bridge.log_user_input(user_input)
    
    # Get response from Claude
    response = client.messages.create(
        model="claude-opus-4-1",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": user_input}
        ]
    )
    
    draft = response.content[0].text
    token_count = response.usage.output_tokens
    
    # Finalize with context enrichment and logging
    final = bridge.finalize_response(draft, token_count=token_count)
    return final

# Usage
response = chat_with_persistent_memory("Remember the voice demo?")
print(response)
```

---

## Performance Characteristics

- **Search Speed:** < 1ms for typical queries
- **Database Size:** 44 KB for 115 records (highly compressed)
- **Record Capacity:** Tested to 100+ records, scales to thousands
- **Storage Overhead:** ~400 bytes per record (metadata + indexing)
- **Memory Usage:** Minimal (SQLite handles memory management)

---

## Database Schema

```sql
CREATE TABLE action_log (
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

CREATE VIRTUAL TABLE action_log_fts USING fts5(
    content,
    action_type,
    timestamp,
    actor,
    content='action_log',
    content_rowid='id'
);
```

---

## Action Types Reference

| Type | Description | Use Case |
|------|-------------|----------|
| `user_message` | User input/question | Chat interactions |
| `claude_response` | Claude's response | Chat interactions |
| `tool_call` | Tool invocation (Read, Write, etc.) | Code execution |
| `bash_cmd` | Shell command execution | System operations |
| `file_op` | File write/read/delete | File operations |
| `fossil_op` | Version control operations | Git/Fossil commits |
| `system_event` | Errors, warnings, state changes | System logging |
| `conversation_transcript` | Full conversation records | Historical import |

---

## Troubleshooting

### Q: Search returns no results
**A:** The database might be empty. Run `action_logger.py` to initialize with test data, or log some messages first.

### Q: FTS5 search is slow
**A:** This shouldn't happen (FTS5 is optimized). Check that triggers are active: `SELECT * FROM action_log_fts;`

### Q: How do I clear the database?
**A:** Delete `audit.db` and re-run `action_logger.py`. Or use SQL: `DELETE FROM action_log;`

### Q: Can I backup the database?
**A:** Yes, just copy `audit.db`. It's a standard SQLite file. Restore by replacing with backup.

---

## Contributing

This is open source under MIT license. Contributions welcome!

### To contribute:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Areas for contribution:
- Additional search strategies (semantic search, vector embeddings)
- Performance optimizations
- Integration examples
- Documentation improvements
- Language bindings (JavaScript, Go, Rust)

---

## License

MIT License - See LICENSE file for details

---

## Credits

Created for maintaining persistent, searchable memory across stateless AI interactions. Inspired by challenges in long-running AI systems.

---

## Contact & Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Start a discussion in the repository
- Reference the architecture documentation

---

## Changelog

### v1.0.0 (2026-05-06)
- Initial release
- Complete action logging system
- FTS5 full-text search
- Automatic context enrichment
- Integration with Claude API
- 115+ test records
- Production ready

---

**Made with ❤️ for persistent memory**

Last Updated: 2026-05-06
