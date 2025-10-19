import logging
from collections import deque
from threading import Event, Thread
from typing import Deque, Dict, Optional

from ...context import ctx
from ...dao.job import JobStatus, RunState
from ...server.models.job import JobRunnerHistoryItem
from ...utils.time_utils import current_timestamp
from .cleaner import run_cleaner
from .runner import run_crawler

logger = logging.getLogger(__name__)

CONCURRENCY = 2


class JobScheduler:
    def __init__(self) -> None:
        self.start_ts: int = 0
        self.last_cleanup_ts: int = 0
        self.signal: Optional[Event] = None
        self.threads: Dict[str, Thread] = {}
        self.history: Deque[JobRunnerHistoryItem] = deque(maxlen=50)

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
        Thread(
            target=self.run,
            args=[self.signal],
            daemon=True,
        ).start()

    def stop(self):
        if not self.signal:
            return
        self.signal.set()
        self.signal = None

    def run(self, signal=Event()):
        logger.info("Scheduler started")
        try:
            while not signal.is_set():
                signal.wait(ctx.config.crawler.runner_cooldown)
                if signal.is_set():
                    return
                self.__free()
                self.__add_cleaner(signal)
                if len(self.threads) < CONCURRENCY:
                    self.__add_crawler(signal)
        except KeyboardInterrupt:
            signal.set()
        finally:
            logger.info("Scheduler stoppped")

    def __free(self):
        logger.debug("Waiting for queue to be free")
        # wait for any job to finish
        for k, t in self.threads.items():
            t.join(1)  # wait 1s for this job
            if not t.is_alive():  # if done
                # remove from queue and exit loop
                del self.threads[k]
                break

    def __add_cleaner(self, signal=Event()):
        # skip if another cleaner is already running
        if "cleaner" in self.threads:
            return

        # skip if cleaner has run recently
        timeout = ctx.config.crawler.cleaner_cooldown * 1000
        if current_timestamp() - self.last_cleanup_ts < timeout:
            return
        self.last_cleanup_ts = current_timestamp()

        # create and start threads
        t = Thread(
            target=run_cleaner,
            args=[signal],
        )
        t.start()
        self.threads["cleaner"] = t

    def __add_crawler(self, signal=Event()):
        logger.debug("Running new task")
        for job in ctx.jobs.pending_jobs():
            with ctx.db.session() as sess:
                # check for orphaned novel
                if not job.novel_id:
                    sess.refresh(job)
                    job.run_state = RunState.FETCHING_NOVEL
                    sess.add(job)
                    sess.commit()
                    continue

                # cancel duplicate jobs
                if job.novel_id in self.threads:
                    if job.status != JobStatus.RUNNING:
                        sess.refresh(job)
                        job.status = JobStatus.COMPLETED
                        job.run_state = RunState.CANCELED
                        job.error = "Canceled as a duplicate job"
                        sess.add(job)
                        sess.commit()
                    continue

            # if queue is full, wait for the next round,
            # but continue processing pending jobs to detect duplicates
            if len(self.threads) >= CONCURRENCY:
                continue

            # create and start threads
            t = Thread(
                target=run_crawler,
                args=[job.id, signal],
                # daemon=True,
            )
            t.start()
            self.threads[job.novel_id] = t

            # log this to history
            self.history.append(
                JobRunnerHistoryItem(
                    time=current_timestamp(),
                    job_id=job.id,
                    user_id=job.user_id,
                    novel_id=job.novel_id,
                    status=job.status,
                    run_state=job.run_state,
                )
            )
