import logging
import re
import zipfile
from pathlib import Path
from threading import Event

from bs4 import BeautifulSoup

from ...context import ctx
from ...dao import Artifact
from ...exceptions import ServerErrors
from ...utils.platforms import Platform

logger = logging.getLogger(__name__)


def extract_text(html: str) -> str:
    html = html.replace("</p><p", "</p>\n<p")
    soup = BeautifulSoup(html, "lxml")
    text = "\n\n".join(soup.stripped_strings)
    if Platform.posix:
        text = re.sub(r"[\r\n]+", '\n', text)
    return text


def make_text(working_dir: Path, artifact: Artifact, signal=Event()):
    out_file = ctx.files.resolve(artifact.output_file)
    tmp_file = working_dir / out_file.name
    if out_file.exists():
        return

    novel = ctx.novels.get(artifact.novel_id)
    with zipfile.ZipFile(tmp_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        if signal.is_set():
            raise ServerErrors.canceled_by_signal
        for volume in ctx.volumes.list(artifact.novel_id):
            if signal.is_set():
                raise ServerErrors.canceled_by_signal
            for chapter in ctx.chapters.list(volume_id=volume.id):
                if chapter.is_available:
                    content = ctx.files.load_text(chapter.content_file)
                    content = chapter.title + '\n\n' + extract_text(content)
                    chapter_file = f'{volume.serial:03}/{chapter.serial:05}.txt'
                    zipf.writestr(chapter_file, content.encode())

        if signal.is_set():
            raise ServerErrors.canceled_by_signal
        for image in ctx.chapter_images.list(novel_id=artifact.novel_id):
            if image.is_available:
                content = ctx.files.load(image.image_file)
                zipf.writestr(f'images/{image.id}.jpg', content)

        if signal.is_set():
            raise ServerErrors.canceled_by_signal
        if novel.cover_available:
            content = ctx.files.load(novel.cover_file)
            zipf.writestr('cover.jpg', content)

        if signal.is_set():
            raise ServerErrors.canceled_by_signal
        meta_text = '\n'.join([
            f"{novel.url}",
            '',
            "-" * 40,
            '',
            novel.title,
            f"by, {novel.authors}",
            '',
            "-" * 40,
            '',
            extract_text(novel.synopsis),
            '',
            "-" * 40,
            '',
            f"Tags: {', '.join(map(lambda s: s.title(), novel.tags))}",
            f"Volumes: {novel.volume_count}",
            f"Chapters: {novel.chapter_count}",
        ])
        zipf.writestr('meta.txt', meta_text.encode())

    out_file.parent.mkdir(parents=True, exist_ok=True)
    tmp_file.rename(out_file)
    logger.info(f'Created: {out_file}')
