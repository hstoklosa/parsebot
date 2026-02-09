from fastapi import APIRouter
from app.schemas.extract import ExtractRequest, ExtractResponse
from app.services.scrape_service import get_website_content
from app.services.llm_service import generate_schema, extract_schema_data
from fastapi import HTTPException

router = APIRouter(
    prefix="/extract",
    tags=["extract"],
)

@router.post("/")
async def extract_data(request: ExtractRequest):
    website_content = await get_website_content(request.url)
    if not website_content:
        raise HTTPException(status_code=400, detail="Failed to scrape website")

    json_schema = await generate_schema(request.prompt, website_content)
    if not json_schema:
        raise HTTPException(status_code=400, detail="Failed to generate schema")

    extracted_data = await extract_schema_data(website_content, json_schema)
    
    return ExtractResponse(data=extracted_data, schema_used=json_schema)