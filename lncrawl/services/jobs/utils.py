from sqlmodel import col, select

from ...dao import Job


def sa_select_children(job_id: str):
    deps = (
        select(Job.id)
        .where(Job.id == job_id)
        .cte("descendends", recursive=True)
    )
    deps = deps.union_all(
        select(Job.id)
        .where(Job.parent_job_id == deps.c.id)
    )
    return select(deps.c.id)


def sa_select_parents(job_id: str):
    pars = (
        select(col(Job.parent_job_id).label('id'))
        .where(Job.id == job_id)
        .cte('ancestors', recursive=True)
    )
    pars = pars.union_all(
        select(col(Job.parent_job_id).label('id'))
        .where(Job.id == pars.c.id)
    )
    return select(pars.c.id)
