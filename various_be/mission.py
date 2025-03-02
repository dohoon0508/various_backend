from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime, time, timedelta
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


# ✅ 미션 업로드 API
@router.post("/")
async def upload_mission(user_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    current_time = datetime.now().time()
    today = datetime.now().date()
    weekday = today.weekday()  # 0=월, 1=화, ..., 4=금

    # ✅ 주말에는 미션 불가능
    if weekday >= 5:
        raise HTTPException(status_code=400, detail="미션은 평일(월~금)에만 가능합니다.")

    success_time_start = time(6, 0, 0)
    success_time_end = time(9, 0, 0)

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

    if success_time_start <= current_time <= success_time_end:
        mission.success_count += 1
    else:
        mission.failure_count += 1
        fine = db.query(Fine).filter(Fine.user_id == user.id).first()
        if not fine:
            fine = Fine(user_id=user.id, accumulated_fine=1000)
            db.add(fine)
        else:
            fine.accumulated_fine += 1000

    # ✅ 전체 벌금(total_fine) 갱신
    total_fine_sum = db.query(Fine).with_entities(Fine.accumulated_fine).all()
    fine.total_fine = sum(f[0] for f in total_fine_sum if f[0] is not None)

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
            "total_fine": fine.total_fine,
            "accumulated_fine": fine.accumulated_fine
        }
    }

@router.get("/fine/{user_id}")
async def get_user_fine(user_id: int, db: Session = Depends(get_db)):
    # ✅ 유저 존재 여부 확인
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

    # ✅ 벌금 정보 조회
    fine = db.query(Fine).filter(Fine.user_id == user_id).first()
    
    # ✅ 벌금 기록이 없을 경우 기본값 반환
    if not fine:
        return {
            "user_id": user_id,
            "accumulated_fine": 0,
            "total_fine": 0,
            "message": "부지런하시네요!"  # ✅ 벌금이 없으면 메시지 출력
        }

    # ✅ 벌금이 0원이면 메시지 추가
    message = "부지런하시네요!" if fine.accumulated_fine == 0 else ""

    return {
        "user_id": user_id,
        "accumulated_fine": fine.accumulated_fine,
        "total_fine": fine.total_fine,
        "message": message  # ✅ 벌금이 없으면 메시지 출력
    }


# ✅ 자정에 미션 안 올린 유저에게 벌금 자동 부과
def apply_auto_fines():
    db = next(get_db())
    today = datetime.now().date()
    weekday = today.weekday()  # 0=월, 1=화, ..., 4=금

    if weekday < 5:  # 평일만 적용
        users = db.query(User).all()
        for user in users:
            mission = db.query(Mission).filter(Mission.user_id == user.id, Mission.mission_date == today).first()
            if not mission:  # ✅ 미션을 아예 안 올린 경우
                fine = db.query(Fine).filter(Fine.user_id == user.id).first()
                if not fine:
                    fine = Fine(user_id=user.id, accumulated_fine=1000)
                    db.add(fine)
                else:
                    fine.accumulated_fine += 1000

        # ✅ 전체 벌금(total_fine) 갱신 (모든 유저의 accumulated_fine 합산)
        total_fine_sum = db.query(Fine).with_entities(Fine.accumulated_fine).all()
        total_fine_value = sum(f[0] for f in total_fine_sum if f[0] is not None) if total_fine_sum else 0

        # ✅ 벌금 테이블의 모든 `total_fine` 값을 합산된 값으로 설정
        for fine in db.query(Fine).all():
            fine.total_fine = total_fine_value

        db.commit()


@router.get("/fine/total")
async def get_total_fine(db: Session = Depends(get_db)):
    # ✅ 전체 벌금 합산 (벌금 데이터가 없을 경우 기본값 0)
    total_fine_sum = db.query(Fine).with_entities(Fine.accumulated_fine).all()
    total_fine_value = sum(f[0] for f in total_fine_sum if f[0] is not None) if total_fine_sum else 0

    # ✅ 전체 벌금이 0이면 메시지 출력
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