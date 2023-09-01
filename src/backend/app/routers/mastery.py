from fastapi import APIRouter, Depends
from ..models.mastery import Mastery
from ..db_session import SessionLocal

router = APIRouter()

@router.get("/champion-info")
async def get_champion_info(champion_name: str):
    db = SessionLocal()
    champion = db.query(Mastery).filter(Mastery.champion_name == champion_name).first()
    db.close()
    
    if champion:
        champion_data = [getattr(champion, column_name) for column_name in Mastery.__table__.columns.keys()]
        return {"champion_name": champion.champion_name, **dict(zip(Mastery.__table__.columns.keys(), champion_data))}
    else:
        return {"message": "Champion not found"}