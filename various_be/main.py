from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
import auth, mission, fine, upload
from database import Base, engine

# FastAPI 인스턴스 생성
app = FastAPI()

# 세션 미들웨어 추가
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

# 라우트 추가
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(mission.router, prefix="/mission", tags=["Mission"])
app.include_router(fine.router, prefix="/fine", tags=["Fine"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])