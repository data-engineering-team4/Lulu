from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db_session import SessionLocal
from ..models.tier import tb_info
from ..utils.helpers import get_db

router = APIRouter()

@router.post("/banpick/tier/{tier}")
async def get_tier(tier: str, db: Session = Depends(get_db)):
    try:
        query = db.query(tb_info)
        query = query.filter(tb_info.tier == tier)
        query = query.order_by(tb_info.champion_tier.desc())
        data1 = query.all()

        query1 = db.query(tb_info).filter(tb_info.tier == tier, tb_info.position == 'TOP')
        query1 = query1.order_by(tb_info.champion_tier.desc())
        query2 = db.query(tb_info).filter(tb_info.tier == tier, tb_info.position == 'JUNGLE')
        query2 = query2.order_by(tb_info.champion_tier.desc())
        query3 = db.query(tb_info).filter(tb_info.tier == tier, tb_info.position == 'MIDDLE')
        query3 = query3.order_by(tb_info.champion_tier.desc())
        query4 = db.query(tb_info).filter(tb_info.tier == tier, tb_info.position == 'BOTTOM')
        query4 = query4.order_by(tb_info.champion_tier.desc())
        query5 = db.query(tb_info).filter(tb_info.tier == tier, tb_info.position == 'UTILITY')
        query5 = query5.order_by(tb_info.champion_tier.desc())

        data2 = query1.all()
        data3 = query2.all()
        data4 = query3.all()
        data5 = query4.all()
        data6 = query5.all()
        
        return data1, data2, data3, data4, data5, data6
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
