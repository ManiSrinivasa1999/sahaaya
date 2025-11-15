from fastapi import FastAPI
from typing import Optional
from pydantic import BaseModel

app = FastAPI()


class ProcessRequest(BaseModel):
    text: str
    language: Optional[str] = "en"


@app.get("/")
def home():
    return {"message": "Sahaaya Backend is running - Basic Test Version"}


@app.get("/test")
def test_endpoint():
    return {
        "status": "working",
        "message": "Basic FastAPI functionality is working",
        "version": "1.1-basic-test"
    }


@app.post("/simple-process")
def simple_process(request: ProcessRequest):
    """
    Simple text processing endpoint for testing (without audio/model dependencies)
    """
    return {
        "input_text": request.text,
        "language": request.language,
        "simple_guidance": f"Basic health guidance for '{request.text}' in {request.language}",
        "status": "processed_successfully"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)