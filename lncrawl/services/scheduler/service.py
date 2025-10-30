import logging
from threading import Event, Thread
from typing import List, Optional

from ...context import ctx
from ...utils.time_utils import current_timestamp
# from .cleaner import run_cleaner
# from .runner import run_crawler

logger = logging.getLogger(__name__)

CONCURRENCY = 2


class JobScheduler:
    def __init__(self) -> None:
        self.start_ts: int = 0
        self.last_cleanup_ts: int = 0
        self.threads: List[Thread] = []
        self.signal: Optional[Event] = None

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
                # self.__free()
                # self.__add_cleaner(signal)
                # if len(self.threads) < CONCURRENCY:
                #     self.__add_crawler(signal)
        except KeyboardInterrupt:
            signal.set()
        finally:
            logger.info("Scheduler stoppped")

    def __free(self):
        logger.debug("Waiting for queue to be free")
        # wait for any job to finish
        for i, t in enumerate(self.threads):
            if not t.is_alive():  # if done
                return self.threads.pop(i)  # remove
            t.join(1)  # wait 1s for this job

    def __add_cleaner(self, signal=Event()):
        # skip if another cleaner is already running
        if "cleaner" in self.threads:
            return

        # skip if cleaner has run recently
        timeout = ctx.config.crawler.cleaner_cooldown * 1000
        if current_timestamp() - self.last_cleanup_ts < timeout:
            return
        self.last_cleanup_ts = current_timestamp()

        # # create and start threads
        # t = Thread(
        #     target=run_cleaner,
        #     args=[signal],
        # )
        # t.start()
        # self.threads.append(t)

    def __add_crawler(self, signal=Event()):
        logger.debug("Running new task")
        for job in ctx.jobs.list_pending():
            # if queue is full, wait for the next round,
            # but continue processing pending jobs to detect duplicates
            if len(self.threads) >= CONCURRENCY:
                continue

            # # create and start threads
            # t = Thread(
            #     target=run_crawler,
            #     args=[job.id, signal],
            #     # daemon=True,
            # )
            # t.start()
            # self.threads.append(t)
