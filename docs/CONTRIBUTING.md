# Contributing to Smart Building Energy Management System (SBEMS)

We welcome contributions to SBEMS! This document provides guidelines for contributing to the project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Style](#code-style)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Reporting Issues](#reporting-issues)

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your feature or bugfix
4. Make your changes
5. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.9+
- Git
- Virtual environment (recommended)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/smart-building-energy-management.git
cd smart-building-energy-management

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -e ".[dev]"

# Run tests to verify setup
python test_system.py
```

## Code Style

We use the following tools and standards:

- **Code Formatting**: [Black](https://black.readthedocs.io/)
- **Import Sorting**: [isort](https://pycqa.github.io/isort/)
- **Linting**: [Flake8](https://flake8.pycqa.org/)
- **Type Checking**: [MyPy](https://mypy.readthedocs.io/)

### Running Code Quality Checks

```bash
# Format code
black sbems/

# Sort imports
isort sbems/

# Run linter
flake8 sbems/

# Type checking
mypy sbems/
```

### Pre-commit Hooks

We recommend using pre-commit hooks:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

## Testing

### Running Tests

```bash
# Run basic functionality test
python test_system.py

# Run unit tests (when available)
pytest tests/

# Run with coverage
pytest --cov=sbems tests/
```

### Writing Tests

- Write tests for all new features
- Maintain test coverage above 80%
- Use descriptive test names
- Include both positive and negative test cases

## Submitting Changes

### Pull Request Process

1. **Update Documentation**: Ensure README.md and relevant docs are updated
2. **Add Tests**: Include tests for new functionality
3. **Follow Code Style**: Run formatting and linting tools
4. **Write Good Commit Messages**: Use clear, descriptive commit messages
5. **Keep Changes Focused**: One feature or fix per pull request

### Commit Message Format

```
type(scope): description

- feat: new feature
- fix: bug fix
- docs: documentation changes
- style: formatting changes
- refactor: code refactoring
- test: adding tests
- chore: maintenance tasks

Example:
feat(sensors): add new air quality sensor type
fix(anomaly): resolve false positive detection
docs(readme): update installation instructions
```

### Pull Request Template

When submitting a pull request, please include:

- **Description**: What does this PR do?
- **Motivation**: Why is this change needed?
- **Testing**: How was this tested?
- **Breaking Changes**: Any breaking changes?
- **Checklist**: Use the PR template checklist

## Reporting Issues

### Bug Reports

When reporting bugs, please include:

- **Environment**: OS, Python version, dependency versions
- **Steps to Reproduce**: Detailed steps to reproduce the issue
- **Expected Behavior**: What should happen
- **Actual Behavior**: What actually happens
- **Error Messages**: Full error messages and stack traces
- **Additional Context**: Screenshots, logs, etc.

### Feature Requests

For feature requests, include:

- **Use Case**: Why is this feature needed?
- **Proposed Solution**: How should it work?
- **Alternatives**: Any alternative solutions considered?
- **Implementation Ideas**: Technical implementation thoughts

## Development Guidelines

### Architecture Principles

- **Modularity**: Keep components loosely coupled
- **Extensibility**: Design for easy extension
- **Performance**: Consider performance implications
- **Documentation**: Document public APIs
- **Error Handling**: Provide meaningful error messages

### Sensor Development

When adding new sensor types:

1. Inherit from `BaseSensor`
2. Implement required abstract methods
3. Add realistic simulation logic
4. Include comprehensive unit tests
5. Update documentation

### Analytics Development

For new analytics features:

1. Consider computational complexity
2. Provide configuration options
3. Include data validation
4. Add performance metrics
5. Document algorithm parameters

## Resources

- [Project Documentation](docs/)
- [API Reference](docs/api.md)
- [Architecture Guide](docs/architecture.md)
- [Issue Tracker](https://github.com/yourusername/smart-building-energy-management/issues)
- [Discussions](https://github.com/yourusername/smart-building-energy-management/discussions)

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/). Please be respectful and inclusive.

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to SBEMS! 🏢⚡
