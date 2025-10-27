import logging
import os
from pathlib import Path
from typing import Union

import zstd

from ..context import ctx
from ..exceptions import ServerErrors

logger = logging.getLogger(__name__)

StrPath = Union[str, Path]

ZSTD_HEAD = b'\x28\xB5\x2F\xFD'


class FileService:
    def __init__(self) -> None:
        pass

    @property
    def root(self):
        return ctx.config.app.output_path

    def resolve(self, file: StrPath) -> Path:
        if isinstance(file, str):
            file = Path(file)
        if file.is_absolute():
            return file
        return self.root / file

    def exists(self, file_path: StrPath):
        return self.resolve(file_path).is_file()

    def load(self, file_path: StrPath) -> bytes:
        file = self.resolve(file_path)
        if not file.is_file():
            raise ServerErrors.no_such_file
        return file.read_bytes()

    def save(self, file_path: StrPath, content: bytes) -> Path:
        file = self.resolve(file_path)
        file.parent.mkdir(parents=True, exist_ok=True)
        tmp = file.with_suffix(f'{file.suffix}.tmp')
        try:
            tmp.write_bytes(content)
            os.replace(tmp, file)
        finally:
            tmp.unlink(missing_ok=True)
        return file

    def load_text(
        self,
        file_path: StrPath,
        encoding: str = 'utf-8',
    ) -> str:
        data = self.load(file_path)
        if data.startswith(ZSTD_HEAD):
            data = zstd.decompress(data)
        return data.decode(encoding)

    def save_text(
        self,
        file_path: StrPath,
        content: str,
        compress: bool = True,
        encoding: str = 'utf-8',
    ) -> Path:
        data = content.encode(encoding)
        if compress or data.startswith(ZSTD_HEAD):
            data = zstd.compress(data)
        return self.save(file_path, data)
