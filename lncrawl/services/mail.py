import logging
from email.mime.text import MIMEText
from smtplib import SMTP
from typing import Optional

import lxml.etree
import lxml.html

from ..assets import emails
from ..context import ctx
from ..dao import Job, User
from ..dao.enums import JobType
from ..exceptions import ServerErrors

logger = logging.getLogger(__name__)


class MailService:
    def __init__(self) -> None:
        self.server: Optional[SMTP] = None
        self.sender = (
            ctx.config.mail.smtp_sender
            or ctx.config.mail.smtp_username
        )

    def close(self):
        if self.server:
            self.server.close()
            self.server = None

    def prepare(self):
        if self.server:
            return

        smtp_server = ctx.config.mail.smtp_server
        smtp_port = ctx.config.mail.smtp_port
        smtp_user = ctx.config.mail.smtp_username
        smtp_pass = ctx.config.mail.smtp_password
        if not all([smtp_server, smtp_port, smtp_user, smtp_pass]):
            raise ServerErrors.smtp_server_unavailable

        try:
            logger.info('Preparing mail server')
            self.server = SMTP(smtp_server, smtp_port)
            self.server.starttls()
            self.server.login(smtp_user, smtp_pass)
            logger.info(f'Connected with SMTP server: {smtp_server}')
        except Exception as e:
            self.close()
            raise ServerErrors.smtp_server_login_fail from e

    def send(self, email: str, subject: str, html_body: str):
        # Prepare mail server
        self.prepare()

        # Minify HTML
        tree = lxml.html.fromstring(html_body)
        minified = lxml.etree.tostring(tree, encoding='unicode', pretty_print=False)

        # Create mail body
        msg = MIMEText(minified, 'html')
        msg['Subject'] = subject
        msg['From'] = self.sender
        msg['To'] = email

        try:
            assert self.server
            self.server.sendmail(msg['From'], [msg['To']], msg.as_string())
        except Exception as e:
            raise ServerErrors.email_send_failure from e

    def send_otp(self, email: str, otp: str):
        subject = f'OTP ({otp})'
        body = emails.otp_template().render(otp=otp)
        self.send(email, subject, body)

    def send_reset_password_link(self, email: str, link: str):
        subject = 'Reset Password'
        body = emails.repass_template().render(link=link)
        self.send(email, subject, body)

    def send_full_novel_job_success(self, user: User, job: Job):
        if job.type != JobType.FULL_NOVEL:
            return

        if not ctx.users.is_verified(user.email):
            return

        novel_id = job.extra.get('novel_id')
        if not novel_id:
            return

        novel = ctx.novels.get(novel_id)
        artifacts = ctx.artifacts.list(job_id=job.id)

        base_url = ctx.config.server.base_url
        job_url = f'{base_url}/job/{job.id}'
        novel_title = novel.title or "Unknown Title"
        novel_authors = novel.authors or "Unknown Author"
        chapter_count = novel.chapter_count or "?"
        volume_count = novel.volume_count or "?"
        novel_synopsis = novel.synopsis or "No synopsis available."

        token = ctx.users.generate_token(user)
        artifacts = [
            {
                'format': str(item.format),
                'name': ctx.files.resolve(item.output_file).name,
                'url': f'{base_url}/static/{item.output_file}/download?token={token}',
            } for item in artifacts.items
        ]

        if len(novel_synopsis) > 300:
            novel_synopsis = f'{novel_synopsis[:300]}...'

        body = emails.job_template().render(
            job_url=job_url,
            artifacts=artifacts,
            novel_title=novel_title,
            novel_authors=novel_authors,
            chapter_count=chapter_count,
            volume_count=volume_count,
            novel_synopsis=novel_synopsis,
        )

        self.send(user.email, novel_title, body)
