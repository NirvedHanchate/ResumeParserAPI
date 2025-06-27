from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import JSONResponse
import shutil
import os
from parser import parse_resume

app = FastAPI(docs_url="/docs")

@app.get("/")
def home():
    return {"message": "Resume Parser API is up!"}

@app.post("/upload/")
async def upload_resume(file: UploadFile = File(...), mode: str = Form("Digital")):
    # Save file temporarily
    file_location = f"temp_{file.filename}"
    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        parsed_data = parse_resume(file_location, mode)
    except Exception as e:
        os.remove(file_location)
        return JSONResponse(status_code=500, content={"error": str(e)})
    
    os.remove(file_location)
    return parsed_data