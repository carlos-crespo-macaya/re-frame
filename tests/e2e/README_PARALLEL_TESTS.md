# E2E Tests - Parallel Execution with pytest-xdist

## Overview
The E2E tests are configured to run in parallel using pytest-xdist, significantly reducing test execution time.

## Configuration

### Default Behavior
- Tests run in parallel by default using all available CPU cores (`-n auto`)
- Configuration is in `pytest.ini`
- Each test gets a unique session ID that includes the worker ID

### Running Tests

```bash
# Run with default parallel execution
pytest

# Run serially (disable parallel execution)
pytest -n 0

# Run with specific number of workers
pytest -n 4

# Run only specific tests in parallel
pytest -k "test_conversation" -n auto
```

### Performance Measurement

Use the included script to measure performance improvement:

```bash
cd tests/e2e
python measure_performance.py
```

## Implementation Details

### 1. Unique Session IDs
Each test gets a unique session ID that includes the worker ID:
```python
@pytest.fixture
def session_id(worker_id) -> str:
    return f"test-session-{worker_id}-{uuid.uuid4().hex[:8]}"
```

### 2. Test Isolation
- Each worker uses its own browser instance
- Session IDs prevent conflicts between parallel tests
- Docker services are shared across all workers

### 3. Markers for Serial Execution
Tests that must run serially can be marked:
```python
@pytest.mark.serial
async def test_that_needs_serial_execution():
    pass
```

Then run serial tests separately:
```bash
pytest -m serial -n 0
```

## CI/CD Integration

The GitHub Actions workflow automatically uses parallel execution:
- The `pytest` command in CI will use the settings from `pytest.ini`
- This provides consistent behavior between local and CI environments

## Troubleshooting

### Tests Failing in Parallel but Passing Serially
- Check for shared state between tests
- Ensure unique session IDs are used
- Look for hardcoded ports or resources

### Debugging Parallel Test Issues
```bash
# Run with more verbose output
pytest -n auto -v -s

# Run specific test in isolation
pytest tests/test_conversation_flow.py::TestConversationFlow::test_multi_turn_conversation -n 0
```

## Performance Expectations

With pytest-xdist enabled:
- Expected speedup: 2-4x (depending on CPU cores)
- Typical execution time: ~5-7 minutes (down from ~15-20 minutes)
- Best results with 4-8 workers

## Best Practices

1. **Keep tests independent** - Each test should be able to run in any order
2. **Use unique identifiers** - Always use the session_id fixture
3. **Avoid hardcoded waits** - Use explicit waits instead
4. **Monitor resource usage** - Parallel tests use more memory and CPU

## Monitoring Performance

The test output will show:
- Which worker is running each test (e.g., `[gw0]`, `[gw1]`)
- Total execution time
- Number of tests run per worker