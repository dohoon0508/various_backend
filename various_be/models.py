from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey
from database import Base

# 유저 테이블 (회원 정보 저장)
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    userid = Column(String(100), unique=True, nullable=False, index=True)  # 로그인 ID
    password = Column(String(512), nullable=False)  # 해싱된 비밀번호
    username = Column(String(100), nullable=False)  # 닉네임

# 미션 테이블 (사용자가 수행한 미션 기록 저장)
class Mission(Base):
    __tablename__ = "missions"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 사용자 ID
    mission_date = Column(Date, nullable=False)  # 미션 수행 날짜
    mission_time = Column(Time, nullable=False)  # 미션 수행 시간
    image_path = Column(String(255), nullable=True)  # 업로드한 이미지 경로

# 벌금 테이블 (사용자의 벌금 기록 저장)
class Fine(Base):
    __tablename__ = "fines"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 사용자 ID
    total_fine = Column(Integer, default=0)  # 전체 벌금 합계
    accumulated_fine = Column(Integer, default=0)  # 현재까지 쌓인 벌금
