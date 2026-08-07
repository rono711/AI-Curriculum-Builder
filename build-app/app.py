from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from api.workbook_reader import WorkbookReader
import httpx
from fastapi.responses import FileResponse

# ==========================================================
# FastAPI App
# ==========================================================

app = FastAPI(title="Rono AI Curriculum Builder")


# ==========================================================
# Static Files
# ==========================================================

app.mount("/static", StaticFiles(directory="static"), name="static")


# ==========================================================
# HTML Templates
# ==========================================================

templates = Jinja2Templates(directory="templates")


# ==========================================================
# Workbook
# ==========================================================

reader = WorkbookReader()


# ==========================================================
# Home Page
# ==========================================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Rono AI Curriculum Builder"
        }
    )


# ==========================================================
# Health Check
# ==========================================================

@app.get("/health")
async def health():

    return {
        "status": "running"
    }


# ==========================================================
# Year Levels
# ==========================================================

@app.get("/api/year-levels")
async def get_year_levels():

    reader.reload()

    return reader.get_year_levels()



# ==========================================================
# Build Request
# ==========================================================

@app.post("/api/build")
async def build(request: Request):

    payload = await request.json()

    print("===================================")
    print("===== PAYLOAD TO BUILDER =====")
    print(payload)
    print("===================================")

    async with httpx.AsyncClient() as client:

        response = await client.post(
            "http://localhost:8004/build",
            json=payload,
            timeout=300
        )
    print("=" * 60)
    print("BUILDER STATUS:", response.status_code)
    print("BUILDER RESPONSE:")
    print(response.text)
    print("=" * 60)

    if response.status_code != 200:
        raise HTTPException(

            status_code=response.status_code,

            detail=response.text

        )

    return response.json()