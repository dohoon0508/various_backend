from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserCreate
from security import get_password_hash

router = APIRouter()

# 회원가입 API
@router.post("/signup")
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    # 기존에 동일한 ID가 있는지 확인
    existing_user = db.query(User).filter(User.userid == user_data.userid).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 가입된 아이디입니다.")
    
    # 비밀번호 해싱 후 유저 생성
    hashed_password = get_password_hash(user_data.password)
    new_user = User(userid=user_data.userid, password=hashed_password, username=user_data.username)
    
    # 데이터베이스에 추가
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "회원가입이 성공했습니다."}
