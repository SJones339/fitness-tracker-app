import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Link } from "react-router-dom";
import '../styles/Dashboard.css';

interface Workout {
  workout_name: string;
  time: number;
  calories_burned: number;
  intensity: string;
}

interface FoodItem {
    name: string;
    calories: number;
}

interface DailyLog {
  date: string;
  foods: FoodItem[];
  workouts: Workout[];
  totalCaloriesConsumed: number;
  totalCaloriesBurned: number;
}

const Dashboard: React.FC = () => {
  const [selectedDate, setSelectedDate] = useState<string>(new Date().toISOString().split('T')[0]);
  const [dailyLog, setDailyLog] = useState<DailyLog | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDailyLog = async () => {
      setLoading(true);
      setError(null);

      console.log("Fetching data for date:", selectedDate); 
      //Get daily log data from backend for the date
      try {
        const response = await axios.get(`http://localhost:8000/api/daily-log?date=${selectedDate}`);
        console.log("API Response:", response); //debugging

        const data = response.data;
        console.log("Response Data:", data); //debugging

        if (!data) {
            throw new Error("No data received from the API."); //if didnt receive date from abckend throw error
        }
        //set the daily log to the data received or to empty/0 if no significant data
        setDailyLog({
          date: data.date || selectedDate,
          foods: data.foods || [],
          workouts: data.workouts || [],
          totalCaloriesConsumed: data.calories_consumed || 0,
          totalCaloriesBurned: data.calories_burned || 0,
        });

        console.log("Daily Log State After Update:", dailyLog); //debugging
      } catch (err: any) {
        console.error('Error fetching data:', err);
        setError(err.message || 'Failed to fetch data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchDailyLog();
  }, [selectedDate]);

  const handleDateChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      setSelectedDate(e.target.value);
      console.log("Selected Date Changed:", e.target.value); //debugging
  };

  if (error) {
    return <div className="error">{error}</div>; 
  }

  return (
    <div className="dashboard-page">
      <h2>Dashboard</h2>
      <div className="date-picker">
        <label htmlFor="date">Select Date:</label>
        <input
          type="date"
          id="date"
          value={selectedDate}
          onChange={handleDateChange}
        />
      </div>
      {loading ? (
        <p>Loading...</p>
      ) : dailyLog ? ( //Check to see if daily log is null
        <div className="log-details">
          <h3>{dailyLog.date}</h3>
          <div className="log-section">
            <h4>Food Items</h4> {/*Food Section*/}
            <ul>
              {dailyLog.foods.length > 0 ? (
                dailyLog.foods.map((item, index) => (
                  <li key={index}><strong>{item.name}</strong>: {item.calories} calories</li>
                ))
              ) : (
                <li>No food items logged.</li>
              )}
            </ul>
            <button>
              <Link to="/log-food">Log Food!</Link>
            </button>
          </div>
          <div className="log-section">
            <h4>Workouts</h4> {/*Workouts Section*/}
            <ul>
              {dailyLog.workouts.length > 0 ? (
                dailyLog.workouts.map((workout, index) => (
                  <li key={index}>
                    <strong>{workout.time} min {workout.intensity} {workout.workout_name}</strong>: {workout.calories_burned} calories burned
                  </li>
                ))
              ) : (
                <li>No workouts logged.</li>
              )}
            </ul>
            <button>
              <Link to="/log-workout">Log a Workout!</Link>
            </button>
          </div>
          <div className="log-summary">
            <p>Total Calories Consumed: {dailyLog.totalCaloriesConsumed}</p>
            <p>Total Calories Burned: {dailyLog.totalCaloriesBurned}</p>
          </div>
        </div>
      ) : (
        <p>No data available for the selected date.</p>
      )}
    </div>
  );
};

export default Dashboard;