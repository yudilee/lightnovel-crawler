from fastapi import APIRouter

from ...context import ctx

# The root router
router = APIRouter()


@router.post("/update-sources", summary='Update sources from the repository')
async def update() -> int:
    await ctx.sources.update()
    return ctx.sources.version
