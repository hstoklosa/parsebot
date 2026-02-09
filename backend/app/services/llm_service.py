import json
from typing import Dict, Any

from openai import AsyncOpenAI

from app.core.config import settings

openai_client = AsyncOpenAI(
    api_key=settings.OPENAI_API_KEY,
    base_url=settings.OPENAI_BASE_URL
)


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
    extracted_data = json.loads(extracted_text)
    return extracted_data
