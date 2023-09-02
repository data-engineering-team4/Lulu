from sqlalchemy import Column, String, Float, Integer
from ..db_session import Base


class tb_info(Base):
    __tablename__ = "tb_info"
    tier = Column(String)
    position = Column(String)
    champion_name = Column(String)
    win_rate = Column(Float)
    pick_rate = Column(Float)
    ban_rate = Column(Float)
    kda = Column(Float)
    champion_id = Column(Integer, primary_key=True)
    champion_tier = Column(Float)
