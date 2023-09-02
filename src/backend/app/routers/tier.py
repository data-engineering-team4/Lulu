from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db_session import SessionLocal
from ..models.tier import tb_info

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/banpick/tier/{tier}/{position}")
async def get_tier(tier: str, position: str, db: Session = Depends(get_db)):
    try:
        query = db.query(tb_info)

        if tier == "all":
            query = query.filter(tb_info.position == position)
        else:
            query = query.filter(tb_info.tier == tier, tb_info.position == position)

        query = query.order_by(tb_info.champion_tier.desc())
        results = query.all()

        data = []
        for row in results:
            data.append(
                {
                    "champion_id": row.champion_id,
                    "win_rate": row.win_rate,
                    "pick_rate": row.pick_rate,
                    "ban_rate": row.ban_rate,
                }
            )

        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
