from sqlalchemy import Column, String
from ..db_session import Base

class Mastery(Base):
    __tablename__ = "mastery"
    champion_name = Column(String, index=True, primary_key=True)
    column_1 = Column(String)
    column_2 = Column(String)
    column_3 = Column(String)
    column_4 = Column(String)
    column_5 = Column(String)
    column_6 = Column(String)
    column_7 = Column(String)
    column_8 = Column(String)
    column_9 = Column(String)
    column_10 = Column(String)