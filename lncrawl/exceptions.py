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


class ServerErrors:
    forbidden = ServerError(403, 'Forbidden')
    not_found = ServerError(404, 'Not Found')
    unauthorized = ServerError(401, 'Unauthorized')
    server_error = ServerError(500, 'Internal Server Error')

    invalid_url = ServerError(422, "Invalid URL")
    sort_column_is_none = ServerError(422, "No such field to sort by")

    no_such_user = ServerError(404, "No such user")
    inactive_user = ServerError(403, 'User is inactive')
    user_exists = ServerError(409, "User already exists")
    wrong_password = ServerError(401, 'Wrong password')
    can_not_delete_self = ServerError(403, 'You are not allowed to delete your own account')

    no_such_job = ServerError(404, "No such job")
    duplicate_output_format = ServerError(422, "Duplicate formats are not allowed")

    no_such_novel = ServerError(404, "No such novel")
    no_such_artifact = ServerError(404, "No such artifact")
    no_artifact_file = ServerError(404, "Artifact file not available")
    email_already_verified = ServerError(409, "Email is already verified")

    no_novel_title = ServerError(500, "Novel has no title")
    unable_to_resume_job = ServerError(500, "Unable to resume Job")
    no_novel_cover = ServerError(500, "Novel cover is not available")
    invalid_image_response = ServerError(500, "Invalid image response")
    smtp_server_unavailable = ServerError(500, "SMTP server is not available")
    smtp_server_login_fail = ServerError(500, "Failed to login to SMTP server")
    email_send_failure = ServerError(500, "Failed to send email")
    no_novel_output_path = ServerError(500, "Novel output path is not found")
    malformed_json_file = ServerError(500, 'Malformed JSON file')
    no_metadata_file = ServerError(500, "Novel metadata file is not found")
    malformed_metadata_file = ServerError(500, "Novel metadata file is malformed")
