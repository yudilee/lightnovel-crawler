from enum import Enum, IntEnum

__all__ = [
    'OutputFormat',
    'UserRole',
    'UserTier',
    'JobStatus',
    'JobPriority',
    'RunState',
]


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class UserTier(IntEnum):
    BASIC = 0
    PREMIUM = 1
    VIP = 2


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "done"


class JobPriority(IntEnum):
    LOW = 0
    NORMAL = 1
    HIGH = 2


class RunState(IntEnum):
    FAILED = 0
    SUCCESS = 1
    CANCELED = 2
    FETCHING_NOVEL = 3
    FETCHING_CONTENT = 4
    CREATING_ARTIFACTS = 5


class OutputFormat(str, Enum):
    json = "json"
    epub = "epub"
    web = "web"
    text = "text"
    pdf = "pdf"
    mobi = "mobi"
    docx = "docx"
    rtf = "rtf"
    fb2 = "fb2"
    azw3 = "azw3"
    lit = "lit"
    lrf = "lrf"
    oeb = "oeb"
    pdb = "pdb"
    rb = "rb"
    snb = "snb"
    tcr = "tcr"

    def __str__(self) -> str:
        return self.value
