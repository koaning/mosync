import asyncio
import random
import logging
import tqdm
from typing import List, Dict, Any, Callable, Optional

async def process_with_retry(
    func, 
    item, 
    max_retries=3, 
    initial_backoff=1.0, 
    backoff_factor=2.0, 
    jitter=0.1,
    timeout=None,
    on_success=None,
    on_failure=None,
    logger=None
):
    """Process a single item with retry logic and backoff."""
    logger = logger or logging.getLogger(__name__)
    attempts = 0
    last_exception = None

    while attempts <= max_retries:
        try:
            # Add timeout if specified
            if timeout is not None:
                result = await asyncio.wait_for(func(item), timeout=timeout)
            else:
                result = await func(item)

            # Call success callback if provided
            if on_success:
                on_success(item, result)

            return item, result, None

        except Exception as e:
            attempts += 1
            last_exception = e

            if attempts <= max_retries:
                # Calculate backoff time with jitter
                backoff_time = initial_backoff * (backoff_factor ** (attempts - 1))
                jitter_amount = backoff_time * jitter
                actual_backoff = backoff_time + random.uniform(-jitter_amount, jitter_amount)
                actual_backoff = max(0.1, actual_backoff)  # Ensure minimum backoff

                logger.warning(
                    f"Attempt {attempts}/{max_retries} failed for item {item}. "
                    f"Retrying in {actual_backoff:.2f}s. Error: {str(e)}"
                )

                await asyncio.sleep(actual_backoff)
            else:
                if on_failure:
                    on_failure(item, last_exception)

                logger.error(
                    f"All {max_retries} retry attempts failed for item {item}. "
                    f"Final error: {str(last_exception)}"
                )

    return item, None, last_exception

async def async_map_worker(
    items, 
    func, 
    semaphore,
    max_retries=3, 
    initial_backoff=1.0, 
    backoff_factor=2.0, 
    jitter=0.1,
    timeout=None,
    on_success=None,
    on_failure=None,
    logger=None
):
    """Map an async function over items with concurrency control."""
    async def bounded_process(item):
        async with semaphore:
            return await process_with_retry(
                func, 
                item, 
                max_retries, 
                initial_backoff, 
                backoff_factor, 
                jitter,
                timeout,
                on_success,
                on_failure,
                logger
            )

    # Create tasks
    tasks = [bounded_process(item) for item in items]
    return tasks

def async_map_with_retry(
    items: List[Dict[Any, Any]],
    func: Callable,
    max_concurrency: int = 10,
    max_retries: int = 3,
    initial_backoff: float = 1.0,
    backoff_factor: float = 2.0,
    jitter: float = 0.1,
    timeout: Optional[float] = None,
    on_success: Optional[Callable] = None,
    on_failure: Optional[Callable] = None,
    show_progress: bool = True,
    description: str = "Processing items",
    logger: Optional[logging.Logger] = None
):
    """
    Map an async function over a list of dictionaries with progress tracking and retry.

    Args:
        items: List of dictionaries to process
        func: Async function that takes a dictionary and returns a result
        max_concurrency: Maximum number of concurrent tasks
        max_retries: Maximum number of retry attempts
        initial_backoff: Initial backoff time in seconds
        backoff_factor: Multiplier for backoff on successive retries
        jitter: Random jitter factor to avoid thundering herd
        timeout: Maximum time to wait for a task to complete (None = wait forever)
        on_success: Callback function to run on successful processing
        on_failure: Callback function to run when an item fails after all retries
        show_progress: Whether to show progress bar
        description: Description for progress bar
        logger: Optional logger for detailed logging

    Returns:
        List of tuples (original_dict, result_or_None, exception_or_None)
    """
    logger = logger or logging.getLogger(__name__)

    async def main():
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(max_concurrency)

        # Get tasks
        tasks = await async_map_worker(
            items, 
            func, 
            semaphore,
            max_retries, 
            initial_backoff, 
            backoff_factor, 
            jitter,
            timeout,
            on_success,
            on_failure,
            logger
        )

        # Set up progress bar if requested
        if show_progress:
            results = []
            with mo.status.progress_bar(total=len(tasks), title=description) as progress_bar:
                for task in asyncio.as_completed(tasks):
                    result = await task
                    results.append(result)
                    progress_bar.update()
            return results
        else:
            # Without progress bar, just gather all results
            return await asyncio.gather(*tasks)

    return main()
