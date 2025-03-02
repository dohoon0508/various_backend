from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime, time
import os
import shutil

from various_be.database import get_db
from various_be.models import User, Mission, Fine
from various_be.schemas import MissionCreate

router = APIRouter()

UPLOAD_DIR = "static/uploads/"

# ✅ 디렉토리 확인 후 생성
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# ✅ 미션 업로드 API
@router.post("/")
async def upload_mission(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    current_time = datetime.now().time()
    
    # ✅ 06:00 ~ 09:00 사이에 업로드해야 성공
    success_time_start = time(6, 0, 0)
    success_time_end = time(9, 0, 0)

    # ✅ 사용자 확인
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    # ✅ 미션 이미지 저장
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    today = datetime.now().date()
    mission = db.query(Mission).filter(Mission.user_id == user.id, Mission.mission_date == today).first()

    if not mission:
        mission = Mission(
            user_id=user.id,
            mission_date=today,
            total_attempts=1,
            success_count=0,
            failure_count=0,
            mission_time=current_time,
            image_path=file_location
        )
        db.add(mission)
    else:
        mission.total_attempts += 1
        mission.mission_time = current_time
        mission.image_path = file_location

    if success_time_start <= current_time <= success_time_end:
        mission.success_count += 1
    else:
        mission.failure_count += 1
        fine = db.query(Fine).filter(Fine.user_id == user.id).first()
        if not fine:
            fine = Fine(user_id=user.id, total_fine=1000, accumulated_fine=1000)
            db.add(fine)
        else:
            fine.accumulated_fine += 1000
            fine.total_fine += 1000

    db.commit()
    db.refresh(mission)

    return {
        "message": "미션 업로드 완료",
        "status": "성공" if success_time_start <= current_time <= success_time_end else "실패",
        "mission": {
            "date": mission.mission_date,
            "attempts": mission.total_attempts,
            "success": mission.success_count,
            "failure": mission.failure_count,
        },
        "fine": {
            "total_fine": fine.total_fine if 'fine' in locals() else 0,
            "accumulated_fine": fine.accumulated_fine if 'fine' in locals() else 0
        }
    }


# ✅ 특정 유저의 벌금 조회 API
@router.get("/fine/{user_id}")
async def get_user_fine(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    fine = db.query(Fine).filter(Fine.user_id == user_id).first()
    if not fine:
        return {"user_id": user_id, "accumulated_fine": 0, "total_fine": 0}

    return {
        "user_id": user_id,
        "accumulated_fine": fine.accumulated_fine,
        "total_fine": fine.total_fine
    }


# ✅ 전체 벌금 조회 API
@router.get("/fine/total")
async def get_total_fine(db: Session = Depends(get_db)):
    total_fine = db.query(Fine).with_entities(Fine.total_fine).all()
    total_fine_sum = sum(f[0] for f in total_fine) if total_fine else 0

    return {"total_fine": total_fine_sum if total_fine_sum is not None else 0}
