# Test Suite for TaskMaster Backend

## Overview
This directory contains integration tests for the TaskMaster Backend API, with a focus on validating the new task attributes migration (estimated_time, complexity, parent_task_id, user_id).

## Prerequisites
```bash
pip install pytest pytest-cov httpx
```

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run with verbose output
```bash
pytest tests/ -v
```

### Run specific test class
```bash
pytest tests/test_task_integration.py::TestComplexityValidation -v
```

### Run with coverage report
```bash
pytest tests/ --cov=app --cov-report=html
```

### Run specific test
```bash
pytest tests/test_task_integration.py::TestComplexityValidation::test_valid_complexity_values -v
```

## Test Coverage

### Test Classes

1. **TestTaskCreationWithNewFields**
   - Create task with all new fields
   - Create task without new fields (backward compatibility)
   - Create task with zero estimated time
   - Create task with partial new fields

2. **TestComplexityValidation**
   - Valid complexity values (1-5)
   - Invalid complexity values (0, 6+, negative)
   - Invalid type for complexity

3. **TestEstimatedTimeValidation**
   - Valid estimated time values (including decimals)
   - Negative estimated time (should fail)
   - Invalid type for estimated_time

4. **TestTaskHierarchy**
   - Create subtask with valid parent
   - Create subtask with invalid parent (should fail)
   - Prevent self-reference on update
   - Create nested tasks (3+ levels)
   - Update task's parent

5. **TestTaskUpdateWithNewFields**
   - Add new fields to existing task
   - Clear new fields by setting to null
   - Update task with invalid complexity
   - Update task with invalid parent

6. **TestTaskRetrieval**
   - GET /get-tasks includes new fields
   - Get mixed old and new tasks

7. **TestBackwardCompatibility**
   - Task completion status toggle
   - Task deletion
   - Task with tags and new fields

8. **TestErrorHandling**
   - Delete non-existent task
   - Update non-existent task
   - Toggle status of non-existent task
   - Create task missing required fields
   - Create task with empty strings

## Test Fixtures

- **test_db**: In-memory SQLite database for isolated tests
- **client**: FastAPI TestClient for making requests

## Expected Results

- **73 total test cases** covering:
  - ✅ 5 valid complexity values (1-5)
  - ✅ 5 invalid complexity values
  - ✅ 6 valid estimated time values
  - ✅ 3 invalid estimated time values
  - ✅ Task hierarchy validation
  - ✅ Self-reference prevention
  - ✅ Backward compatibility
  - ✅ Error handling

## Notes

- Tests use in-memory SQLite database for speed
- No external database required
- Each test is isolated
- Parametrized tests reduce code duplication
- Tests include both happy path and error cases

## Continuous Integration

Add to CI/CD pipeline:
```bash
pytest tests/ --cov=app --cov-report=xml --junit-xml=test-results.xml
```

## Troubleshooting

### Database connection errors
- Ensure test database is using in-memory SQLite
- Check that get_db override is properly set in fixtures

### Schema not created
- Verify Base.metadata.create_all() is called in test_db fixture
- Check that all models are imported before tests run

### Import errors
- Ensure app package is in PYTHONPATH
- Run from project root: `pytest tests/`

### Test timeouts
- In-memory SQLite should be fast
- If tests timeout, check for blocking I/O operations
