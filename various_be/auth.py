from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from various_be.database import get_db
from various_be.models import User
from various_be.schemas import UserCreate, UserLogin
from various_be.security import get_password_hash, verify_password

router = APIRouter()

# ✅ 회원가입 API
@router.post("/signup")
async def signup(user_data: UserCreate, db: Session = Depends(get_db)):
    # 중복 ID 체크
    existing_user = db.query(User).filter(User.userid == user_data.userid).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="이미 가입된 아이디입니다.")
    
    # 비밀번호 해싱 후 유저 추가
    hashed_password = get_password_hash(user_data.password)
    new_user = User(userid=user_data.userid, password=hashed_password, username=user_data.username)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "회원가입 성공"}

# ✅ 로그인 API
@router.post("/login")
async def login(request: Request, signin_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.userid == signin_data.userid).first()
    
    if user and verify_password(signin_data.password, user.password):
        request.session["userid"] = user.userid  # 세션 저장
        return {"message": "로그인 성공"}
    else:
        raise HTTPException(status_code=401, detail="로그인 실패")

# ✅ 로그아웃 API
@router.post("/logout")
async def logout(request: Request):
    request.session.pop("userid", None)  # 세션에서 삭제
    return {"message": "로그아웃 성공"}