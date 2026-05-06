# Contributing to Persistent Memory System

Thank you for your interest in contributing! This project is open source under the MIT license and welcomes contributions from everyone.

---

## Code of Conduct

- Be respectful and inclusive
- Assume good intent
- Focus on the work, not the person
- Help others learn and grow

---

## How to Contribute

### Report a Bug

1. Check if the bug has already been reported (search Issues)
2. If not, create a new Issue with:
   - **Title:** Clear, concise description
   - **Environment:** Python version, OS, SQLite version
   - **Reproduction steps:** How to reproduce the bug
   - **Expected behavior:** What should happen
   - **Actual behavior:** What actually happened
   - **Error messages:** Full stack trace if applicable

### Suggest an Enhancement

1. Check if the enhancement has been discussed (search Issues/Discussions)
2. Create an Issue with:
   - **Title:** Feature name
   - **Description:** What and why
   - **Use case:** Why this is needed
   - **Proposed implementation:** How you'd approach it (optional)

### Submit a Pull Request

#### Prerequisites
- Fork the repository
- Clone your fork locally
- Create a feature branch: `git checkout -b feature/your-feature-name`

#### Before You Start
- Read the Architecture documentation
- Understand the three-layer design
- Check if your change affects multiple layers

#### Development Workflow

1. **Make your changes**
   ```bash
   # Edit files
   # Test locally
   python3 -m pytest
   ```

2. **Follow the code style**
   - PEP 8 compliant
   - Use meaningful variable names
   - Add docstrings to functions
   - Keep functions focused and small

3. **Add tests**
   - Write tests for new functionality
   - Ensure existing tests still pass
   - Aim for > 80% code coverage

4. **Document your changes**
   - Update README.md if user-facing
   - Update ARCHITECTURE.md if architecture changes
   - Add comments for complex logic

5. **Commit with clear messages**
   ```bash
   git add .
   git commit -m "Add feature: description of what and why"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Open a Pull Request**
   - Target the `main` branch
   - Fill out the PR template
   - Link related issues
   - Describe your changes

#### PR Checklist
- [ ] Code follows style guide
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No new warnings/errors
- [ ] Commits are clear and well-written

---

## Development Setup

### Clone and Install
```bash
git clone https://github.com/yourusername/persistent-memory-system.git
cd persistent-memory-system

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dev dependencies
pip install -e .[dev]
```

### Run Tests
```bash
pytest                    # Run all tests
pytest -v                # Verbose output
pytest --cov             # With coverage
pytest tests/test_specific.py  # Run specific test
```

### Code Quality
```bash
black .                  # Format code
pylint *.py             # Check for issues
mypy action_logger.py   # Type checking
```

---

## Areas for Contribution

### High Priority
- [ ] Vector embeddings integration (semantic search)
- [ ] Performance optimizations
- [ ] Extended test coverage
- [ ] Documentation improvements

### Medium Priority
- [ ] Additional search strategies
- [ ] Visualization dashboard
- [ ] Analytics and reporting
- [ ] Integration examples

### Low Priority
- [ ] Language bindings
- [ ] Alternative database backends
- [ ] Web UI
- [ ] Mobile app

---

## Architecture Notes

### Three-Layer Design
1. **Capture (ActionLogger):** Logs all actions
2. **Storage (FTS5):** Searches across actions
3. **Integration:** Enriches responses with context

### Key Files
- `action_logger.py` - Core logging (240 lines)
- `query_builder.py` - Search interface (230 lines)
- `context_aware_responder.py` - Context detection (290 lines)
- `integration_bridge.py` - End-to-end pipeline (180 lines)

### Design Principles
- **No external dependencies** - Uses only Python stdlib + SQLite
- **Zero manual work** - Everything is automatic
- **Fast searches** - FTS5 < 1ms typical query
- **Rich metadata** - JSON for flexibility
- **Extensible** - Easy to add new action types

---

## Testing Guidelines

### Unit Tests
Test individual components:
```python
def test_action_logger_user_message():
    logger = ActionLogger()
    action_id = logger.log_user_message("test")
    assert action_id > 0

def test_query_builder_search():
    query = AuditLogQuery()
    results = query.search_text("test", limit=5)
    assert isinstance(results, list)
```

### Integration Tests
Test end-to-end workflows:
```python
def test_context_enrichment_flow():
    bridge = AuditBridge()
    bridge.log_user_input("Remember voice demo?")
    response = bridge.finalize_response("Sure!", token_count=2)
    assert "voice" in response.lower()
```

### Performance Tests
Ensure performance targets are met:
```python
def test_search_performance():
    query = AuditLogQuery()
    start = time.time()
    results = query.search_text("test", limit=10)
    elapsed = time.time() - start
    assert elapsed < 0.01  # < 10ms
```

---

## Documentation Standards

### Code Comments
- Explain WHY, not WHAT
- Use docstrings for functions
- Include examples for complex logic

### Docstring Format
```python
def search_text(self, query: str, limit: int = 10) -> List[Dict]:
    """
    Search audit log using FTS5.

    Args:
        query: FTS5 search query (supports AND, OR, phrases)
        limit: Maximum results to return (default: 10)

    Returns:
        List of matching action records, most recent first

    Example:
        >>> query = AuditLogQuery()
        >>> results = query.search_text("voice demo", limit=5)
        >>> print(results[0]['content'])
    """
```

### README Updates
- Update when adding features
- Add examples for new functionality
- Keep Quick Start section current

### ARCHITECTURE Updates
- Document new design decisions
- Update data flow diagrams
- Explain performance implications

---

## Review Process

### What We Look For
- **Code quality:** Clean, readable, well-documented
- **Testing:** Comprehensive tests, good coverage
- **Documentation:** Updates to README/ARCHITECTURE
- **Performance:** No regressions, ideally improvements
- **Design:** Fits the three-layer architecture

### Review Timeline
- Expect review within 3-5 business days
- May request changes before merging
- Work with reviewers to iterate
- Be patient, we're all volunteers

### Getting Approved
- Address all comments
- Get sign-off from maintainers
- Tests pass in CI
- Documentation is complete

---

## Release Process

### Version Numbers
We use semantic versioning: MAJOR.MINOR.PATCH

- **MAJOR:** Breaking changes
- **MINOR:** New features (backwards compatible)
- **PATCH:** Bug fixes

### Release Steps
1. Update version in setup.py
2. Update CHANGELOG.md
3. Tag release in git
4. Publish to PyPI
5. Announce on social media

### How to Request a Release
- Open an issue requesting a release
- List the changes included
- Wait for maintainers to create release

---

## Getting Help

### Questions?
- Check documentation
- Search existing Issues
- Ask in Discussions
- Contact maintainers

### Need Help Contributing?
- Start with "good first issue" labels
- Ask questions in Pull Request
- Reach out to maintainers
- Look at example PRs

---

## Credit

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in commit messages

---

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Last Updated:** 2026-05-06

Thank you for contributing! 🎉
