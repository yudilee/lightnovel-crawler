import logging
import os
import subprocess
from functools import lru_cache
from pathlib import Path

from ...context import ctx
from ...dao import Artifact
from ...dao.enums import OutputFormat
from ...exceptions import ServerErrors
from .epub import make_epub

logger = logging.getLogger(__name__)


def __ebook_convert(*args) -> bool:
    """
    Calls `ebook-convert` with given args
    Visit https://manual.calibre-ebook.com/generated/en/ebook-convert.html for argument list.
    """
    try:
        isdebug = os.getenv("debug_mode")
        with open(os.devnull, "w", encoding="utf8") as dumper:
            subprocess.run(
                args=['ebook-convert'] + [str(a) for a in args],
                stdout=None if isdebug else dumper,
                stderr=dumper,
                check=True
            )

        return True
    except subprocess.CalledProcessError:
        logger.exception("Failed to convert ebook with args: %s", list(args))
        return False
    except Exception as e:
        logger.exception("An unexpected error occurred: %s", str(e))
        return False


@lru_cache
def is_calibre_available() -> bool:
    return bool(__ebook_convert("--version"))


def convert_epub(working_dir: Path, artifact: Artifact) -> None:
    out_file = ctx.files.resolve(artifact.output_file)
    if out_file.exists():
        return

    if not is_calibre_available():
        raise ServerErrors.calibre_exe_not_found

    epub = ctx.artifacts.get_latest(artifact.novel_id, artifact.format)
    if not (epub and epub.is_available):
        with ctx.db.session() as sess:
            epub = Artifact(
                novel_id=artifact.novel_id,
                format=OutputFormat.epub,
                job_id=artifact.job_id,
                user_id=artifact.user_id,
            )
            make_epub(working_dir, epub)
            sess.add(epub)
            sess.commit()

    if not epub.is_available:
        raise ServerErrors.failed_creating_artifact(OutputFormat.epub)

    tmp_file = working_dir / out_file.name
    novel = ctx.novels.get(artifact.novel_id)
    epub_file = ctx.files.resolve(epub.output_file)

    logger.info(f'Converting "{epub_file}" to "{out_file}"', )
    args = [
        epub_file,
        tmp_file,
        "--unsmarten-punctuation",
        "--no-chapters-in-toc",
        "--title",
        novel.title,
        "--authors",
        novel.authors,
        "--comments",
        novel.synopsis,
        "--language",
        novel.language,
        "--tags",
        ",".join(novel.tags),
        "--series",
        novel.title,
        "--publisher",
        novel.url,
        "--book-producer",
        "Lightnovel Crawler",
        "--enable-heuristics",
        "--disable-renumber-headings",
    ]

    if novel.cover_available:
        args += ["--cover", ctx.files.resolve(novel.cover_file)]
    if artifact.format == OutputFormat.pdf:
        args += [
            "--paper-size",
            "letter",
            "--pdf-page-numbers",
            "--pdf-hyphenate",
            "--pdf-header-template",
            '<p style="text-align:center; color:#555; font-size:0.9em">⦗ _TITLE_ &mdash; _SECTION_ ⦘</p>',
        ]

    __ebook_convert(*args)

    if not tmp_file.exists():
        raise ServerErrors.failed_creating_artifact

    out_file.parent.mkdir(parents=True, exist_ok=True)
    tmp_file.rename(out_file)
    logger.info("Created: %s", out_file.name)
