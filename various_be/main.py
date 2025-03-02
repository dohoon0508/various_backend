from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from fastapi import FastAPI

app = FastAPI()

# MySQL 연결 정보
DATABASE_URL = "mysql+pymysql://root:ASdh%402304@localhost/various"

# 데이터베이스 엔진 생성
engine = create_engine(DATABASE_URL)

# 세션 로컬 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy 모델의 베이스 클래스
Base = declarative_base()

def get_db():
    """데이터베이스 세션을 가져오는 함수"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ✅ 테이블 자동 생성 실행 (이 코드가 필요!)
Base.metadata.create_all(bind=engine)
