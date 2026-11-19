# Vakeel Contracts API

## Project overview

I’m building this as a personal learning project around a Mumbai legal-tech use case: an API for lawyers to upload PDF or TXT contracts and receive AI-generated insights. It extracts the document text, identifies key clauses and risks, and returns recommendations and an overall risk level. Contract documents and analysis results are stored in MongoDB.

## Features

- Upload PDF and TXT files up to 10 MB.
- Extract contract text and calculate page and word counts.
- Store contracts and analysis results in MongoDB.
- Generate summaries, key clauses, risk flags, and recommendations using the Google GenAI SDK.

## Tech stack

- Python
- FastAPI and Uvicorn
- Pydantic
- MongoDB with PyMongo
- PyPDF2
- Google GenAI SDK (`google-genai`)
- python-dotenv
- Docker Compose for a local MongoDB service

`requirements.txt` pins the installed packages, including FastAPI 0.163.1, `google-genai` 3.6.1, PyMongo 4.20.0, PyPDF2 3.0.1, and Uvicorn 0.54.0.

## Project structure

```text
.
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── .env                  # Local settings; ignored by Git
│   ├── routes/
│   │   ├── contracts.py
│   │   └── analysis.py
│   └── service/
│       ├── document_parser.py
│       ├── gemini_analyze.py
│       └── prompt.py
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Database setup and migrations

The app connects to MongoDB and uses the `mydb` database with `contracts` and `analysis` collections. At startup, it creates indexes for `contract_id` and `analysis_id`. There is no separate migration system.

The workspace includes a Compose file with a `mongodb` service. If that file is present in your checkout, start MongoDB from the project root:

```text
docker compose up -d mongodb
```

The service publishes MongoDB on port `27017`. Set `MONGODB_URI` to connect to it. The URI should use `localhost` when the API runs on your machine, and its username and password must match the MongoDB configuration.

## Installation and setup

Clone the repository and enter its folder:

```text
git clone https://github.com/dube-codes/vakeel_contracts_api.git
cd vakeel_contracts_api
```

The workspace uses `venv/` as its virtual environment folder. No Python version is specified in the code or configuration.

### Windows PowerShell

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If script activation is blocked, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

### Windows Command Prompt

```bat
python -m venv venv
venv\Scripts\activate.bat
python -m pip install -r requirements.txt
```

### macOS/Linux (bash/zsh)

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

Create `app/.env` and set the variables below. Start MongoDB before launching the API.

## Environment variables

```dotenv
MONGODB_URI=mongodb://<username>:<password>@localhost:27017/mydb?authSource=admin
GEMINI_API_KEY=<your-gemini-api-key>
```

`app/config.py` reads both variables. The Gemini service creates `genai.Client()` without passing the key explicitly, so the app relies on the SDK's environment-variable handling.

## How to run

From the project root, with the virtual environment active and MongoDB running:

```text
fastapi dev app/main.py
```

Open `http://127.0.0.1:8000/docs` to confirm the API starts and view its interactive documentation.

## API endpoints

All endpoints are unauthenticated.

| Method | Path | Description | Success / declared error statuses | Auth |
|---|---|---|---|---|
| GET | `/` | Return the API name, version, and endpoint summary. | 200 | None |
| POST | `/api/contracts/upload` | Upload and parse a PDF or TXT contract. | 200; 400 for unsupported file types or oversized files | None |
| GET | `/api/contracts/` | List contracts without their extracted text. | 200 | None |
| GET | `/api/contracts/{contract_id}` | Retrieve a contract, including its extracted text. | 200; 400 if not found | None |
| POST | `/api/analysis/analyze/{contract_id}` | Analyze a stored contract and save the result. | 200; 400 if text is empty; 404 if the contract is not found; 500 if the Gemini key is missing | None |
| GET | `/api/analysis/{analysis_id}` | Retrieve one saved analysis. | 200; 400 if not found | None |
| GET | `/api/analysis/` | List saved analyses. | 200 | None |
| GET | `/api/analysis/contract/{contract_id}` | List saved analyses for a contract. | 200 | None |

The upload endpoint expects a multipart form field named `file`. The analysis endpoint takes the contract ID in the path and does not take a request body.

## Request and response examples

Upload a file:

```bash
curl -X POST "http://127.0.0.1:8000/api/contracts/upload" \
  -F "file=@contract.pdf"
```

Example upload response:

```json
{
  "message": "File uploaded and processed successfully",
  "contract": {
    "id": "<mongo-object-id>",
    "filename": "<generated-name>.pdf",
    "original_name": "contract.pdf",
    "upload_date": "<ISO-formatted string>",
    "text_content": "One two three.",
    "page_count": 1,
    "word_count": 3,
    "status": "uploaded"
  },
  "id": "<mongo-object-id>"
}
```

Request an analysis using the `id` from the upload response:

```bash
curl -X POST "http://127.0.0.1:8000/api/analysis/analyze/<contract-id>"
```

Example analysis response:

```json
{
  "message": "contract analyzed successfully.!",
  "analysis": {
    "id": "<mongo-object-id>",
    "contract_id": "<mongo-object-id>",
    "analysis_date": "<ISO-formatted string>",
    "summary": "<summary>",
    "contract_type": "<contract type>",
    "key_clauses": [],
    "risk_flags": [],
    "overall_risk_level": "low",
    "recommendations": []
  },
  "id": "<mongo-object-id>"
}
```

## Swagger/OpenAPI docs

FastAPI's generated docs are enabled at `/docs` and `/redoc`. The OpenAPI schema is at `/openapi.json`.

## What I learned

- I practiced defining FastAPI routers and handling file uploads.
- I used Pydantic models to represent contracts and analysis results.
- I connected an API to MongoDB with PyMongo.
- I worked with PDF and TXT text extraction.
- I used an AI SDK to request structured contract analysis.

## Known limitations

- The POST upload and analysis routes use FastAPI's default success status, `200`, rather than `201`.
- The ID path parameters are plain strings passed directly to `ObjectId`; malformed IDs are not validated before conversion.
- No endpoint requires authentication. Contract text and analysis results may contain personal or sensitive information.
- `GET /api/analysis/contract/{contract_id}` does not check whether the contract exists before querying analyses.
- The parser functions are annotated as returning `str`, but they return dictionaries containing text and counts.
- The PDF parser appends the literal string `"/n"` between pages instead of a newline.
- The startup indexes do not match the inserted document fields: contract documents have no `contract_id`, and analysis documents have no `analysis_id`. The unique indexes can prevent inserting more than one document with a missing indexed value.
- The Gemini client is initialized without an explicit API key argument, while the key is read separately in `config.py`.
- Only `CONTRACT_ANALYSIS_PROMPT` is used; the clause extraction, risk assessment, and summary prompt templates are currently unused.
- `docker-compose.yml` is ignored by `.gitignore`, so it may not be included in a fresh clone. Its MongoDB root password is hard-coded; replace it with a local secret before using the file.
- The endpoint list returned by `/` does not match the actual `/api/...` paths.
- There is no test suite in the workspace.

## Potential improvements

- Pass the Gemini API key explicitly when creating the Google GenAI client.
- Align the unique indexes with fields that are actually stored.
- Validate MongoDB IDs and return a clear `400` for malformed IDs.
- Add authentication and authorization before exposing contract or analysis data.
- Return `201 Created` from routes that create records.
- Correct the PDF page separator and parser return annotations.
- Keep database credentials out of the Compose file and make the Compose configuration available to new clones.
- Add tests for upload, parsing, database serialization, and analysis failure cases.
