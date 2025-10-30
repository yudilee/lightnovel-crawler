from enum import Enum, IntEnum

__all__ = [
    'OutputFormat',
    'UserRole',
    'UserTier',
    'JobStatus',
    'JobPriority',
    'JobType',
]


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class UserTier(IntEnum):
    BASIC = 0
    PREMIUM = 1
    VIP = 2


class JobType(IntEnum):
    NOVEL = 0
    FULL_NOVEL = 1
    CHAPTER = 10
    BATCH_CHAPTERS = 11
    VOLUME = 20
    BATCH_VOLUMES = 21
    IMAGE = 30
    BATCH_IMAGES = 31
    ARTIFACT = 40
    BATCH_ARTIFACTS = 41


class JobStatus(str, Enum):
    PENDING = 0
    RUNNING = 1
    SUCCESS = 2
    FAILED = 3
    CANCELED = 4


class JobPriority(IntEnum):
    LOW = 0
    NORMAL = 1
    HIGH = 2


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
