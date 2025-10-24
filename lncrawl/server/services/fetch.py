import httpx
from bs4 import BeautifulSoup

from ...exceptions import ServerErrors


class FetchService:
    def __init__(self) -> None:
        pass

    async def website_title(self, url: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            BeautifulSoup()

    async def image(self, image_url: str):
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url)
            if response.status_code >= 400:
                raise ServerErrors.invalid_image_response
            return response
