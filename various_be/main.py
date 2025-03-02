from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from various_be import auth, mission, fine, upload
from various_be.database import Base, engine
import os

# FastAPI 앱 생성
app = FastAPI()

# ✅ CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 연동
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ 세션 미들웨어 추가
app.add_middleware(SessionMiddleware, secret_key="your-secret-key")

# ✅ Jinja2 템플릿 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 현재 파일 기준 경로
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))  # templates 폴더 지정

# ✅ DB 테이블 생성
Base.metadata.create_all(bind=engine)

# ✅ API 라우트 추가
app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(mission.router, prefix="/mission", tags=["Mission"])
app.include_router(fine.router, prefix="/fine", tags=["Fine"])
app.include_router(upload.router, prefix="/upload", tags=["Upload"])

# ✅ 홈 화면 라우트 추가
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
