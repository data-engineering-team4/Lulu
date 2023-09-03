from sqlalchemy import Column, Text, Float, BigInteger
from ..db_session import Base


class AllTeam(Base):
    __tablename__ = "all_team"

    id = Column(Text, primary_key=True)
    champion_name = Column(Text)
    pick_rate = Column(BigInteger, nullable=False)
    my_lane = Column(Text, nullable=False)
    our_top = Column(Text, nullable=False)
    opponent_top = Column(Text, nullable=False)
    our_jungle = Column(Text, nullable=False)
    opponent_jungle = Column(Text, nullable=False)
    our_middle = Column(Text, nullable=False)
    opponent_middle = Column(Text, nullable=False)
    our_bottom = Column(Text, nullable=False)
    opponent_bottom = Column(Text, nullable=False)
    our_utility = Column(Text, nullable=False)
    opponent_utility = Column(Text, nullable=False)


class OpponentLane(Base):
    __tablename__ = "opponent_lane"

    id = Column(Text, primary_key=True)
    champion_name = Column(Text)
    pick_rate = Column(BigInteger, nullable=False)
    my_lane = Column(Text, nullable=False)
    opponent_champ = Column(Text, nullable=False)


class OpponentTeam(Base):
    __tablename__ = "opponent_team"

    id = Column(Text, primary_key=True)
    champion_name = Column(Text)
    pick_rate = Column(BigInteger, nullable=False)
    my_lane = Column(Text, nullable=False)
    top = Column(Text, nullable=False)
    jungle = Column(Text, nullable=False)
    middle = Column(Text, nullable=False)
    bottom = Column(Text, nullable=False)
    utility = Column(Text, nullable=False)


class OurTeam(Base):
    __tablename__ = "our_team"

    id = Column(Text, primary_key=True)
    champion_name = Column(Text)
    pick_rate = Column(BigInteger, nullable=False)
    my_lane = Column(Text, nullable=False)
    top = Column(Text, nullable=False)
    jungle = Column(Text, nullable=False)
    middle = Column(Text, nullable=False)
    bottom = Column(Text, nullable=False)
    utility = Column(Text, nullable=False)
