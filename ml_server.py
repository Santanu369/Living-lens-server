from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib
from fastapi.middleware.cors import CORSMiddleware
import os
import dotenv
import resend
from database import engine, Base

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Keeper, Observation, Citizen, Admin

Base.metadata.create_all(bind=engine)

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load your trained model
model = joblib.load("zoo_sentinel_model.pkl")


class PredictionInput(BaseModel):
    animal: str
    behaviour: str
    intensity: float
    abnormality_percentage: float
    duration_minutes: float

class AddObservation(BaseModel):
    keeper_id: str
    zoo_id: str
    animal_name: str
    behaviour: str
    intensity: int
    animal_percentage: int
    duration: int
    date: str



class KeeperLoginRequest(BaseModel):
    username: str
    keeper_id: str
    zoo_id: str

class AddKeeperRequest(BaseModel):
    username: str
    keeper_id: str
    zoo_id: str

class CitizenRegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    latitude: float
    longitude: float

class CitizenLoginRequest(BaseModel):
    email: str
    password: str

class AdminLoginRequest(BaseModel):
    username: str
    admin_key: str
    zoo_id: str

@app.get("/observations")
def fetch_observations(db: Session = Depends(get_db)):
    observations = db.query(Observation).all()
    return observations

@app.get("/zoo_keepers")
def fetch_zoo_keepers(zoo_id: str, db: Session = Depends(get_db)):
    zoo_keepers = db.query(Keeper).filter(
        Keeper.zoo_id == zoo_id
    ).all()

    return zoo_keepers 

@app.post("/add_zoo_keeper")
def add_zoo_keeper(data: AddKeeperRequest, db: Session = Depends(get_db)):
    keeper = Keeper(
        username=data.username,
        keeper_id=data.keeper_id,
        zoo_id=data.zoo_id
    )

    db.add(keeper)
    db.commit()
    db.refresh(keeper)

    return {
        "message": "Keeper added successfully",
        "id": keeper.id,
        "username": keeper.username,
        "keeper_id": keeper.keeper_id,
        "zoo_id": keeper.zoo_id
    }

@app.post("/keeper_login")
def login(data: KeeperLoginRequest, db: Session = Depends(get_db)):

    keeper = db.query(Keeper).filter(
        Keeper.username == data.username,
        Keeper.keeper_id == data.keeper_id,
    ).first()

    if not keeper:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or keeper ID"
        )

    return {
        "message": "Login successful",
        "keeper_id": keeper.keeper_id,
        "username": keeper.username,
        "zoo_id": keeper.zoo_id
    }

@app.post("/citizen_register")
def citizen_register(
    data: CitizenRegisterRequest,
    db: Session = Depends(get_db)
):

    existing_citizen = db.query(Citizen).filter(
        Citizen.email == data.email
    ).first()

    if existing_citizen:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    citizen = Citizen(
        username=data.username,
        email=data.email,
        password=data.password,
        latitude=data.latitude,
        longitude=data.longitude
    )

    db.add(citizen)
    db.commit()
    db.refresh(citizen)

    return {
        "message": "Citizen registered successfully",
        "citizen_id": citizen.id,
        "username": citizen.username,
        "email": citizen.email,
        "latitude": citizen.latitude,
        "longitude": citizen.longitude
    }

@app.post("/citizen_login")
def citizen_login(
    data: CitizenLoginRequest,
    db: Session = Depends(get_db)
):

    existing_citizen = db.query(Citizen).filter(
        Citizen.email == data.email,
        Citizen.password == data.password
    ).first()

    if not existing_citizen:
        raise HTTPException(
            status_code=400,
            detail="Citizen doesn't exist, please register first"
        )

    return {
        "message": "You logged in succefully"
    }

@app.post("/admin_login")
def admin_login(
    data: AdminLoginRequest,
    db: Session = Depends(get_db)
):
        return {
        "message": "Admin loggedin successfully",
    }

    # admin = db.query(Admin).filter(
    #     Admin.username == data.username,
    #     Admin.email == data.email,
    #     Admin.password == data.password,
    #     Admin.zoo_id == data.zoo_id
    # ).first()

    

    # if not admin:
    #     raise HTTPException(
    #         status_code=401,
    #         detail="Invalid admin credentials"
    #     )
@app.get("/")
def home():
    return {"message": "Zoo Sentinel ML server is running"}

@app.post("/add_observation")
def add_observation(data: AddObservation, db: Session = Depends(get_db)):

    observation = Observation(
        keeper_id=data.keeper_id,
        zoo_id=data.zoo_id,
        animal_name=data.animal_name,
        behaviour=data.behaviour,
        intensity=data.intensity,
        animal_percentage=data.animal_percentage,
        duration=data.duration,
        date=data.date
    )

    db.add(observation)
    db.commit()
    db.refresh(observation)

    return {
        "message": "Observation added successfully",
        "observation": {
            "id": observation.id,
            "keeper_id": observation.keeper_id,
            "zoo_id": observation.zoo_id,
            "animal_name": observation.animal_name,
            "behaviour": observation.behaviour,
            "intensity": observation.intensity,
            "animal_percentage": observation.animal_percentage,
            "duration": observation.duration
        }
    }

@app.post("/predict")
def predict(data: AddObservation, db: Session = Depends(get_db)):



    input_data = pd.DataFrame([{
        "Animal_Name": data.animal_name,
        "Behaviour": data.behaviour,
        "Intensity": data.intensity,
        "Abnormality_Percentage": data.animal_percentage,
        "Duration_Minutes": data.duration
    }])

    prediction = model.predict(input_data)[0]

#agfsdfg

    observation = Observation(
        keeper_id=data.keeper_id,
        zoo_id=data.zoo_id,
        animal_name=data.animal_name,
        behaviour=data.behaviour,
        intensity=data.intensity,
        animal_percentage=data.animal_percentage,
        duration=data.duration,
        date=data.date,
        hazard_prob=round(float(prediction), 2)
    )

    db.add(observation)
    db.commit()
    db.refresh(observation)
#adfasfasfadfsfasdfas

    return {
        "hazard_probability": round(float(prediction), 2)
    }

@app.get("/sendEmail")
def send_email():

    dotenv.load_dotenv()
    resend.api_key = os.getenv("RESEND_API")

    r = resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": "piyalibanerjee369@gmail.com",
        "subject": "🚨 EMERGENCY ALERT 🚨",
        "html": """
            <h2>🚨 EMERGENCY ALERT 🚨</h2>

            <p>
                Unusual animal behaviour has been detected at a nearby zoo.
            </p>

            <p>
                Please stay alert and take necessary precautions, as this may
                indicate a potential risk of an impending natural disaster
                in the area.
            </p>

            <p>
                <strong>Stay safe and stay informed.</strong>
            </p>
        """
    })

    return {
        "status": "Email sent"
    }