# Contributing to ADM Compliance Framework

Thank you for your interest in contributing to the Australian Privacy Act ADM Compliance Framework!

## Code of Conduct

This project adheres to the Contributor Covenant Code of Conduct. By participating, you are expected to uphold this code.

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues. When creating a bug report, include:

- **Clear title and description**
- **Steps to reproduce**
- **Expected vs actual behavior**
- **Screenshots** (if applicable)
- **Environment details** (OS, Python version, etc.)

### Suggesting Enhancements

Enhancement suggestions are welcome! Please provide:

- **Clear use case**
- **Expected behavior**
- **Why this enhancement would be useful**
- **Possible implementation approach**

### Pull Requests

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Add tests** for new functionality
5. **Run the test suite** (`./scripts/run-tests.sh`)
6. **Commit your changes** (`git commit -m 'Add amazing feature'`)
7. **Push to the branch** (`git push origin feature/amazing-feature`)
8. **Open a Pull Request**

## Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/APAADMCF.git
cd APAADMCF

# Add upstream remote
git remote add upstream https://github.com/originalowner/APAADMCF.git

# Create virtual environment (backend)
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Install pre-commit hooks
pre-commit install

# Run tests
pytest tests/
```

## Coding Standards

### Python (Backend)

- Follow **PEP 8** style guide
- Use **type hints** where appropriate
- Maximum line length: **120 characters**
- Use **docstrings** for all public functions/classes
- Run `black` for formatting
- Run `flake8` for linting
- Run `mypy` for type checking

Example:

```python
def calculate_fairness_score(metrics: Dict[str, float]) -> int:
    """
    Calculate overall fairness score from individual metrics.

    Args:
        metrics: Dictionary of fairness metric names to values

    Returns:
        Overall fairness score (0-100)

    Raises:
        ValueError: If metrics dictionary is empty
    """
    if not metrics:
        raise ValueError("Metrics dictionary cannot be empty")

    # Implementation
    return score
```

### TypeScript/React (Frontend)

- Follow **Airbnb JavaScript Style Guide**
- Use **TypeScript** for type safety
- Use **functional components** with hooks
- Use **Material-UI** components
- Follow **React best practices**

Example:

```typescript
interface DashboardProps {
  userId: string;
  onUpdate: (data: DashboardData) => void;
}

const Dashboard: React.FC<DashboardProps> = ({ userId, onUpdate }) => {
  const [data, setData] = useState<DashboardData | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, [userId]);

  // Implementation

  return <Box>...</Box>;
};
```

### SQL

- Use **meaningful table/column names**
- Always include **comments** explaining complex queries
- Use **proper indexing**
- Follow **naming conventions**

## Testing

All contributions must include appropriate tests:

### Backend Tests

```python
def test_create_adm_system(client, auth_headers):
    """Test creating a new ADM system"""
    response = client.post(
        "/api/v1/adm/registry",
        json={
            "name": "Test System",
            "purpose": "Testing",
            "adm_category": "fully_automated",
            "decision_impact": "low"
        },
        headers=auth_headers
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test System"
```

### Test Coverage

- Aim for **80%+ code coverage**
- Test **happy paths** and **error cases**
- Include **integration tests**
- Test **edge cases**

## Documentation

- Update **README.md** if adding features
- Add **docstrings** to all functions
- Update **API documentation** for new endpoints
- Add **examples** for complex features
- Update **CHANGELOG.md**

## Commit Messages

Follow conventional commits format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Build process or auxiliary tool changes

Examples:

```
feat(pia): add automated risk scoring

Implement automatic risk level calculation based on
PIA assessment scores. Includes weighted scoring
algorithm and threshold configuration.

Closes #123
```

```
fix(api): correct fairness metric calculation

Fixed bug in demographic parity calculation that
caused incorrect results for imbalanced datasets.

Fixes #456
```

## Security

- **Never commit secrets** or credentials
- Use **environment variables** for configuration
- Follow **OWASP guidelines**
- Report security issues privately to security@example.com

## Privacy & Compliance

This framework handles sensitive compliance data:

- Follow **data minimisation** principles
- Implement **proper encryption**
- Respect **Australian data sovereignty**
- Comply with **Privacy Act requirements**
- Document privacy impacts of new features

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Feel free to:
- Open an issue for discussion
- Join our community chat
- Email: dev@example.com

## Recognition

Contributors will be recognized in:
- README.md Contributors section
- Release notes
- Project documentation

Thank you for contributing to privacy compliance in AI systems! 🇦🇺
