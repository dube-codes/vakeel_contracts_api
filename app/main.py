from fastapi import FastAPI
from database import init_db
from routes.contracts import router as contract_router
from routes.analysis import router as analysis_router

vers = "1.0.0"
app = FastAPI(
    title="Vakeel Contracts API",
    description="AI-Powered Contract Analysis using Gemini",
    version=vers,
)


@app.on_event("startup")
async def startup_event():
    init_db()


@app.get("/")
async def index():
    return {
        "app": "Vakeel Contracts API",
        "version": vers,
        "endpoints": {
            "POST /contracts/upload": "Upload a PDF or TXT contract for analysis",
            "GET /contracts/": "Retrieve a list of all uploaded contracts",
            "GET /contracts/{id}": "Retrive details of a specific contract by ID",
            "POST /analysis/analyse/{contract_id}": "Analyze a contract using AI and return insights",
            "GET /analysis/{analysis_id}": "Retrive the results of a specific analysis by ID",
            "GET /analysis/contract/{contract_id}": "Retrive a list of all analysis performed for specific contract",
        },
    }


app.include_router(contract_router)
app.include_router(analysis_router)
