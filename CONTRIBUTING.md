# Contributing to AutoGen Research Assistant

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/learning-autogen.git
   cd learning-autogen
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/learning-autogen.git
   ```

## Development Setup

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Node.js 18+ and npm
- Redis (for async features)
- Git

### Installation

1. Install Python dependencies:
   ```bash
   uv sync --all-extras
   ```

2. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

3. Install pre-commit hooks:
   ```bash
   uv run pre-commit install
   ```

4. Set up environment:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

## Development Workflow

### Creating a Branch

Always create a new branch for your work:

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions or modifications

### Making Changes

1. **Keep changes focused** - One feature or fix per pull request
2. **Write tests** - Add tests for new features and bug fixes
3. **Update documentation** - Keep README and docs in sync
4. **Follow coding standards** - See below

## Coding Standards

### Python Code

We use the following tools to maintain code quality:

- **Ruff** - Linting and formatting
- **MyPy** - Type checking
- **Black** - Code formatting (via Ruff)

Run before committing:

```bash
# Lint and format
uv run ruff check src/ tests/ --fix
uv run ruff format src/ tests/

# Type check
uv run mypy src/
```

### Code Style Guidelines

1. **Type Hints**
   - Use type hints for all function parameters and return values
   - Example:
     ```python
     def process_data(input: str, count: int = 5) -> List[Dict[str, Any]]:
         ...
     ```

2. **Docstrings**
   - Use Google-style docstrings
   - Document all public functions, classes, and modules
   - Example:
     ```python
     def research(task: str, verbose: bool = True) -> List[Dict[str, Any]]:
         """
         Execute a research task with the team.

         Args:
             task: Research task description
             verbose: Whether to print messages in real-time

         Returns:
             List of messages from the conversation

         Raises:
             Exception: If the research task fails
         """
     ```

3. **Imports**
   - Group imports: standard library, third-party, local
   - Use absolute imports
   - Sort imports alphabetically within groups

4. **Line Length**
   - Maximum 100 characters per line
   - Break long lines logically

### Frontend Code

- Follow React best practices
- Use functional components and hooks
- Keep components small and focused
- Add PropTypes or TypeScript types

## Testing

### Running Tests

Run the full test suite:

```bash
uv run pytest
```

Run with coverage:

```bash
uv run pytest --cov=src/autogen_research --cov-report=html
```

Run specific tests:

```bash
uv run pytest tests/test_agents.py -v
```

### Writing Tests

1. **Test Organization**
   - Place tests in `tests/` directory
   - Name test files `test_*.py`
   - Name test functions `test_*`

2. **Test Coverage**
   - Aim for >80% code coverage
   - Test both success and failure cases
   - Test edge cases

3. **Test Structure**
   - Use pytest fixtures for common setup
   - Keep tests isolated and independent
   - Use descriptive test names

Example:

```python
def test_research_agent_handles_empty_task():
    """Test that research agent properly handles empty task."""
    agent = ResearchAgent(model_client=mock_client)
    with pytest.raises(ValueError):
        agent.process_task("")
```

## Submitting Changes

### Before Submitting

1. **Update your branch** with latest upstream:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run all checks**:
   ```bash
   # Run tests
   uv run pytest

   # Run linting
   uv run ruff check src/ tests/

   # Run type checking
   uv run mypy src/
   ```

3. **Pre-commit hooks** will run automatically on commit

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): subject

body

footer
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/tooling changes

Examples:
```
feat(agents): add custom agent configuration support

- Add AgentConfig class
- Update ResearchTeam to accept custom configs
- Add tests for custom configurations

Closes #123
```

```
fix(api): handle rate limiter when Redis unavailable

Fall back to memory storage when Redis connection fails

Fixes #456
```

### Creating a Pull Request

1. Push your branch to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. Open a Pull Request on GitHub

3. Fill out the PR template:
   - **Title**: Clear, concise description
   - **Description**: What changed and why
   - **Testing**: How you tested the changes
   - **Screenshots**: If UI changes
   - **Related Issues**: Link to issues

4. Wait for review and address feedback

### Pull Request Guidelines

- Keep PRs focused and reasonably sized
- Link to related issues
- Update documentation if needed
- Ensure CI/CD passes
- Respond to review comments promptly
- Squash commits if requested

## Reporting Issues

### Bug Reports

Include:
- Clear, descriptive title
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Error messages and logs
- Screenshots if applicable

### Feature Requests

Include:
- Clear description of the feature
- Use case and motivation
- Proposed implementation (optional)
- Alternative solutions considered

### Questions

For questions:
- Check existing issues first
- Search documentation
- Provide context for your question
- Include relevant code snippets

## Development Tips

### Database Migrations

Create a new migration:
```bash
uv run alembic revision --autogenerate -m "description"
```

Apply migrations:
```bash
uv run alembic upgrade head
```

### Running Locally

Full development mode:
```bash
./start_dev.sh
```

Individual components:
```bash
# Backend
python app.py

# Frontend
cd frontend && npm run dev

# Celery worker
celery -A src.autogen_research.tasks.celery_app worker --loglevel=info
```

### Debugging

- Use Python debugger: `import pdb; pdb.set_trace()`
- Check logs in `logs/` directory
- Use verbose mode for detailed output
- Enable debug mode in Flask for development

## Project Structure

```
learning-autogen/
├── src/autogen_research/   # Core Python package
│   ├── agents/             # Agent implementations
│   ├── models/             # Model factory
│   ├── teams/              # Team orchestration
│   ├── database/           # Database models
│   ├── tasks/              # Celery tasks
│   └── utils/              # Utilities
├── frontend/               # React frontend
├── tests/                  # Test suite
├── migrations/             # Database migrations
├── .github/workflows/      # CI/CD pipelines
└── docs/                   # Documentation
```

## Release Process

Maintainers only:

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Create release branch
4. Run full test suite
5. Create GitHub release
6. Tag release

## Questions?

- Open an issue for bugs or features
- Check existing documentation
- Review closed issues and PRs

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to AutoGen Research Assistant! 🎉
