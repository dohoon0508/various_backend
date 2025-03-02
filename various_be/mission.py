from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from various_be.database import get_db  # ✅ 경로 수정
from various_be.models import Mission
from various_be.schemas import MissionCreate

router = APIRouter()
