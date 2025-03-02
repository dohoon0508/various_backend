from fastapi import APIRouter, File, UploadFile
import os
import shutil

router = APIRouter()
UPLOAD_DIR = "static/uploads/"

@router.post("/")
async def upload_image(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"filename": file.filename, "path": file_location}
