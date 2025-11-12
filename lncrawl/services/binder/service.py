import logging
import shutil
from functools import cached_property
from threading import Event, Lock
from typing import Callable, Dict, Optional, Set

from ...context import ctx
from ...dao import Artifact
from ...dao.enums import OutputFormat
from ...exceptions import ServerError, ServerErrors
from ...utils.file_tools import safe_filename
from .calibre import convert_epub
from .epub import make_epub
from .json import make_json
from .text import make_text

logger = logging.getLogger(__name__)

requires_zip = set([
    OutputFormat.json,
    OutputFormat.text,
])
archive_maker: Dict[OutputFormat, Callable[..., None]] = {
    OutputFormat.json: make_json,
    OutputFormat.text: make_text,
    OutputFormat.epub: make_epub,
    OutputFormat.docx: convert_epub,
    OutputFormat.mobi: convert_epub,
    OutputFormat.pdf: convert_epub,
    OutputFormat.rtf: convert_epub,
    OutputFormat.azw3: convert_epub,
    OutputFormat.fb2: convert_epub,
    OutputFormat.lit: convert_epub,
    OutputFormat.lrf: convert_epub,
    OutputFormat.pdb: convert_epub,
    OutputFormat.rb: convert_epub,
    OutputFormat.tcr: convert_epub,
}


class BinderService:
    def __init__(self):
        self.lock = Lock()
        pass

    @cached_property
    def depends_on_epub(self) -> Set[OutputFormat]:
        return set([
            k
            for k, v in archive_maker.items()
            if v == convert_epub
        ])

    def make_artifact(
        self,
        novel_id: str,
        novel_title: str,
        format: OutputFormat,
        job_id: Optional[str] = None,
        user_id: Optional[str] = None,
        depends_on: Optional[str] = None,
        signal=Event(),
    ) -> Artifact:
        make = archive_maker[format]
        if not callable(make):
            raise ServerErrors.format_not_available

        file_name = safe_filename(novel_title).title()
        file_name += f'.{format}'
        if format in requires_zip:
            file_name += '.zip'

        artifact = Artifact(
            novel_id=novel_id,
            user_id=user_id,
            job_id=job_id,
            format=format,
            file_name=file_name,
        )
        working_dir = ctx.config.app.output_path / 'tmp' / artifact.id
        try:
            shutil.rmtree(working_dir, ignore_errors=True)
            working_dir.mkdir(parents=True)
            make(
                working_dir,
                signal=signal,
                artifact=artifact,
                depends_on=depends_on
            )
            with self.lock, ctx.db.session() as sess:
                sess.add(artifact)
                sess.commit()
                return artifact
        except ServerError as e:
            raise e.with_extra(artifact.format)
        except Exception as e:
            logger.error(f'Create artifact failed: {file_name}', exc_info=True)
            raise ServerErrors.failed_creating_artifact.with_extra(artifact.format) from e
        finally:
            shutil.rmtree(working_dir, ignore_errors=True)
