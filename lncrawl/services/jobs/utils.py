from sqlmodel import col, select, literal

from ...dao import Job


def sa_select_children(job_id: str, inclusive: bool = False):
    deps = (
        select(Job.id)
        .where(Job.parent_job_id == job_id)
        .cte("descendends", recursive=True)
    )
    deps = deps.union_all(
        select(Job.id)
        .where(Job.parent_job_id == deps.c.id)
    )
    if inclusive:
        return select(deps.c.id).union_all(
            select(literal(job_id).label('id'))
        )
    else:
        return select(deps.c.id)


def sa_select_parents(job_id: str, inclusive: bool = False):
    pars = (
        select(col(Job.parent_job_id).label('id'))
        .where(Job.id == job_id)
        .cte('ancestors', recursive=True)
    )
    pars = pars.union_all(
        select(col(Job.parent_job_id).label('id'))
        .where(Job.id == pars.c.id)
    )
    if inclusive:
        return select(pars.c.id).union_all(
            select(literal(job_id).label('id'))
        )
    else:
        return select(pars.c.id)
