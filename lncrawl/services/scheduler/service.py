import logging
from threading import Event, Lock, Thread
from typing import List, Optional, Set

from sqlmodel import asc, col, desc, select, true

from ...context import ctx
from ...dao import Job
from ...utils.time_utils import current_timestamp
from .runner import JobRunner

logger = logging.getLogger(__name__)

CONCURRENCY = 5


class JobScheduler:
    def __init__(self) -> None:
        self.start_ts: int = 0
        self.last_cleanup_ts: int = 0
        self.threads: List[Thread] = []
        self.signal: Optional[Event] = None
        self.queue: Set[str] = set()
        self.lock = Lock()

    def close(self):
        self.stop()

    @property
    def running(self) -> bool:
        if not self.signal:
            return False
        return not self.signal.is_set()

    def start(self):
        if self.running:
            return
        self.signal = Event()
        self.start_ts = current_timestamp()
        for _ in range(CONCURRENCY):
            t = Thread(
                target=self.run,
                args=[self.signal],
                daemon=True,
            )
            t.start()
            self.threads.append(t)
        logger.info("Scheduler started")

    def stop(self):
        if not self.signal:
            return
        self.signal.set()
        for t in self.threads:
            t.join()
        self.threads.clear()
        self.signal = None
        logger.info("Scheduler stoppped")

    def run(self, signal=Event()):
        while not signal.is_set():
            try:
                signal.wait(ctx.config.crawler.runner_cooldown)
                if signal.is_set():
                    return
                self.__job(signal)
            except KeyboardInterrupt:
                signal.set()
            except Exception:
                logger.error('Runner error', exc_info=True)

    def __job(self, signal=Event()):
        job = self.__get_next_job()
        if not job:
            return
        try:
            JobRunner(job, signal).process()
        finally:
            with self.lock:
                self.queue.remove(job.id)

    def __get_next_job(self) -> Optional[Job]:
        with ctx.db.session() as sess:
            jobs = sess.exec(
                select(Job)
                .where(col(Job.is_done).is_not(true()))
                .order_by(
                    desc(Job.priority),
                    asc(Job.created_at),
                )
            ).all()
            for job in jobs:
                with self.lock:
                    if job.id in self.queue:
                        continue
                    self.queue.add(job.id)
                    return job

    # def __cleaner(self):
    #     # skip if cleaner has run recently
    #     timeout = ctx.config.crawler.cleaner_cooldown * 1000
    #     now = current_timestamp()
    #     if now - self.last_cleanup_ts < timeout:
    #         return
    #     self.last_cleanup_ts = now
    #     # TODO
