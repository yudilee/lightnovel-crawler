import logging
from abc import abstractmethod

from ...exceptions import FallbackToBrowser, ScraperErrorGroup
from .general import GeneralBrowserTemplate

logger = logging.getLogger(__name__)


class LoginBrowserTemplate(GeneralBrowserTemplate):
    """Attempts to crawl using cloudscraper first, if failed use the browser."""

    def login(self, username_or_email: str, password_or_token: str) -> None:
        try:
            return self.login_in_soup(username_or_email, password_or_token)
        except ScraperErrorGroup:
            return self.login_in_browser(username_or_email, password_or_token)

    def login_in_soup(self, username_or_email: str, password_or_token: str) -> None:
        """Login to the website using the scraper"""
        raise FallbackToBrowser()

    @abstractmethod
    def login_in_browser(self, username_or_email: str, password_or_token: str) -> None:
        """Login to the website using the browser"""
        raise NotImplementedError()
