import logging
from threading import Event, Thread
from typing import Callable, List, Set

from ...context import ctx
from ...exceptions import AbortedException
from ...utils.event_lock import EventLock
from .cleaner import run_cleaner
from .runner import run_pending

logger = logging.getLogger(__name__)


class JobScheduler:
    def __init__(self) -> None:
        self._threads: List[Thread] = []
        self._queue: Set[str] = set()
        self._lock = EventLock()
        self._signal = Event()
        self._signal.set()

    def close(self):
        self.stop()

    @property
    def running(self) -> bool:
        return not self._signal.is_set()

    def start(self):
        if self.running:
            return
        self._signal = Event()
        self._thread(run_cleaner, ctx.config.crawler.cleaner_cooldown)
        for _ in range(ctx.config.crawler.runner_concurrency):
            self._thread(run_pending, ctx.config.crawler.runner_cooldown)
        logger.info("Scheduler started")

    def stop(self):
        if not self.running:
            return
        self._signal.set()
        for t in self._threads:
            t.join()
        self._threads.clear()
        logger.info("Scheduler stoppped")

    def _thread(self, run: Callable[[Event], None], interval: int) -> None:
        t = Thread(
            target=self._loop,
            args=[run, interval],
            daemon=True,  # does not block exit
        )
        t.start()
        self._threads.append(t)

    def _loop(self, run: Callable[[Event], None], interval: int) -> None:
        while self.running:
            try:
                self._signal.wait(interval)
                if self._signal.is_set():
                    return
                run(self._signal)
            except KeyboardInterrupt:
                self._signal.set()
            except AbortedException:
                return
            except Exception:
                logger.error('Unexpected error in scheduler', stack_info=True)
