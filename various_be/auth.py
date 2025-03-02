from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from various_be.database import get_db
from various_be.models import User
from various_be.schemas import UserCreate
from various_be.security import get_password_hash

router = APIRouter()

@router.post("/signup")
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.userid == user_data.userid).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 가입된 아이디입니다.")
    
    hashed_password = get_password_hash(user_data.password)
    new_user = User(userid=user_data.userid, password=hashed_password, username=user_data.username)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "회원가입 성공"}
