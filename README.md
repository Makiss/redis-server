# Redis Server Project

A Redis server implementation in Python.

## Development

### Code Formatting

This project uses the following tools for code formatting and linting:

- **Black**: Code formatter
- **isort**: Import sorter
- **flake8**: Code linter

To install these tools:

```bash
pip install -e ".[dev]"
```

To format the code:

```bash
# Format code with Black
black app tests

# Sort imports
isort app tests

# Run linting checks
flake8 app tests
```

You can also set up your editor to run these automatically on save.
