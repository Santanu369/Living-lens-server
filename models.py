from sqlalchemy import Column, Integer, String, Float
from database import Base


class Keeper(Base):
    __tablename__ = "keepers"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    keeper_id = Column(String, unique=True, nullable=False)
    zoo_id = Column(String, nullable=False)

class Citizen(Base):
    __tablename__ = "citizens"

    id = Column(Integer, primary_key=True)
    username = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, unique=True, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    admin_key = Column(String, unique=True, nullable=False)
    zoo_id = Column(String, nullable=False)

class Observation(Base):
    __tablename__ = "observations"

    id = Column(Integer, primary_key=True)
    keeper_id = Column(String, nullable=False)
    zoo_id = Column(String, nullable=False)
    animal_name = Column(String, nullable=False)
    behaviour = Column(String, nullable=False)
    intensity = Column(Integer, nullable=False)
    animal_percentage = Column(Integer, nullable=False)
    duration = Column(Integer, nullable=False)
