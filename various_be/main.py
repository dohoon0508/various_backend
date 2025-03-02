from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

# ✅ 내부 모듈 import (경로 문제 해결)
from various_be.database import Base, engine
from various_be import auth, mission, fine, upload

# FastAPI 앱 생성
app = FastAPI()

# 세션 미들웨어 추가 (로그인 상태 유지)
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

# 데이터베이스 테이블 자동 생성
Base.metadata.create_all(bind=engine)

# API 라우트 추가
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(mission.router, prefix="/mission", tags=["Mission"])
app.include_router(fine.router, prefix="/fine", tags=["Fine"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
