import pytest
import asyncio
from mosync import ProcessResult, async_map_with_retry

# Test ProcessResult class
def test_process_result():
    # Test successful case
    success_result = ProcessResult(item="test", result="success", error=None)
    assert success_result.is_success() == True
    assert success_result.item == "test"
    assert success_result.result == "success"
    assert success_result.error is None

    # Test failure case
    error = ValueError("test error")
    failure_result = ProcessResult(item="test", result=None, error=error)
    assert failure_result.is_success() == False
    assert failure_result.item == "test"
    assert failure_result.result is None
    assert failure_result.error == error

# Async test helpers
async def success_func(x):
    await asyncio.sleep(0.1)
    return x * 2

async def failing_func(x):
    await asyncio.sleep(0.1)
    raise ValueError(f"Error processing {x}")

async def sometimes_failing_func(x):
    await asyncio.sleep(0.1)
    if x % 2 == 0:
        raise ValueError(f"Error processing even number {x}")
    return x * 2

# Test async_map_with_retry functionality
@pytest.mark.asyncio
async def test_async_map_success():
    items = [1, 2, 3, 4, 5]
    results = await async_map_with_retry(
        items=items,
        func=success_func,
        max_concurrency=2,
        show_progress=False
    )
    
    assert len(results) == len(items)
    for i, result in enumerate(results):
        assert result.is_success()
        assert result.item == items[i]
        assert result.result == items[i] * 2
        assert result.error is None

@pytest.mark.asyncio
async def test_async_map_all_failing():
    items = [1, 2, 3]
    results = await async_map_with_retry(
        items=items,
        func=failing_func,
        max_retries=2,
        initial_backoff=0.1,
        show_progress=False
    )
    
    assert len(results) == len(items)
    for result in results:
        assert not result.is_success()
        assert isinstance(result.error, ValueError)
        assert result.result is None

@pytest.mark.asyncio
async def test_async_map_partial_failures():
    items = [1, 2, 3, 4]
    results = await async_map_with_retry(
        items=items,
        func=sometimes_failing_func,
        max_retries=2,
        initial_backoff=0.1,
        show_progress=False
    )
    
    assert len(results) == len(items)
    for i, result in enumerate(results):
        if items[i] % 2 == 0:
            assert not result.is_success()
            assert isinstance(result.error, ValueError)
            assert result.result is None
        else:
            assert result.is_success()
            assert result.result == items[i] * 2
            assert result.error is None

@pytest.mark.asyncio
async def test_async_map_concurrency():
    items = list(range(10))
    max_concurrency = 2
    
    # Track concurrent executions
    running = 0
    max_running = 0
    
    async def tracking_func(x):
        nonlocal running, max_running
        running += 1
        max_running = max(max_running, running)
        await asyncio.sleep(0.1)
        running -= 1
        return x
    
    results = await async_map_with_retry(
        items=items,
        func=tracking_func,
        max_concurrency=max_concurrency,
        show_progress=False
    )
    
    assert len(results) == len(items)
    assert max_running <= max_concurrency
    for result in results:
        assert result.is_success()

@pytest.mark.asyncio
async def test_async_map_with_timeout():
    async def slow_func(x):
        await asyncio.sleep(0.5)
        return x

    items = [1, 2, 3]
    results = await async_map_with_retry(
        items=items,
        func=slow_func,
        timeout=0.1,
        show_progress=False
    )
    
    assert len(results) == len(items)
    for result in results:
        assert not result.is_success()
        assert isinstance(result.error, asyncio.TimeoutError)
