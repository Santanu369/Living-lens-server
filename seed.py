from database import SessionLocal
from models import Keeper, Admin, Observation


db = SessionLocal()

keepers = [
    Admin(username="admin1",
    admin_key="admin123",
    zoo_id="Z001"),

    Keeper(
        username = "zoo_keeper1",
        keeper_id = "1",
        zoo_id = "Z001"
    ),

        Keeper(
        username = "zoo_keeper2",
        keeper_id = "2",
        zoo_id = "Z001"
    ),

        Keeper(
        username = "zoo_keeper3",
        keeper_id = "3",
        zoo_id = "Z002"
    ),
    
]

db.add_all(keepers)
db.commit()

db.close()

print("Keepers added successfully")