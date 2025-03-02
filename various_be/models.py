from sqlalchemy import Column, Integer, String, Date, Time, ForeignKey
from various_be.database import Base

# ✅ 유저 테이블
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    userid = Column(String(100), unique=True, nullable=False, index=True)  # 로그인 ID
    password = Column(String(512), nullable=False)  # 해싱된 비밀번호
    username = Column(String(100), nullable=False)  # 닉네임

# ✅ 미션 테이블
class Mission(Base):
    __tablename__ = "missions"
    
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 사용자 ID
    mission_date = Column(Date, nullable=False)  # 미션 수행 날짜
    total_attempts = Column(Integer, default=0)  # 전체 시도 횟수
    success_count = Column(Integer, default=0)  # 성공 횟수
    failure_count = Column(Integer, default=0)  # 실패 횟수
    mission_time = Column(Time, nullable=True)  # ✅ 미션 수행 시간이 없을 수도 있음
    image_path = Column(String(255), nullable=True)  # ✅ 미션을 안 올릴 수도 있음

# ✅ 벌금 테이블
class Fine(Base):
    __tablename__ = "fines"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 사용자 ID
    total_fine = Column(Integer, default=0)  # 전체 벌금
    accumulated_fine = Column(Integer, default=0)  # 개인 벌금
