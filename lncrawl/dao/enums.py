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
    NOVEL_BATCH = 1
    FULL_NOVEL = 5
    FULL_NOVEL_BATCH = 6
    CHAPTER = 10
    CHAPTER_BATCH = 11
    VOLUME = 20
    VOLUME_BATCH = 21
    IMAGE = 30
    IMAGE_BATCH = 31
    ARTIFACT = 40
    ARTIFACT_BATCH = 41
    NOVEL_ARTIFACTS = 42


class JobStatus(IntEnum):
    PENDING = 0
    RUNNING = 1
    SUCCESS = 2
    FAILED = 3
    CANCELED = 4


class JobPriority(IntEnum):
    LOW = 0
    NORMAL = 1
    HIGH = 2


class SecretType(IntEnum):
    TEXT = 0
    LOGIN = 1


class OutputFormat(str, Enum):
    json = "json"
    epub = "epub"
    text = "txt"
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
