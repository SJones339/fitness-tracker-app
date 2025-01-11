from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import User, Workout, DailyLog
import datetime
from dotenv import load_dotenv
import requests
import os

load_dotenv(dotenv_path="../../.env")

food_api_key = os.getenv("FOOD_API_KEY")


#Initialize the app
app = FastAPI()

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

#Create new user
@app.post("/users/")
def create_user(username: str, db: Session = Depends(get_db)):
    user = User(username=username)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

#Get all users
@app.get("/users/")
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

#---------------------------- CREATING AND LOGGING WORKOUTS -----------------------------#
#Create Workout
@app.post("/create-workout")
def create_workout(name: str, calories_per_minute: float, db: Session = Depends(get_db)):
    if db.query(Workout).filter_by(name=name).first():
        raise HTTPException(status_code=400, detail="Workout already exists.")

    workout = Workout(name=name, calories_per_minute=calories_per_minute)
    db.add(workout)
    db.commit()

    return {"message": "Workout created successfully.", "workout": {"name": name, "calories_per_minute": calories_per_minute}}

#Log Workout
@app.post("/log-workout")
def log_workout(user_id: int, workout_id: int, time: int, intensity: str, db: Session = Depends(get_db)):
    
    #Find the workout and check if it exists
    workout = db.query(Workout).filter_by(id=workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found.")

    #Get the intensity factor and calculate total calories burned
    intensity_factor = INTENSITY_ADJUSTMENT.get(intensity.lower(), 1.0)
    calories_burned = workout.calories_per_minute * time * intensity_factor

    #Get the date and teh log for today (check if it exists if not make a new one)
    today = datetime.date.today()
    daily_log = db.query(DailyLog).filter_by(user_id=user_id, date=today).first()
    if not daily_log:
        daily_log = DailyLog(user_id=user_id, date=today)
        db.add(daily_log)
        #db.flush() 
    
    #Make sure a list of workouts is initialized as part of teh daily log
    if daily_log.workouts is None:
        daily_log.workouts = []

    #Make sure the calories burned is initialized
    if daily_log.calories_burned is None:
        daily_log.calories_burned = 0.0
    
    #Append all of the info for a workout 
    daily_log.workouts.append({
        "workout_name": workout.name, 
        "time": time, 
        "calories_burned": calories_burned,
        "intensity": intensity
    })
    
    
    daily_log.calories_burned += calories_burned
    
    #Mark teh workouts field and calories burned as updated**
    db.query(DailyLog).filter_by(user_id=user_id, date=today).update({
        "workouts": daily_log.workouts,
        "calories_burned": daily_log.calories_burned
    })
    
    db.commit()

    return {"message": "Workout logged successfully.", "daily_log": daily_log.workouts}


#----------------------------FOOD API DATABASE-------------------------------------------#
food_url = "https://api.nal.usda.gov/fdc/v1/foods/search"

#Log Food
@app.post("/log-food")
def log_food(user_id: int, food_name: str, db: Session = Depends(get_db)):
    #Get food details from USDA
    params = {"query": food_name, "api_key": food_api_key}
    response = requests.get(food_url, params=params)

    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch food data.")

    data = response.json()
    if not data.get("foods"):
        raise HTTPException(status_code=404, detail="Food not found.")

    #Food Data
    food_data = data["foods"][0]
    food_nutrients = food_data.get("foodNutrients", [])

    #Caloric Value (keyword=Energy)
    calories = None
    for nutrient in food_nutrients:
        if nutrient["nutrientName"] == "Energy":
            calories = nutrient["value"]
            break
    
    if calories is None:
        raise HTTPException(status_code=500, detail="Caloric data not available for this food.")

    #Get the date and log for today (check if it exists if not make a new one)
    today = datetime.date.today()
    daily_log = db.query(DailyLog).filter_by(user_id=user_id, date=today).first()
    if not daily_log:
        daily_log = DailyLog(user_id=user_id, date=today, foods=[], calories_consumed=0.0, workouts=[], calories_burned=0.0)
        db.add(daily_log)

    #Make sure teh list of foods is intialized as a list
    if daily_log.foods is None:
        daily_log.foods = []

    #Add the food name/calories to list
    new_food = {"name": food_name, "calories": calories}
    daily_log.foods.append(new_food)

    #Add to total calories consumed
    daily_log.calories_consumed += calories

    #Mark the foods and calories consumed as updated so it will retain previously logged foods
    db.query(DailyLog).filter_by(user_id=user_id, date=today).update({
        "foods": daily_log.foods,
        "calories_consumed": daily_log.calories_consumed
    })

    db.commit()

    return {"message": "Food logged successfully.", "daily_log": daily_log.foods}

#-----------------------------------------------------------------------#
#Get Daily Log
@app.get("/daily-log")
def get_daily_log(user_id: int, date: str, db: Session = Depends(get_db)):
    date_obj = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    daily_log = db.query(DailyLog).filter_by(user_id=user_id, date=date_obj).first()
    if not daily_log:
        raise HTTPException(status_code=404, detail="Daily log not found.")

    return {
        "date": daily_log.date,
        "calories_consumed": daily_log.calories_consumed,
        "calories_burned": daily_log.calories_burned,
        "foods": daily_log.foods,
        "workouts": daily_log.workouts,
    }


#to run, cd to backend and run uvicorn app.main:app --reload. If want to reset 
# database, just run database.py