import json
import logging
import os
import time
import uuid
from datetime import datetime
from decimal import Decimal
from functools import cached_property
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union, cast

import dotenv
import typer

T = TypeVar('T')

logger = logging.getLogger(__name__)

ROOT_DIR = Path(__file__).parent.absolute()
APP_DIR = Path(
    typer.get_app_dir(
        "Lightnovel Crawler",
        force_posix=True,
        roaming=True,
    )
).absolute()
DEFAULT_CONFIG_FILE = APP_DIR / 'config.json'


# ------------------------------------------------------------------ #
#                            Section Base                            #
# ------------------------------------------------------------------ #
class _Section(object):
    section: str

    def __init__(self, parent: 'Config') -> None:
        self.root = parent

    def _get(self, key: str, default: Union[T, Callable[[], Any]]) -> T:
        return self.root.get(self.section, key, default)

    def _set(self, key: str, value: Any) -> None:
        logger.debug(f'[{self.section}] seting "{key}" = {value}')
        self.root.set(self.section, key, value)


def _serialize(obj: object) -> Any:
    if isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    if isinstance(obj, (list, tuple, set)):
        return [_serialize(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _serialize(v) for k, v in obj.items()}
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    return str(obj)  # fallback for unknown types


def _deserialize(val: Any, typ: Type[T]) -> T:
    if val is None:
        return cast(T, None)
    if typ in (str, int, float, bool):
        return typ(val)  # type: ignore
    if typ == Decimal:
        return cast(T, Decimal(val))
    if typ == datetime:
        return cast(T, datetime.fromisoformat(val))
    if typ in (list, tuple, set):
        seq = json.loads(val) if isinstance(val, str) else val
        return cast(T, typ(seq))   # type: ignore
    if typ == dict:
        return cast(T, json.loads(val) if isinstance(val, str) else val)
    return cast(T, val)


def _snapshot(obj: object) -> Dict[str, Any]:
    out = {}
    for name in dir(obj):
        if name.startswith("_"):
            continue
        attr = getattr(type(obj), name, None)
        if isinstance(attr, property):
            out[name] = _serialize(getattr(obj, name))
        elif isinstance(attr, cached_property):
            value = getattr(obj, name)
            if isinstance(value, _Section):
                out[value.section] = _snapshot(value)
    return out


# ------------------------------------------------------------------ #
#                             Root Config                            #
# ------------------------------------------------------------------ #
class Config(object):
    def __init__(self) -> None:
        dotenv.load_dotenv()
        self.config_file = DEFAULT_CONFIG_FILE

    @cached_property
    def app(self):
        return AppConfig(self)

    @cached_property
    def db(self):
        return DatabaseConfig(self)

    @cached_property
    def crawler(self):
        return CrawlerConfig(self)

    @cached_property
    def server(self):
        return ServerConfig(self)

    @cached_property
    def cloud(self):
        return CloudConfig(self)

    @cached_property
    def mail(self):
        return MailConfig(self)

    @cached_property
    def discord(self):
        return DiscordConfig(self)

    # -------------------------------------------------------------- #

    def load(self, file: Optional[Path] = None) -> None:
        """
        Loads configurations from given file, env var or default config.

        - Loads from param `file` if provided
        - Loads from `LNCRAWL_CONFIG` env var if available
        - Loads from default config otherwise
        """
        env_file = os.getenv('LNCRAWL_CONFIG')
        if not file and env_file:
            file = Path(env_file)
        self.config_file = file or DEFAULT_CONFIG_FILE
        logger.info(f'Config file: {self.config_file}')
        if self.config_file.is_file():
            self._data = json.loads(
                self.config_file.read_text(encoding="utf-8")
            )
        else:
            self._data = {}
        self._data = _snapshot(self)
        self.save()

    def save(self) -> None:
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        tid = time.thread_time_ns() % 1000
        tmp = self.config_file.with_suffix(f'.json.tmp{tid}')
        content = json.dumps(self._data, indent=2, ensure_ascii=False)
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, self.config_file)
        logger.debug(f'Config saved: {self.config_file}')

    def get(self, section: str, key: str, default: Union[T, Callable[[], Any]]) -> Any:
        sub: dict = self._data.setdefault(section, {})
        if key not in sub:
            if callable(default):
                sub[key] = default()
            else:
                sub[key] = default
        return _deserialize(sub[key], type(sub[key]))

    def set(self, section: str, key: str, value: Any) -> None:
        sub: dict = self._data.setdefault(section, {})
        if value is None:
            sub.pop(key, None)
        else:
            sub[key] = _serialize(value)
        self.save()


