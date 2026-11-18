import httpx
import json
from config import GEMINI_API_KEY
from service.prompt import CONTRACT_ANALYSIS_PROMPT

GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent"


async def analyzing_contract(contract_id: str, text_content: str):
    prompt = CONTRACT_ANALYSIS_PROMPT.format(contract_text=text_content[:15000])

    async with httpx.AsyncClient() as client:
        response = await client.post(
            GEMINI_URL,
            params={"key": GEMINI_API_KEY},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.3,
                    "maxOutputToken": 4096,
                },
            },
            timeout=60.0,
        )

        response.raise_for_status()
        data = response.json()
