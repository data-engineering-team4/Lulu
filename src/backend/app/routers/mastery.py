from fastapi import APIRouter, Depends
from ..models.mastery import Mastery
from fastapi_cache.decorator import cache
from ..utils.helpers import get_db
from sqlalchemy.orm import Session

router = APIRouter()


@router.get("/champion-info")
@cache(expire=86400)
async def get_champion_info(champion_name: str, db: Session = Depends(get_db)):
    champion = db.query(Mastery).filter(Mastery.champion_name == champion_name).first()

    if champion:
        champion_data = [
            getattr(champion, column_name)
            for column_name in Mastery.__table__.columns.keys()
        ]
        return {
            "champion_name": champion.champion_name,
            **dict(zip(Mastery.__table__.columns.keys(), champion_data)),
        }
    else:
        return {"message": "Champion not found"}
