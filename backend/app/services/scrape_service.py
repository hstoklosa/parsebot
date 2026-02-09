import httpx

from fastapi import HTTPException
from bs4 import BeautifulSoup


async def get_website_content(url: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            clean_response = clean_content(response.text)
            return clean_response
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch {url}: {str(e)}")


def clean_content(content: str):
    soup = BeautifulSoup(content, "lxml")
    text = soup.get_text(separator='\n', strip=True)
    return text