# ------------------------------------------------------------------ #
#                             App Section                            #
# ------------------------------------------------------------------ #
class AppConfig(_Section):
    section = "app"
    name = "Lightnovel Crawler"
    _secret = str(uuid.uuid4())

    @cached_property
    def version(self) -> str:
        return (ROOT_DIR / "VERSION").read_text(encoding="utf8").strip()

    def __output_path(self) -> str:
        return str(Path("Lightnovels").absolute())

    @property
    def output_path(self) -> Path:
        return Path(self._get("output_path", self.__output_path))

    @output_path.setter
    def output_path(self, path: Optional[Path]) -> None:
        self._set("output_path", str(path) if path else None)

    @property
    def history_limit_per_user(self) -> int:
        '''Number of items to store per user'''
        return self._get("history_limit_per_user", 10000)

    @history_limit_per_user.setter
    def history_limit_per_user(self, v: Optional[int]) -> None:
        self._set("history_limit_per_user", v)

    @property
    def secret_key(self) -> str:
        return self._get("secret_key", self._secret)

    @secret_key.setter
    def secret_key(self, v: Optional[str]) -> None:
        self._set("secret_key", v)

# ------------------------------------------------------------------ #
#                          Database Section                          #
# ------------------------------------------------------------------ #


class DatabaseConfig(_Section):
    section = "database"

    def __url(self) -> str:
        return f"sqlite:///{(APP_DIR / 'sqlite.db').resolve().as_posix()}"

    @property
    def url(self) -> str:
        return self._get("url", self.__url)

    @url.setter
    def url(self, url: Optional[str]) -> None:
        self._set("url", url)

    @property
    def admin_email(self) -> str:
        return self._get("admin_email", "admin")

    @admin_email.setter
    def admin_email(self, v: Optional[str]) -> None:
        self._set("admin_email", v)

    @property
    def admin_password(self) -> str:
        return self._get("admin_password", "admin")

    @admin_password.setter
    def admin_password(self, v: Optional[str]) -> None:
        self._set("admin_password", v)


# ------------------------------------------------------------------ #
#                           Crawler Section                          #
# ------------------------------------------------------------------ #
class CrawlerConfig(_Section):
    section = "crawler"

    @property
    def ignore_images(self) -> bool:
        return self._get("ignore_images", False)

    @property
    def add_source_url_in_chapter_content(self) -> bool:
        return self._get("add_source_url_in_chapter_content", False)

    @property
    def selenium_grid(self) -> str:
        return self._get("selenium_grid", "")

    @selenium_grid.setter
    def selenium_grid(self, url: Optional[str]) -> None:
        self._set("selenium_grid", url)

    @cached_property
    def local_index_file(self) -> Path:
        for dir in [ROOT_DIR, ROOT_DIR.parent]:
            file = dir / "sources" / "_index.json"
            if file.is_file():
                return file
        raise ValueError('No local index file')

    @cached_property
    def user_index_file(self) -> Path:
        return APP_DIR / "sources" / "_index.json"

    @property
    def index_file_download_url(self) -> str:
        return "https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/dev/sources/_index.zip"

    @property
    def runner_cooldown(self) -> int:
        '''Crawler job cooldown in seconds'''
        return self._get("runner_cooldown", 1)

    @runner_cooldown.setter
    def runner_cooldown(self, v: Optional[int]) -> None:
        self._set("runner_cooldown", v)

    @property
    def cleaner_cooldown(self) -> int:
        '''Cleaner job cooldown in seconds'''
        return self._get("cleaner_cooldown", lambda: 6 * 3600)

    @cleaner_cooldown.setter
    def cleaner_cooldown(self, v: Optional[int]) -> None:
        self._set("cleaner_cooldown", v)

    @property
    def disk_size_limit(self) -> int:
        '''Maximum disk size limit of crawled data in bytes'''
        mb = self._get("disk_size_limit_mb", 0)
        return mb * 1024 * 1024

    @disk_size_limit.setter
    def disk_size_limit(self, bytes_val: Optional[int]) -> None:
        mb = None if bytes_val is None else bytes_val // (1024 * 1024)
        self._set("disk_size_limit_mb", mb)


