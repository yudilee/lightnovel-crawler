from typing import Any, Dict, Optional

from box import Box


class Volume(Box):
    def __init__(
        self,
        id: int,
        title: str = "",
        chapter_count: int = 0,
        extras: Dict[str, Any] = dict(),
        **kwargs,
    ) -> None:
        self.id = id
        self.title = title
        self.chapter_count = chapter_count
        self.extra = extras
        extras.update(kwargs)
        self.update(extras)
