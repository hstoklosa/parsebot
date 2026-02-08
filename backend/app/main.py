import json
import httpx
from typing import Dict, Any, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from bs4 import BeautifulSoup
from openai import AsyncOpenAI

from app.core.config import settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ExtractRequest(BaseModel):
    url: str
    prompt: str

class ExtractResponse(BaseModel):
    data: List[Dict[str, Any]]
    # data: str
    schema_used: Dict[str, Any]


openai_client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL
)


async def get_website_content(url: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch {url}: {str(e)}")


def clean_content(content: str):
    soup = BeautifulSoup(content, "lxml")
    text = soup.get_text(separator='\n', strip=True)
    return text


async def generate_schema(prompt: str, text_content: str):
    schema_prompt = f"""Based on this user request {prompt}

And this sample of the website content:
{text_content}

Generate a JSON schema (as a simple dict of field_name: description) that would best capture the requested data from the website content.

For example:

{{
    "title": "title of the article"
    "time_published": "time published of the article"
    "author": "author of the article"
    "content": "content of the article"
}}

Return ONLY a valid JSON object with the schema, no explanation and no markdown code block."""
    response = await openai_client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a data extraction expert. Return only valid JSON."},
            {"role": "user", "content": schema_prompt}
        ],
    )
    schema_text = response.choices[0].message.content
    schema = json.loads(schema_text)
    return schema
    

async def extract_schema_data(text_content: str, schema: Dict[str, Any]):
    extract_prompt = f"""Extract data from the following website content according to this schema:

Schema:
{json.dumps(schema, indent=2)}

Website Content:
{text_content}

Extract the data and return ONLY a valid JSON object matching the schema fields. No explanation, no markdown code blocks."""
    
    response = await openai_client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "You are a data extraction expert. Extract structured data from text and return only valid JSON matching the provided schema."},
            {"role": "user", "content": extract_prompt}
        ],
    )
    
    extracted_text = response.choices[0].message.content
    print(extracted_text)
    extracted_data = json.loads(extracted_text)
    print(extracted_data)
    return extracted_data


@app.post("/")
async def extract_data(data: ExtractRequest):
    html_content = await get_website_content(data.url)
    text_content = clean_content(html_content)
    if not text_content:
        raise HTTPException(status_code=400, detail="Failed to scrape website")

    json_schema = await generate_schema(data.prompt, text_content)
    if not json_schema:
        raise HTTPException(status_code=400, detail="Failed to generate schema")

    extracted_data = await extract_schema_data(text_content, json_schema)
    
    return ExtractResponse(data=extracted_data, schema_used=json_schema)