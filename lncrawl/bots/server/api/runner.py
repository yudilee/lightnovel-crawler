from fastapi import APIRouter, Depends

from ....context import AppContext
from ....dao.job import JobRunnerHistory

# The root router
router = APIRouter()


@router.get("/status", summary='Get runner status')
def status(ctx: AppContext = Depends()) -> bool:
    return bool(ctx.scheduler.running)


@router.get("/history", summary='Get runner history')
def history(ctx: AppContext = Depends()) -> JobRunnerHistory:
    return JobRunnerHistory(
        running=ctx.scheduler.running,
        history=list(reversed(ctx.scheduler.history)),
    )


@router.post("/start", summary='Start the runner')
def start(ctx: AppContext = Depends()) -> bool:
    ctx.scheduler.start()
    return True


@router.post("/stop", summary='Stops the runner')
def stop(ctx: AppContext = Depends()) -> bool:
    ctx.scheduler.stop()
    return True
