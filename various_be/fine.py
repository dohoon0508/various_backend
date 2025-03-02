from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from various_be.database import get_db
from various_be.models import User, Fine

router = APIRouter()

# ✅ 모든 유저의 총 벌금 조회
@router.get("/total")  # 여기 확인!! 👀
async def get_total_fine(db: Session = Depends(get_db)):
    users_fines = db.query(User.username, Fine.accumulated_fine).join(Fine, User.id == Fine.user_id, isouter=True).all()

    users_fines = [{"username": user, "accumulated_fine": fine if fine else 0} for user, fine in users_fines]
    total_fine_value = sum(user["accumulated_fine"] for user in users_fines)

    return {
        "users": users_fines,
        "total_fine": total_fine_value,
        "message": "전체 벌금 조회 완료!"
    }
