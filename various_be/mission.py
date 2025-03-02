from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime, time
import os
import shutil
import schedule
import threading
import time as tm

from various_be.database import get_db
from various_be.models import User, Mission, Fine

router = APIRouter()

UPLOAD_DIR = "static/uploads/"

# ✅ 디렉토리 확인 후 생성
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


# ✅ 🔥 `total_fine`을 전체 `accumulated_fine` 합으로 즉시 갱신하는 함수
def update_total_fine(db: Session):
    total_fine_value = db.query(Fine.accumulated_fine).with_entities(Fine.accumulated_fine).all()
    total_fine_value = sum(f[0] if f[0] is not None else 0 for f in total_fine_value)

    # ✅ 모든 벌금 레코드의 `total_fine` 갱신
    db.query(Fine).update({"total_fine": total_fine_value})
    db.commit()


@router.post("/")
async def upload_mission(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    current_time = datetime.now().time()
    today = datetime.now().date()

    # ✅ 사용자 확인
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
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

    # ✅ 미션 성공 여부 판별
    success_time_start = time(6, 0, 0)
    success_time_end = time(9, 0, 0)

    if success_time_start <= current_time <= success_time_end:
        mission.success_count += 1
    else:
        mission.failure_count += 1

        # ✅ 개인 벌금 처리
        fine = db.query(Fine).filter(Fine.user_id == user.id).first()
        if not fine:
            fine = Fine(user_id=user.id, accumulated_fine=1000, total_fine=0)
            db.add(fine)
        else:
            fine.accumulated_fine += 1000

    db.commit()  # ✅ 개인 벌금 먼저 반영 후 total 갱신

    # ✅ 🔥 `total_fine` 즉시 업데이트 (commit 이후 실행)
    update_total_fine(db)

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
            "total_fine": db.query(Fine).first().total_fine,  # ✅ 갱신된 값 반환
            "accumulated_fine": fine.accumulated_fine if fine else 0
        }
    }


# ✅ 자정에 미션 안 올린 유저에게 벌금 자동 부과
def apply_auto_fines():
    db = next(get_db())
    today = datetime.now().date()

    users = db.query(User).all()
    for user in users:
        mission = db.query(Mission).filter(Mission.user_id == user.id, Mission.mission_date == today).first()
        if not mission:
            fine = db.query(Fine).filter(Fine.user_id == user.id).first()
            if not fine:
                fine = Fine(user_id=user.id, accumulated_fine=1000)
                db.add(fine)
            else:
                fine.accumulated_fine += 1000

    db.commit()  # ✅ 개인 벌금 먼저 반영 후 total 갱신

    # ✅ 🔥 `total_fine` 즉시 업데이트
    update_total_fine(db)


@router.get("/fine/{user_id}")
async def get_user_fine(user_id: int, db: Session = Depends(get_db)):
    # ✅ 유저 존재 여부 확인
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    fine = db.query(Fine).filter(Fine.user_id == user_id).first()
    
    if not fine:
        return {
            "user_id": user_id,
            "accumulated_fine": 0,
            "total_fine": 0,
            "message": "부지런하시네요!"
        }

    message = "부지런하시네요!" if fine.accumulated_fine == 0 else ""

    return {
        "user_id": user_id,
        "accumulated_fine": fine.accumulated_fine,
        "total_fine": fine.total_fine,
        "message": message
    }


@router.get("/fine-total")
async def get_total_fine(db: Session = Depends(get_db)):
    """
    모든 유저의 벌금 총합을 조회하는 API
    """
    # ✅ 모든 유저의 `accumulated_fine` 합산하여 `total_fine` 값으로 반환
    total_fine_query = db.query(Fine.accumulated_fine).with_entities(Fine.accumulated_fine).all()
    
    # ✅ accumulated_fine 값을 합산하여 total_fine 생성
    total_fine_value = sum(f[0] if f[0] is not None else 0 for f in total_fine_query) if total_fine_query else 0

    message = "모든 유저가 부지런하네요!" if total_fine_value == 0 else "다들 화이팅!"

    return {
        "total_fine": total_fine_value,
        "message": message
    }



# ✅ 매일 자정(00:00)에 벌금 자동 부과 스케줄러 실행
schedule.every().day.at("00:00").do(apply_auto_fines)

def schedule_runner():
    while True:
        schedule.run_pending()
        tm.sleep(60)

# ✅ 스케줄러 실행을 위한 백그라운드 스레드 시작
threading.Thread(target=schedule_runner, daemon=True).start()
