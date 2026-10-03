from collections import defaultdict, deque
import hashlib
import secrets
from threading import Lock
from time import monotonic

from fastapi import Request

from app.errors import problem

_events: dict[str, deque[float]] = defaultdict(deque)
_salt = secrets.token_bytes(32)
_lock = Lock()


def limit(request: Request, bucket: str, count: int, window_seconds: int) -> None:
    address = request.client.host if request.client else "unknown"
    key = hashlib.sha256(_salt + f"{bucket}:{address}".encode()).hexdigest()
    now = monotonic()
    with _lock:
        for old_key, old_events in list(_events.items()):
            if not old_events or old_events[-1] < now - 86400:
                del _events[old_key]
        events = _events[key]
        while events and events[0] < now - window_seconds:
            events.popleft()
        if len(events) >= count:
            raise problem(429, "Terlalu banyak permintaan", "Coba lagi setelah beberapa saat.")
        events.append(now)
