from pydantic import BaseModel

class KeeperCreate(BaseModel):
    username: str
    keeper_id: str