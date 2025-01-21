import datetime
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import date

#by using sqlalchemy, can interact with SQL Databse with python instead of raw SQL
Base = declarative_base()

#Workouts table that will contain predefined workouts and their calories/min
class Workout(Base):
    __tablename__ = "workouts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    calories_per_minute = Column(Integer)

#Daily Logs table
class DailyLog(Base):
    __tablename__ = "daily_logs"
    id = Column(Integer, primary_key=True, index=True)
    
    date = Column(Date, unique=True) 
    calories_consumed = Column(Float, default=0.0)
    calories_burned = Column(Float, default=0.0)

    foods = Column(JSON, default=[]) 
    workouts = Column(JSON, default=[])



