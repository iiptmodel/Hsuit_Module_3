import asyncio
from typing import Dict, Any

_QUEUES: Dict[int, asyncio.Queue] = {}


def create_queue(report_id: int) -> asyncio.Queue:
    """Create and return a new asyncio.Queue for a report id."""
    loop = asyncio.get_event_loop()
    q: asyncio.Queue = asyncio.Queue()
    _QUEUES[report_id] = q
    return q


def get_queue(report_id: int):
    return _QUEUES.get(report_id)


def remove_queue(report_id: int):
    _QUEUES.pop(report_id, None)


def publish(report_id: int, message: Any) -> None:
    """Publish a message to the queue for the given report id.

    This is safe to call from background threads: it schedules the put
    on the running event loop.
    """
    q = _QUEUES.get(report_id)
    if not q:
        return

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        # Not in event loop (called from thread); get the main loop and schedule
        loop = asyncio.get_event_loop()

    # Schedule putting the message into the queue
    loop.call_soon_threadsafe(asyncio.create_task, q.put(message))
