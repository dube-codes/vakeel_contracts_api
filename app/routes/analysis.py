from fastapi import APIRouter, HTTPException, status
from config import GEMINI_API_KEY
from database import contracts_collection
from bson import ObjectId

router = APIRouter(prefix="/api/analysis", tags=["Analysis"])


@router.post("/analyze/{contract_id}")
async def analyze_contract(contract_id: str):
    """Analyze a contract using AI and return insights.!"""

    if not GEMINI_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI API key is not configured..!",
        )

    contract = contracts_collection.find_one({"_id": ObjectId(contract_id)})
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contract not found with Id: {contract_id}",
        )

    if not contract.get("text_content"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract has no text content to analyze.!",
        )

    contracts_collection.update_one(
        {"_id": ObjectId(contract_id)}, {"$set": {"analysis_status": "in_progress"}}
    )

    result = await analyzing_contract(contract_id, contract["text_content"])


@router.get("/")
def analysis_list():
    pass
