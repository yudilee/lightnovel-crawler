import logging
from threading import Event, Thread
from typing import List, Set

from ...context import ctx
from ...utils.event_lock import EventLock
from ...utils.time_utils import current_timestamp
from .cleaner import run_cleaner
from .runner import JobRunner

logger = logging.getLogger(__name__)


class JobScheduler:
    def __init__(self) -> None:
        self.start_ts: int = 0
        self.last_cleanup_ts: int = 0
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
        self.start_ts = current_timestamp()
        for _ in range(ctx.config.crawler.runner_concurrency):
            t = Thread(
                target=self.run,
                daemon=True,
            )
            t.start()
            self._threads.append(t)
        logger.info("Scheduler started")

    def stop(self):
        if not self.running:
            return
        self._signal.set()
        for t in self._threads:
            t.join()
        self._threads.clear()
        logger.info("Scheduler stoppped")

    def run(self):
        while self.running:
            try:
                self._signal.wait(ctx.config.crawler.runner_cooldown)
                self.__cleaner()
                self.__job()
            except KeyboardInterrupt:
                self._signal.set()
            except Exception:
                logger.error('Runner error', stack_info=True)

    def __job(self):
        with self._lock.using(self._signal):
            job = ctx.jobs._pending(self._queue)
            if not job:
                return
            self._queue.add(job.id)

        try:
            JobRunner(job, self._signal).process()
        finally:
            with self._lock.using(self._signal):
                self._queue.remove(job.id)

    def __cleaner(self):
        job_id = 'cleaner'

        with self._lock.using(self._signal):
            if job_id in self._queue:
                return
            timeout = ctx.config.crawler.cleaner_cooldown * 1000
            if current_timestamp() - self.last_cleanup_ts < timeout:
                return
            self._queue.add(job_id)

        try:
            run_cleaner(self._signal)
        finally:
            with self._lock.using(self._signal):
                self._queue.remove(job_id)
                self.last_cleanup_ts = current_timestamp()
