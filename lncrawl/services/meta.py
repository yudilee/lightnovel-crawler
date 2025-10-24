import base64
import io
import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Dict

from fastapi import APIRouter
from fastapi.responses import FileResponse
from PIL import Image

from ..context import ctx
from ..core.app import App
from ..core.download_chapters import get_chapter_file
from ..core.metadata import META_FILE_NAME
from ..dao import Novel
from ..models import Chapter, MetaInfo
from ..utils.algo import binary_search
from ..utils.url_tools import extract_host
from ..exceptions import ServerError, ServerErrors
from ..server.models.meta import SupportedSource
from ..server.models.novel import NovelChapter, NovelChapterContent, NovelVolume

logger = logging.getLogger(__name__)

# The root router
router = APIRouter()


class MetadataService:
    def __init__(self) -> None:
        pass

    @lru_cache()
    def list_supported_sources(self):
        for url, item in ctx.sources.list(include_rejected=True):
            domain = extract_host(url)
            yield SupportedSource(
                url=url,
                domain=domain,
                has_mtl=item.info.has_mtl,
                has_manga=item.info.has_manga,
                can_login=item.info.can_login,
                can_logout=item.info.can_logout,
                can_search=item.info.can_search,
                is_disabled=(domain in ctx.sources.rejected),
                disable_reason=ctx.sources.rejected.get(domain, ''),
            )

    @lru_cache()
    def resolve_output_path(self, novel_id: str):
        with ctx.db.session() as sess:
            novel = sess.get(Novel, novel_id)
            if not novel:
                raise ServerErrors.no_such_novel

            output_path = novel.extra.get('output_path')
            if output_path and Path(output_path).is_dir():
                return Path(output_path)

            if not novel.title:
                raise ServerErrors.no_novel_title

            with App() as app:
                app.user_input = novel.url
                app.prepare_search()

                crawler = app.crawler
                if not crawler:
                    logger.error(f'No crawler for: {novel.url}')
                    raise ServerErrors.server_error

                crawler.novel_url = novel.url
                crawler.novel_title = novel.title
                app.prepare_novel_output_path()

                output_path = Path(app.output_path)

            if not output_path.is_dir():
                raise ServerErrors.no_novel_output_path

            novel.extra = dict(novel.extra)
            novel.extra['output_path'] = str(output_path)
            sess.add(novel)
            sess.commit()

            return output_path

    def load_novel_meta(self, output_path: Path):
        meta_file = output_path / META_FILE_NAME
        if not meta_file.is_file():
            raise ServerErrors.no_metadata_file
        with open(meta_file, "r", encoding="utf-8") as fp:
            data = json.load(fp)
            meta = MetaInfo(**data)
        if not meta.novel or not meta.session:
            raise ServerErrors.malformed_metadata_file
        return meta.session, meta.novel

    # NOTE: might be require in future
    # def save_novel_meta(self, meta: MetaInfo, output_path: Path):
    #     meta_file = output_path / META_FILE_NAME
    #     output_path.mkdir(parents=True, exist_ok=True)
    #     meta.to_json(meta_file, encoding="utf-8", indent=2)

    def convert_chapter(self, chapter: Chapter, output_path: Path, pack_by_volume: bool) -> NovelChapter:
        json_file = get_chapter_file(
            chapter=chapter,
            output_path=str(output_path),
            pack_by_volume=pack_by_volume,
        )
        relative_path = str(json_file.relative_to(output_path))
        hash = base64.urlsafe_b64encode(relative_path.encode()).decode()
        return NovelChapter(
            id=chapter.id,
            title=chapter.title,
            hash=hash,
        )

    def get_novel_toc(self, novel_id: str):
        try:
            output_path = self.resolve_output_path(novel_id)
            session, novel = self.load_novel_meta(output_path)
        except ServerError:
            return []

        volumes: Dict[int, NovelVolume] = {}
        for vol in novel.volumes:
            volumes[vol.id] = NovelVolume(
                id=vol.id,
                title=vol.title,
            )

        for chapter in novel.chapters:
            if not chapter.volume or not chapter.success:
                continue

            volume = volumes.get(chapter.volume)
            if not volume:
                continue

            nove_chapter = self.convert_chapter(
                chapter,
                output_path,
                session.pack_by_volume,
            )
            volume.chapters.append(nove_chapter)

        return list(volumes.values())

    def get_novel_chapter_content(self, novel_id: str, hash: str):
        output_path = self.resolve_output_path(novel_id)
        session, novel = self.load_novel_meta(output_path)

        file_path = base64.urlsafe_b64decode(hash).decode()
        json_file = (Path(output_path) / file_path).resolve()
        if not json_file.is_file():
            raise ServerErrors.not_found

        with open(json_file, 'r', encoding='utf-8') as fp:
            content = json.load(fp)
            if not isinstance(content, dict):
                raise ServerErrors.malformed_json_file

        result = NovelChapterContent(
            id=content['id'],
            body=content['body'],
            title=content['title'],
            volume_id=content['volume'],
            volume=content['volume_title'],
        )

        index = binary_search(
            novel.chapters,
            content,
            compare=lambda a, b: a['id'] < b['id']
        )
        if index is None:
            raise ServerErrors.server_error

        prev = index - 1
        while prev >= 0:
            chapter = novel.chapters[prev]
            if not chapter.success:
                prev -= 1
                continue
            result.prev = self.convert_chapter(
                chapter,
                output_path,
                session.pack_by_volume,
            )
            break

        next = index + 1
        while next < len(novel.chapters):
            chapter = novel.chapters[next]
            if not chapter.success:
                next += 1
                continue
            result.next = self.convert_chapter(
                chapter,
                output_path,
                session.pack_by_volume,
            )
            break

        return result

    def get_novel_cover(self, novel_id: str):
        with ctx.db.session() as sess:
            novel = sess.get(Novel, novel_id)
            if not novel:
                raise ServerErrors.no_such_novel
            cover_url = novel.cover

        output_path = self.resolve_output_path(novel_id)
        file_path = output_path / 'cover.jpg'
        if not file_path.is_file():
            if not cover_url or not cover_url.startswith('http'):
                raise ServerErrors.no_novel_cover

            response = ctx.http.image(cover_url)
            content_type = response.headers.get("Content-Type")
            if not content_type:
                raise ServerErrors.invalid_image_response

            with Image.open(io.BytesIO(response.content)) as img:
                if img.mode not in ("L", "RGB", "YCbCr", "RGBX"):
                    if img.mode == "RGBa":
                        img = img.convert("RGBA").convert("RGB")
                    else:
                        img = img.convert("RGB")
                file_path.parent.mkdir(parents=True, exist_ok=True)
                img.save(file_path.as_posix(), "JPEG", optimized=True)

        return FileResponse(
            file_path,
            media_type='image/jpeg',
            headers={
                "Cache-Control": "public, max-age=31536000, immutable"
            }
        )
