from fastapi import APIRouter, HTTPException, status
from config import GEMINI_API_KEY
from database import contracts_collection
from bson import ObjectId
from service.gemini_analyze import analyzing_contract
from database import analysis_collection

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

    doc = result.model_dump()
    insert_result = analysis_collection.insert_one(doc)
    result.id = str(insert_result.inserted_id)

    contracts_collection.update_one(
        {"_id": ObjectId(contract_id)}, {"$set": {"analysis_status": "completed"}}
    )

    return {
        "message": "contract analyzed successfully.!",
        "analysis": result.model_dump(),
        "id": result.id,
    }


@router.get("/{analysis_id}")
def analysis_by_id(analysis_id: str):
    """Retrieve the results of a specific analysis by Id.!"""

    analysis = analysis_collection.find_one({"_id": ObjectId(analysis_id)})

    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Analysis not found with the Id: {analysis_id}",
        )

    analysis["id"] = str(analysis.pop("_id"))
    return {"analysis": analysis}


@router.get("/")
def list_analysis():
    """List all analysis performed.!"""

    analysis = []
    for doc in analysis_collection.find({}):
        doc["id"] = str(doc.pop("_id"))
        analysis.append(doc)

    return {"analysis": analysis}


@router.get("/contract/{contract_id}")
def get_analysis_for_contract(contract_id: str):
    """Get all analysis for a specific contract.!"""

    analysis = []

    cursor = analysis_collection.find({"contract_id": contract_id})

    for doc in cursor:
        doc["id"] = str(doc.pop("_id"))
        analysis.append(doc)

    return {"analysis": analysis, "total": len(analysis)}
