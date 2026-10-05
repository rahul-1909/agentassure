# Contributing to AgentAssure

Thank you for your interest in contributing to **AgentAssure**, an enterprise human-in-the-loop QA workflow and CI-gated regression testing platform for conversational AI agents.

## Development Workflow

1. Fork the repository and create your feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Set up local development environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install flake8 black isort pytest pytest-cov
   ```

3. Initialize local development database:
   ```bash
   python -m agentassure.cli.main init-db
   ```

4. Set up frontend:
   ```bash
   cd frontend
   npm install
   npm run build
   ```

## Code Quality Standards

Before submitting a pull request, ensure all linting and test coverage checks pass:

- **Formatting (Black):**
  ```bash
  python -m black --check agentassure tests
  ```

- **Import Sorting (isort):**
  ```bash
  python -m isort --check-only agentassure tests
  ```

- **Static Analysis (Flake8):**
  ```bash
  python -m flake8 agentassure tests --max-line-length=120 --ignore=E203,W503,F401,F841,E501,E226
  ```

- **Test Suite & Coverage Gate (≥85%):**
  ```bash
  pytest --cov=agentassure --cov-fail-under=85 tests/
  ```

## Pull Request Guidelines

- Ensure your branch is rebased onto `main`.
- Write clear, descriptive commit messages following the Conventional Commits specification (`feat:`, `fix:`, `docs:`, `test:`).
- Document new endpoints or modules with Google-style Python docstrings.
- Add corresponding unit and integration tests under `tests/` for all new functionality.

## License

By contributing to AgentAssure, you agree that your contributions will be licensed under the MIT License.
