import logging
from typing import Union

from rich.logging import RichHandler

logger = logging.getLogger(__name__)


class Logger:
    def __init__(self) -> None:
        pass

    def setup(self, level: Union[int, str]) -> None:
        if isinstance(level, int):
            levels = ['NOTSET', 'WARN', 'INFO', 'DEBUG']
            level = levels[max(0, min(level, 3))]
        self._level = getattr(logging, level, logging.NOTSET)

        if self._level > 0:
            handler = RichHandler(
                level=self._level,
                tracebacks_show_locals=False,
                rich_tracebacks=True,
                markup=True,
            )
            logging.basicConfig(
                level=self._level,
                handlers=[handler],
                format="%(message)s",
                datefmt="[%X]",
                force=True,
            )

    @property
    def level(self) -> int:
        return self._level

    @property
    def is_debug(self) -> bool:
        return self.level == logging.DEBUG

    @property
    def is_info(self) -> bool:
        return self.is_debug or self.level == logging.INFO

    @property
    def is_warn(self) -> bool:
        return self.is_info or self.level == logging.WARN
