from fastapi import APIRouter

from ...context import ctx
from ..models.job import JobRunnerHistory

# The root router
router = APIRouter()


@router.get("/status", summary='Get runner status')
def status() -> bool:
    return bool(ctx.scheduler.running)


@router.get("/history", summary='Get runner history')
def history() -> JobRunnerHistory:
    return JobRunnerHistory(
        running=ctx.scheduler.running,
        history=list(reversed(ctx.scheduler.history)),
    )


@router.post("/start", summary='Start the runner')
def start() -> bool:
    ctx.scheduler.start()
    return True


@router.post("/stop", summary='Stops the runner')
def stop() -> bool:
    ctx.scheduler.stop()
    return True
