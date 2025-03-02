from pydantic import BaseModel
from typing import Optional
from datetime import date, time

# ✅ 회원가입 요청 데이터 검증
class UserCreate(BaseModel):
    userid: str
    password: str
    username: str

# ✅ 로그인 요청 데이터 검증
class UserLogin(BaseModel):
    userid: str
    password: str

# ✅ 미션 관련 요청 데이터 검증
class MissionCreate(BaseModel):
    mission_date: date
    mission_time: time
    image_path: Optional[str] = None

# ✅ 벌금 관련 요청 데이터 검증
class FineUpdate(BaseModel):
    total_fine: Optional[int] = None
    accumulated_fine: Optional[int] = None
