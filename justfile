# Run the dev server
dev:
    uv run uvicorn src.app:app --reload

# Run all tests
test:
    uv run pytest

# Run tests with verbose output
test-v:
    uv run pytest -v
