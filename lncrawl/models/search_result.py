from typing import Any, Dict, List

from box import Box


class SearchResult(Box):
    def __init__(
        self,
        title: str,
        url: str,
        info: str = "",
        extras: Dict[str, Any] = dict(),
        **kwargs,
    ) -> None:
        self.title = str(title)
        self.url = str(url)
        self.info = str(info)
        self.extras = extras
        extras.update(kwargs)
        self.update(extras)


class CombinedSearchResult(Box):
    def __init__(
        self,
        id: str,
        title: str,
        novels: List[SearchResult] = [],
        extras: Dict[str, Any] = dict(),
        **kwargs,
    ) -> None:
        self.id = id
        self.title = str(title)
        self.novels = novels
        self.extras = extras
        extras.update(kwargs)
        self.update(extras)
