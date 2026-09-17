# Day 4 Completion — CI Fundamentals & GitHub Actions

## What Was Completed

### Task 1: First CI Pipeline ✅
- Created `.github/workflows/ci.yml` triggered on push/PR to `main` and `day_*` branches
- Pipeline runs automatically on every code change
- Two jobs: `lint` (flake8) and `test` (pytest), with `test` depending on `lint`

### Task 2: Automated Tests ✅
- Created `tests/test_app.py` with unit test for the home page route
- Created `tests/integration/test_workflow.py` with integration test for the registration flow
- Added `conftest.py` to configure the Python path for the test runner
- Tests mock the database layer (`app.get_db`) so no real DB is needed in CI

### Task 3: Code Quality & Linter Integration ✅
- Added `flake8` to `requirements.txt` for code style enforcement
- CI pipeline lints `tests/` and `conftest.py` before running tests
- Line length limit set to 100 characters

## Files Added / Changed

| File | Change |
|------|--------|
| `.github/workflows/ci.yml` | New — CI pipeline definition |
| `tests/test_app.py` | New — unit tests |
| `tests/integration/test_workflow.py` | New — integration tests |
| `tests/__init__.py` | New — package marker |
| `tests/integration/__init__.py` | New — package marker |
| `conftest.py` | New — pytest path configuration |
| `requirements.txt` | Updated — added `pytest`, `pytest-mock`, `flake8` |

## Acceptance Criteria

- [x] CI pipeline triggers on push to `main` and `day_*` branches
- [x] Pipeline runs linter (flake8) on test code
- [x] Pipeline runs unit and integration tests (pytest)
- [x] Tests pass with mocked database (no real DB dependency)
- [x] Pipeline fails if tests fail (provides fast feedback)

## Testing Instructions

Run the test suite locally:
```bash
pip install -r requirements.txt
pytest tests/ -v --tb=short
```

Run the linter:
```bash
flake8 tests/ conftest.py --max-line-length=100
```

## Key Learnings

- GitHub Actions workflows live in `.github/workflows/` and are version-controlled alongside code
- Mocking the database with `pytest-mock` lets unit tests run without a real database
- Separating `lint` and `test` jobs makes it easy to see which check failed
- The `needs:` keyword enforces job ordering — tests only run if linting passes
