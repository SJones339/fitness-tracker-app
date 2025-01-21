# fitness-tracker-app

## Description
The fitness tracker app is a full stack web application that allows users to create daily logs to track caloric intake and record workouts. This project employs React, FastAPI, Python, and PostgreSQL.

## Features
- **Logging Workouts**
    - Create workouts and set their cal/min value
    - Choose from workouts that have been created, an intensity level, and the time spent working out to log a workout
    - Calculate calories burned and add this to total calories burned for the day

- **Logging Foods**
    - Search for a food and obtain attributes (Calories, Protein, Fats, and Sugars)
    - Log the searched food and its caloric value which is added to total calories consumed for the day
    - Using USDA Food Database API to retrieve food data

- **Dashboard**
    - Select a date and show this date
    - Show the Food items and their caloric value with button underneath to log Food
    - Show Workouts and the calories burned with button underneat to Log Workouts
    - Show Total calories consumed/burned at the bottom

## Technologies Used

### Frontend
- React, TypeScript, Axios (API Communication), React Route, CSS

### Backend
- FastAPI, PostgreSQL (storing daily log and workout info)

Utilized AI tools for assistance in styling and resolving development challenges

## Future Enhancements
 - Gamification (Goal Setting)
 - Integrate AI (workout creation, meal plans)
 - Debugging:
    - Creating a duplicate workout should say workout already exists instead of throwing error
    - Be able to log workouts/foods from previous days instead of just being able to view what was logged on a previous day
    - Resolve CSS issue

