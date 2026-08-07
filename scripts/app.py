from fastapi import FastAPI, HTTPException

from workbook_builder import WorkbookBuilder

app = FastAPI(
    title="AI Curriculum Workbook Service",
    version="1.0.0"
)

builder = WorkbookBuilder()


@app.get("/")
def root():
    return {
        "service": "AI Curriculum Workbook Service",
        "status": "running"
    }


@app.get("/health")
def health():
    return {
        "status": "running"
    }


@app.post("/workbook")
def build_workbook(workbook_request: dict):
    try:

        result = builder.build(workbook_request)

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