# ------------------------------------------------------------------ #
#                           Server Section                           #
# ------------------------------------------------------------------ #
class ServerConfig(_Section):
    section = "server"

    @property
    def base_url(self) -> str:
        return self._get("base_url", "http://localhost:8080").strip("/")

    @base_url.setter
    def base_url(self, v: Optional[str]) -> None:
        self._set("base_url", v)

    @property
    def token_secret(self) -> str:
        return self._get("token_secret", "")

    @token_secret.setter
    def token_secret(self, v: Optional[str]) -> None:
        self._set("token_secret", v)

    @property
    def token_algo(self) -> str:
        return self._get("token_algorithm", "HS256")

    @token_algo.setter
    def token_algo(self, v: Optional[str]) -> None:
        self._set("token_algorithm", v)

    @property
    def token_expiry(self) -> int:
        return self._get("token_expiry", lambda: 7 * 24 * 60)

    @token_expiry.setter
    def token_expiry(self, v: Optional[int]) -> None:
        self._set("token_expiry", v)


# ------------------------------------------------------------------ #
#                         Third Party Section                        #
# ------------------------------------------------------------------ #
class CloudConfig(_Section):
    section = "cloud"

    @property
    def store(self) -> str:
        return self._get("store", "ANONFILES")

    @store.setter
    def store(self, v: Optional[str]) -> None:
        self._set("store", v)


# ------------------------------------------------------------------ #
#                          Discord Section                           #
# ------------------------------------------------------------------ #
class DiscordConfig(_Section):
    section = "discord"

    @property
    def token(self) -> str:
        return self._get("token", "")

    @token.setter
    def token(self, v: Optional[str]) -> None:
        self._set("token", v)


# ------------------------------------------------------------------ #
#                            Mail Section                            #
# ------------------------------------------------------------------ #
class MailConfig(_Section):
    section = "mail"

    @property
    def smtp_server(self) -> str:
        return self._get("smtp_server", "localhost")

    @smtp_server.setter
    def smtp_server(self, v: Optional[str]) -> None:
        self._set("smtp_server", v)

    @property
    def smtp_port(self) -> int:
        return self._get("smtp_port", 1025)

    @smtp_port.setter
    def smtp_port(self, v: Optional[int]) -> None:
        self._set("smtp_port", v)

    @property
    def smtp_username(self) -> str:
        return self._get("smtp_username", "")

    @smtp_username.setter
    def smtp_username(self, v: Optional[str]) -> None:
        self._set("smtp_username", v)

    @property
    def smtp_password(self) -> str:
        return self._get("smtp_password", "")

    @smtp_password.setter
    def smtp_password(self, v: Optional[str]) -> None:
        self._set("smtp_password", v)

    @property
    def smtp_sender(self) -> str:
        return self._get("smtp_sender", "")

    @smtp_sender.setter
    def smtp_sender(self, v: Optional[str]) -> None:
        self._set("smtp_sender", v)
