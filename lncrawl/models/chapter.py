from typing import Any, Dict, Optional

from box import Box


class Chapter(Box):
    def __init__(
        self,
        id: int,
        url: str = "",
        title: str = "",
        volume: Optional[int] = None,
        body: Optional[str] = None,
        images: Dict[str, str] = dict(),
        success: bool = False,
        extras: Dict[str, Any] = dict(),
        **kwargs,
    ) -> None:
        self.id = id
        self.url = url
        self.title = title
        self.volume = volume
        self.body = body
        self.images = images
        self.success = success
        self.extra = extras
        extras.update(kwargs)
        self.update(extras)
