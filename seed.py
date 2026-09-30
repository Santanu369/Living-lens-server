from database import SessionLocal
from models import Keeper


db = SessionLocal()

keepers = [
    Keeper(username="Santanu", keeper_id="ZK001"),
    Keeper(username="Rahul", keeper_id="ZK002"),
    Keeper(username="Amit", keeper_id="ZK003"),
]

db.add_all(keepers)
db.commit()

db.close()

print("Keepers added successfully")