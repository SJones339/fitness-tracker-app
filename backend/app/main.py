from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import Workout, DailyLog
import datetime
from dotenv import load_dotenv
import requests
import os
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

load_dotenv(dotenv_path="../../.env")

food_api_key = os.getenv("FOOD_API_KEY")


#Initialize the app
app = FastAPI()

#This allows for communication between frontend and backend (avoid CORS error)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

#This will allow to create a session directly and not have to
#open and close the DB in EVERY route
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#Intensity scalars
INTENSITY_ADJUSTMENT = {
    "light": 0.8,
    "moderate": 1.0,
    "intense": 1.2
}

#---------------------------- CREATING AND LOGGING WORKOUTS -----------------------------#
#Pydantic model to convert JSON request from frontend into readable data
class WorkoutCreate(BaseModel):
    name: str
    calories_per_minute: int


class LogWorkoutRequest(BaseModel):
    workout_id: int
    intensity: str
    time: int

#Create Workout
@app.post("/create-workout")
def create_workout(workout: WorkoutCreate, db: Session = Depends(get_db)):
    #check if the workout exists already
    if db.query(Workout).filter_by(name=workout.name).first():
        raise HTTPException(status_code=400, detail="Workout already exists.")

    #create new workout instance and add it to the database
    new_workout = Workout(name=workout.name, calories_per_minute=workout.calories_per_minute)
    db.add(new_workout)
    db.commit()

    return {
        "message": "Workout created successfully.",
        "workout": {"name": new_workout.name, "calories_per_minute": new_workout.calories_per_minute},
    }
    
#Get all Workouts
@app.get("/workouts")
def get_workouts(db: Session = Depends(get_db)):
    workouts = db.query(Workout).all()
    workouts_list = []
    for workout in workouts:
        workouts_list.append({"id": workout.id, "name": workout.name})
    return workouts_list

#Log Workout
@app.post("/log-workout")
def log_workout(log_request: LogWorkoutRequest, db: Session = Depends(get_db)):
    workout_id = log_request.workout_id
    time = log_request.time
    intensity = log_request.intensity

    #check if workout exists
    workout = db.query(Workout).filter_by(id=workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found.")

    #Use intensity factor to adjust total calories burned
    intensity_factor = INTENSITY_ADJUSTMENT.get(intensity.lower(), 1.0)
    calories_burned = workout.calories_per_minute * time * intensity_factor

    #Check if daily log exists for a date, if not create a new one
    today = datetime.date.today()
    daily_log = db.query(DailyLog).filter_by(date=today).first()
    if not daily_log:
        daily_log = DailyLog(date=today)
        db.add(daily_log)

    #Make sure teh workouts in daily log is initialized***
    if daily_log.workouts is None:
        daily_log.workouts = []

    #Make sure the calories bruned is initialized***
    if daily_log.calories_burned is None:
        daily_log.calories_burned = 0.0
    
    #Add all of this info to the daily log
    daily_log.workouts.append({
        "workout_name": workout.name, 
        "time": time, 
        "calories_burned": calories_burned,
        "intensity": intensity
    })

    #Update the total calories burned in the daily log
    daily_log.calories_burned += calories_burned
    
    #Mark the workouts and calories burned as updated
    db.query(DailyLog).filter_by(date=today).update({
        "workouts": daily_log.workouts,
        "calories_burned": daily_log.calories_burned
    })

    db.commit()

    return {"message": "Workout logged successfully.", "daily_log": daily_log.workouts}

#----------------------------FOOD API DATABASE-------------------------------------------#
food_url = "https://api.nal.usda.gov/fdc/v1/foods/search"

#Pydantic model to convert JSON request from frontend into readable data
class LogFoodRequest(BaseModel):
    food_name: str
    
@app.post("/api/log-food")
def log_food(request: LogFoodRequest, db: Session = Depends(get_db)):
    #Get food data from USDA Food Database
    params = {"query": request.food_name, "api_key": food_api_key}
    response = requests.get(food_url, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch food data.")

    data = response.json()
    if not data.get("foods"):
        raise HTTPException(status_code=404, detail="Food not found.")
    
    #Get the food data from teh response and get calories (energy)
    food_data = data["foods"][0]
    food_nutrients = food_data.get("foodNutrients", [])
    calories = None
    for nutrient in food_nutrients:
        if nutrient["nutrientName"] == "Energy":
            calories = nutrient["value"]
            break
    
    if calories is None:
        raise HTTPException(status_code=500, detail="Caloric data not available for this food.")

    #Check if daily log exists for a date, if not create a new one
    today = datetime.date.today()
    daily_log = db.query(DailyLog).filter_by(date=today).first()
    if not daily_log:
        daily_log = DailyLog(date=today)
        db.add(daily_log)

    #Make sure calories consumed is init
    if daily_log.calories_consumed is None:
        daily_log.calories_consumed = 0

    #Make sure the foods list is init
    if daily_log.foods is None:
        daily_log.foods = []

    #Add the food and its caloric value to teh daily log food list
    new_food = {"name": request.food_name, "calories": calories}
    daily_log.foods.append(new_food)
    
    #Update total calories consumed in the daily log
    daily_log.calories_consumed += calories
    
    #Mark the foods and calories consumed as updated so it will retain previously logged foods
    db.query(DailyLog).filter_by(date=today).update({
        "foods": daily_log.foods,
        "calories_consumed": daily_log.calories_consumed
    })

    db.commit()

    return {"message": "Food logged successfully.", "daily_log": daily_log.foods}

@app.get("/api/search-food")
def search_food(food_name: str):
    #USDA Food API to search for food
    params = {"query": food_name, "api_key": food_api_key}
    response = requests.get(food_url, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch food data from the USDA API.")

    data = response.json()
    if not data.get("foods"):
        raise HTTPException(status_code=404, detail="Food not found.")

    #Get the first food and extract calories, protein, fats, and sugars
    food_data = data["foods"][0]
    food_nutrients = food_data.get("foodNutrients", [])
    calories = None
    for nutrient in food_nutrients:
        if nutrient["nutrientName"] == "Energy":
            calories = nutrient["value"]
            break

    protein = None
    for nutrient in food_nutrients:
        if nutrient["nutrientName"] == "Protein":
            protein = nutrient["value"]
            break

    fats = None
    for nutrient in food_nutrients:
        if nutrient["nutrientName"] == "Total lipid (fat)":
            fats = nutrient["value"]
            break

    sugars = None
    for nutrient in food_nutrients:
        if nutrient["nutrientName"] == "Total Sugars":
            sugars = nutrient["value"]
            break


    #Return all of this info
    return {
        "name": food_data["description"],
        "calories": calories or 0,
        "protein": protein or 0,
        "fats": fats or 0,
        "sugars": sugars or 0,
    }


#-----------------------------------------------------------------------#
#Get Daily Log
@app.get("/api/daily-log")
def get_daily_log(date: str, db: Session = Depends(get_db)):
    #Get the date and corresponding log because this is what differentiates different daily logs
    date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    daily_log = db.query(DailyLog).filter_by(date=date_obj).first()
    #If there is no daily log then just return empty items so somethign still displayed on screen
    if not daily_log:
        return {"date": date, "foods": [], "workouts": [], "total_calories": 0, "total_burned": 0}

    #Return logged attributes of the daily log, and the total calories consumed/burned
    return {
        "date": daily_log.date,
        "calories_consumed": daily_log.calories_consumed,
        "calories_burned": daily_log.calories_burned,
        "foods": daily_log.foods,
        "workouts": daily_log.workouts,
    }


#to run, cd to backend and run uvicorn app.main:app --reload. If want to reset 
# database, just run database.py