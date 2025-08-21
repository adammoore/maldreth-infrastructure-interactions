# Contributing to MaLDReTH Infrastructure Interactions

First off, thank you for considering contributing to MaLDReTH Infrastructure Interactions! It's people like you that make this project such a great tool for the research community.

## Code of Conduct

This project and everyone participating in it is governed by the [MaLDReTH Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to [support@maldreth.org](mailto:support@maldreth.org).

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues as you might find out that you don't need to create one. When you are creating a bug report, please include as many details as possible:

* **Use a clear and descriptive title** for the issue to identify the problem.
* **Describe the exact steps which reproduce the problem** in as many details as possible.
* **Provide specific examples to demonstrate the steps**.
* **Describe the behavior you observed after following the steps** and point out what exactly is the problem with that behavior.
* **Explain which behavior you expected to see instead and why.**
* **Include screenshots and animated GIFs** if possible.
* **Include details about your environment** (OS, Python version, browser, etc.).

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, please include:

* **Use a clear and descriptive title** for the issue to identify the suggestion.
* **Provide a step-by-step description of the suggested enhancement** in as many details as possible.
* **Provide specific examples to demonstrate the steps**.
* **Describe the current behavior** and **explain which behavior you expected to see instead** and why.
* **Explain why this enhancement would be useful** to most users.

### Pull Requests

Please follow these steps to have your contribution considered by the maintainers:

1. **Fork the repository** and create your branch from `main`.
2. **Follow the styleguides** described below.
3. **Include tests** for any new functionality.
4. **Update documentation** as needed.
5. **Ensure the test suite passes**.
6. **Make sure your code lints**.
7. **Issue that pull request!**

## Styleguides

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line
* Follow [Conventional Commits](https://www.conventionalcommits.org/) specification:
  * `feat:` New feature
  * `fix:` Bug fix
  * `docs:` Documentation only changes
  * `style:` Code style changes (formatting, etc)
  * `refactor:` Code change that neither fixes a bug nor adds a feature
  * `test:` Adding missing tests or correcting existing tests
  * `chore:` Changes to the build process or auxiliary tools

### Python Styleguide

All Python code must adhere to [PEP 8](https://www.python.org/dev/peps/pep-0008/) with the following additions:

* Use type hints where possible
* Maximum line length is 100 characters
* Use f-strings for string formatting
* Sort imports with `isort`
* Format code with `black`

Example:
```python
from typing import List, Optional

from flask import Flask, request
from sqlalchemy import create_engine

from app.models import User


def get_users(status: Optional[str] = None) -> List[User]:
    """
    Get users with optional status filter.
    
    Args:
        status: Optional user status filter
        
    Returns:
        List of User objects
    """
    query = User.query
    if status:
        query = query.filter_by(status=status)
    return query.all()
```

### JavaScript Styleguide

* Use ES6+ features
* 2 spaces for indentation
* Use semicolons
* Use `const` and `let`, avoid `var`
* Use template literals for string interpolation

### Documentation Styleguide

* Use [Google style](https://google.github.io/styleguide/pyguide.html) for Python docstrings
* Keep README and other documentation up to date
* Include code examples where appropriate

## Development Process

1. **Set up your development environment**:
   ```bash
   git clone https://github.com/yourusername/maldreth-infrastructure.git
   cd maldreth-infrastructure
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt -r requirements-dev.txt
   pre-commit install
   ```

2. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes** following the styleguides above.

4. **Run tests**:
   ```bash
   pytest
   black .
   isort .
   flake8 .
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: Add amazing feature"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** from your fork to the main repository.

## Project Structure

```
maldreth-infrastructure/
├── app.py              # Main application file
├── models.py           # Database models
├── routes.py           # API routes
├── config.py           # Configuration
├── utils/              # Utility functions
├── templates/          # HTML templates
├── static/             # CSS, JS, images
├── tests/              # Test files
├── data/               # Data files
└── scripts/            # Utility scripts
```

## Testing

We use pytest for testing. Please write tests for any new functionality:

```python
# test_example.py
def test_new_feature(client, sample_data):
    """Test the new feature works correctly."""
    response = client.get('/api/new-feature')
    assert response.status_code == 200
    assert response.json['status'] == 'success'
```

## Questions?

Feel free to contact the maintainers if you have any questions. We're here to help!

Thank you for contributing! 🎉
