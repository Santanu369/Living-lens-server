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
from models import Keeper
from schemas import KeeperCreate

import models

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



class LoginRequest(BaseModel):
    username: str
    keeper_id: str

@app.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):

    keeper = db.query(Keeper).filter(
        Keeper.username == data.username,
        Keeper.keeper_id == data.keeper_id
    ).first()

    if not keeper:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or keeper ID"
        )

    return {
        "message": "Login successful",
        "keeper_id": keeper.keeper_id,
        "username": keeper.username
    }

@app.get("/")
def home():
    return {"message": "Zoo Sentinel ML server is running"}


@app.post("/predict")
def predict(data: PredictionInput):



    input_data = pd.DataFrame([{
        "Animal_Name": data.animal,
        "Behaviour": data.behaviour,
        "Intensity": data.intensity,
        "Abnormality_Percentage": data.abnormality_percentage,
        "Duration_Minutes": data.duration_minutes
    }])

    prediction = model.predict(input_data)[0]

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