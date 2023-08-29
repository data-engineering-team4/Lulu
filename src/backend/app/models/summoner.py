from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import Session
from ..db_session import Base


class Summoner(Base):
    __tablename__ = "summoners"

    id = Column(Integer, primary_key=True, index=True)
    summonerName = Column(String, index=True)


def create_summoner(db: Session, summoner: Summoner):
    db.add(summoner)
    db.commit()
    db.refresh(summoner)
    return summoner
