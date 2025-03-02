from fastapi import APIRouter, File, UploadFile, HTTPException
import os
import shutil

UPLOAD_DIR = "static/uploads/"
router = APIRouter()

# 이미지 업로드 API
@router.post("/")
async def upload_image(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    
    # 이미지 파일 저장
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"filename": file.filename, "path": file_location}
