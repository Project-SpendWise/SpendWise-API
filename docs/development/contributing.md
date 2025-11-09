# Contributing

Thank you for your interest in contributing to SpendWise API! This document provides guidelines and instructions for contributing.

## Getting Started

1. **Fork the repository**
2. **Clone your fork:**
   ```bash
   git clone https://github.com/yourusername/SpendWise-API.git
   cd SpendWise-API
   ```

3. **Set up development environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Create a branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Guidelines

### Code Style

- Follow PEP 8 style guide
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small

### Commit Messages

Use clear, descriptive commit messages:

```
feat: Add password reset endpoint
fix: Resolve CORS issue with credentials
docs: Update API authentication documentation
refactor: Simplify user validation logic
```

### Pull Request Process

1. **Update documentation** if you change API behavior
2. **Add tests** for new features or bug fixes
3. **Ensure all tests pass**
4. **Update CHANGELOG.md** if applicable
5. **Submit pull request** with clear description

## Adding New Endpoints

1. **Create route in appropriate blueprint:**
   ```python
   @auth_bp.route('/new-endpoint', methods=['POST'])
   @jwt_required()
   def new_endpoint():
       # Implementation
   ```

2. **Get database instance:**
   ```python
   from flask import current_app
   
   def get_db():
       return current_app.extensions['sqlalchemy']
   
   @auth_bp.route('/new-endpoint', methods=['POST'])
   def new_endpoint():
       db_instance = get_db()
       # Use db_instance.session for queries
   ```

3. **Add validation:**
   ```python
   from utils.validators import validate_email
   is_valid, error_msg = validate_email(email)
   ```

4. **Use standardized responses:**
   ```python
   from utils.responses import success_response, error_response
   return success_response(data={...})
   ```

5. **Use SQLAlchemy 2.0 query syntax:**
   ```python
   from sqlalchemy import select
   user = db_instance.session.scalar(select(User).filter_by(email=email))
   ```

6. **Update documentation** in `docs/api/endpoints/`

**See:** [Database Patterns](database-patterns.md) for detailed database access patterns.

## Adding New Models

1. **Create model file in `models/`:**
   ```python
   from app import db
   
   class NewModel(db.Model):
       # Model definition
   ```

2. **Create migration:**
   ```bash
   flask db migrate -m "Add new model"
   flask db upgrade
   ```

3. **Update documentation** in `docs/models/`

## Testing

### Running Tests

```bash
pytest
```

### Writing Tests

```python
def test_user_registration(client):
    response = client.post('/api/auth/register', json={
        'email': 'test@example.com',
        'password': 'TestPass123'
    })
    assert response.status_code == 201
    assert response.json['success'] == True
```

## Documentation

### Updating Documentation

1. **Edit Markdown files** in `docs/`
2. **Preview changes:**
   ```bash
   mkdocs serve
   ```
3. **Build documentation:**
   ```bash
   mkdocs build
   ```

### Documentation Standards

- Use clear, concise language
- Include code examples
- Add request/response examples
- Document all parameters and return values

## Security Considerations

- **Never commit secrets** (API keys, passwords, tokens)
- **Validate all user input**
- **Use parameterized queries** (SQLAlchemy handles this)
- **Sanitize user input** before storing
- **Follow OWASP guidelines**

## Reporting Issues

When reporting issues, include:

- **Description** of the problem
- **Steps to reproduce**
- **Expected behavior**
- **Actual behavior**
- **Environment** (OS, Python version, etc.)
- **Error messages** or logs

## Feature Requests

For feature requests:

- **Describe the feature** clearly
- **Explain the use case**
- **Provide examples** if possible
- **Consider alternatives** you've explored

## Code Review

All contributions require code review. Reviewers will check:

- Code quality and style
- Test coverage
- Documentation updates
- Security considerations
- Performance implications

## Questions?

If you have questions:

- Open an issue for discussion
- Check existing documentation
- Review existing code for patterns

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

Thank you for contributing to SpendWise API! 🎉

