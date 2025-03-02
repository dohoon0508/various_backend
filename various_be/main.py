from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from various_be import auth, mission, fine, upload
from various_be.database import Base, engine

# FastAPI 앱 생성
app = FastAPI()

# ✅ 🔥 CORS 설정 추가 (React와 연결 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 앱의 URL 추가 (필요하면 여러 개 가능)
    allow_credentials=True,  # 쿠키 포함 요청 허용
    allow_methods=["*"],  # 모든 HTTP 메서드 허용 (GET, POST, PUT, DELETE 등)
    allow_headers=["*"],  # 모든 헤더 허용
)

# ✅ DB 테이블 생성
Base.metadata.create_all(bind=engine)

# ✅ API 라우트 추가
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(mission.router, prefix="/mission", tags=["Mission"])
app.include_router(fine.router, prefix="/fine", tags=["Fine"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])
