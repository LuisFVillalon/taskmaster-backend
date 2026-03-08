# Migration Quick Reference

## Change Summary

### New Database Fields
```sql
-- Added to tasks table
ALTER TABLE tasks ADD COLUMN estimated_time NUMERIC(10,2);
ALTER TABLE tasks ADD COLUMN complexity INTEGER;
ALTER TABLE tasks ADD COLUMN parent_task_id INTEGER;
ALTER TABLE tasks ADD COLUMN user_id INTEGER;

-- Added foreign key
ALTER TABLE tasks ADD CONSTRAINT fk_tasks_parent_task_id 
  FOREIGN KEY (parent_task_id) REFERENCES tasks(id);
```

### API Changes

#### All endpoints now support these optional fields:

**Request Body Example:**
```json
{
  "title": "Complete backend API",
  "description": "Implement all remaining endpoints",
  "estimated_time": 8.5,
  "complexity": 4,
  "parent_task_id": 1,
  "user_id": 1,
  "tags": []
}
```

**Response Example:**
```json
{
  "id": 42,
  "title": "Complete backend API",
  "description": "Implement all remaining endpoints",
  "category": null,
  "completed": false,
  "urgent": false,
  "due_date": null,
  "due_time": null,
  "created_date": "2026-03-07T12:00:00",
  "completed_date": null,
  "estimated_time": 8.5,
  "complexity": 4,
  "parent_task_id": 1,
  "user_id": 1,
  "tags": []
}
```

### Validation Rules

| Field | Rules | Error Code |
|-------|-------|-----------|
| `complexity` | Must be 1-5 or null | 422 |
| `estimated_time` | Must be ≥ 0 or null | 422 |
| `parent_task_id` | Must reference existing task or null | 400 |
| `parent_task_id` | Cannot equal task's own id | 400 |
| `user_id` | No validation (for future use) | - |

### Key Error Messages

```
# Complexity out of range
{"detail": "Complexity must be an integer between 1 and 5"}

# Negative estimated time
{"detail": "Estimated time must be a non-negative number (hours)"}

# Parent task not found
{"detail": "Parent task with ID 999 not found"}

# Self-reference
{"detail": "A task cannot be its own parent"}
```

---

## Common Operations

### Create a task hierarchy

```python
# Create parent task
parent = POST /create-task
{
  "title": "Q2 Project",
  "complexity": 3,
  "estimated_time": 40
}
# Returns: { "id": 1, ... }

# Create child task
child = POST /create-task
{
  "title": "Implement API",
  "parent_task_id": 1,
  "complexity": 2,
  "estimated_time": 20
}
# Returns: { "id": 2, "parent_task_id": 1, ... }

# Get all tasks (includes hierarchy info)
GET /get-tasks
# Returns: [{ "id": 1, ... }, { "id": 2, "parent_task_id": 1, ... }]
```

### Add estimation to existing task

```python
# Existing task (no estimation)
GET /get-tasks
# Returns: [{ "id": 5, "title": "Bug fix", "estimated_time": null, ... }]

# Update with estimation
PUT /update-task/5
{
  "title": "Bug fix",
  "estimated_time": 2.5,
  "complexity": 1
}
# Returns: { "id": 5, "estimated_time": 2.5, "complexity": 1, ... }
```

### Promote subtask to standalone

```python
# Remove parent reference
PUT /update-task/2
{
  "title": "Implement API",
  "parent_task_id": null,
  "complexity": 2,
  "estimated_time": 20
}
# Returns: { "id": 2, "parent_task_id": null, ... }
```

---

## Testing Quick Start

```bash
# Install pytest
pip install pytest httpx

# Run all tests
pytest tests/

# Run specific test
pytest tests/test_task_integration.py::TestComplexityValidation::test_valid_complexity_values -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run only hierarchy tests
pytest tests/ -m hierarchy

# Run only validation tests
pytest tests/ -m validation
```

**Expected Result:** All 73 tests pass ✅

---

## Deployment Steps

1. **Pull changes**
   ```bash
   git pull
   ```

2. **Run migration**
   ```bash
   cd taskmaster-backend
   alembic upgrade head
   ```

3. **Run tests**
   ```bash
   pytest tests/ -v
   ```

4. **Restart server**
   ```bash
   python -m uvicorn app.main:app --reload
   ```

5. **Verify with Swagger UI**
   - Visit: `http://localhost:8000/docs`
   - Create task with new fields
   - Verify response includes new fields

---

## Troubleshooting

### Migration fails with "alembic not found"
```bash
pip install alembic
echo $DATABASE_URL  # Verify it's set
```

### Tests fail with import errors
```bash
pip install -r requirements.txt -e .
pytest tests/
```

### FK constraint violation when deleting
- Parent task cannot be deleted if has subtasks
- Delete subtasks first, then parent

### Validation error for complexity
- Must be integer 1-5, not 0 or 6
- Check your input format

---

## Performance Notes

- New columns are nullable (existing queries unaffected)
- FK constraint adds slight overhead on insert/update
- Recommend index on `parent_task_id` for large datasets
- Consider periodic analysis of task hierarchy depth

---

## Backward Compatibility

✅ All new fields are optional  
✅ Existing API clients continue to work  
✅ Old tasks without new fields still queryable  
✅ No breaking changes to existing endpoints  

**Migration is 100% backward compatible**

---

## Next Steps

1. ✅ Migration deployed
2. ✅ Tests passing
3. → Update frontend UI for new fields
4. → Train users on new features
5. → Monitor hierarchy depth
6. → Consider cascade delete enhancement

---

For detailed information, see:
- [MIGRATION_ANALYSIS.md](MIGRATION_ANALYSIS.md) - Technical analysis
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Full deployment guide
- [tests/README.md](tests/README.md) - Test documentation
