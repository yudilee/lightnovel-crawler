from urllib.error import URLError

from fastapi import HTTPException
from PIL import UnidentifiedImageError
from requests.exceptions import RequestException
from urllib3.exceptions import HTTPError

from .cloudscraper.exceptions import CloudflareException


class LNException(Exception):
    pass


class FallbackToBrowser(Exception):
    pass


ScraperErrorGroup = (
    URLError,
    HTTPError,
    CloudflareException,
    RequestException,
    FallbackToBrowser,
    UnidentifiedImageError,
)

RetryErrorGroup = (
    URLError,
    HTTPError,
    CloudflareException,
    RequestException,
    UnidentifiedImageError,
)


class ServerError(HTTPException, LNException):
    def __init__(self, status=400, *args, **kwargs) -> None:
        super().__init__(status, *args, **kwargs)

    def with_detail(self, detail: str) -> 'ServerError':
        self.detail = detail
        return self


class ServerErrors:
    forbidden = ServerError(403, 'Forbidden')
    not_found = ServerError(404, 'Not Found')
    unauthorized = ServerError(401, 'Unauthorized')
    server_error = ServerError(500, 'Internal Server Error')

    wrong_password = ServerError(401, 'Wrong password')
    inactive_user = ServerError(403, 'User is inactive')
    user_exists = ServerError(409, "User already exists")
    email_already_verified = ServerError(409, "Email is already verified")
    can_not_delete_self = ServerError(403, 'You are not allowed to delete your own account')

    invalid_url = ServerError(422, "Invalid URL")
    no_chapters_to_download = ServerError(422, 'No chapters to download')
    no_volumes_to_download = ServerError(422, 'No volumes to download')
    no_images_to_download = ServerError(422, 'No images to download')
    no_artifacts_to_create = ServerError(422, 'No artifacts to create')
    sort_column_is_none = ServerError(422, "No such field to sort by")
    duplicate_output_format = ServerError(422, "Duplicate formats are not allowed")

    no_such_user = ServerError(404, "No such user")
    no_such_job = ServerError(404, "No such job")
    no_such_file = ServerError(404, "No such file")
    no_such_novel = ServerError(404, "No such novel")
    no_such_tag = ServerError(404, "No such tag")
    no_such_secret = ServerError(404, "No such secret")
    no_such_volume = ServerError(404, "No such volume")
    no_such_chapter = ServerError(404, "No such chapter")
    no_such_artifact = ServerError(404, "No such artifact")
    no_artifact_file = ServerError(404, "Artifact file not available")

    no_novel_title = ServerError(500, "Novel has no title")
    no_chapters = ServerError(500, 'No chapters found')
    no_volumes = ServerError(500, 'No volumes found')
    no_images = ServerError(500, 'No images found')
    unable_to_resume_job = ServerError(500, "Unable to resume Job")
    no_novel_cover = ServerError(500, "Novel cover is not available")
    invalid_image_response = ServerError(500, "Invalid image response")
    smtp_server_unavailable = ServerError(500, "SMTP server is not available")
    smtp_server_login_fail = ServerError(500, "Failed to login to SMTP server")
    email_send_failure = ServerError(500, "Failed to send email")
    canceled_by_signal = ServerError(500, "Canceled by signal")
    calibre_exe_not_found = ServerError(500, "No calibre executables")
    failed_creating_artifact = ServerError(500, "Failed to create artifact")
    format_not_available = ServerError(500, "The output format is not available")
    host_rejected = ServerError(500, 'The requested domain is rejected')
    source_not_loaded = ServerError(500, 'Sources are not loaded')
    no_crawler = ServerError(500, "No crawler found for the domain")
