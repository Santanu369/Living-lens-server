from sqlalchemy import Column, Integer, String
from database import Base


class Keeper(Base):
    __tablename__ = "keepers"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    keeper_id = Column(String, unique=True, nullable=False)