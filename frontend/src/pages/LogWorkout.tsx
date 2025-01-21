import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/LogWorkout.css';

interface Workout {
  id: number;
  name: string;
}

const LogWorkout: React.FC = () => {
  const [workouts, setWorkouts] = useState<Workout[]>([]);
  const [selectedWorkout, setSelectedWorkout] = useState<string>('');
  const [intensity, setIntensity] = useState<string>('light');
  const [time, setTime] = useState<string>('');
  const navigate = useNavigate();

  useEffect(() => {
    const fetchWorkouts = async () => {
      try {
        //getting workouts data from the backend 
        const response = await fetch('http://127.0.0.1:8000/workouts');
        if (response.ok) {
          const data = await response.json();
          setWorkouts(Array.isArray(data) ? data : []); 
        } else {
          console.error('Failed to fetch workouts:', response.statusText);
          setWorkouts([]); 
        }
      } catch (error) {
        console.error('Error fetching workouts:', error);
        setWorkouts([]); 
      }
    };
  
    fetchWorkouts();
  }, []);
  

  const handleLogWorkout = async () => {
    //makes sure user enters all items before logging
    if (!selectedWorkout || !time) {
      alert('Please fill in all fields!');
      return;
    }
  
    try {
      //Get data from backend for logging workouts
      const response = await fetch('http://127.0.0.1:8000/log-workout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          workout_id: selectedWorkout,
          time: Number(time),
          intensity,
        }),
      });
  
      if (response.ok) {
        alert('Workout logged successfully!');
        navigate('/dashboard');
      } else {
        console.error('Failed to log workout');
      }
    } catch (error) {
      console.error('Error logging workout:', error);
    }
  };
  
  

  return (
    <div className="log-workout-container">
      <h2>Log a Workout</h2>
      {workouts.length === 0 ? (
        <div>
          <p className="no-workouts-message">
            No workouts available. Create one to get started!
          </p>
        </div>
      ) : null}
  
      <form className="log-workout-form" onSubmit={(e) => e.preventDefault()}>
        <select
          value={selectedWorkout}
          onChange={(e) => setSelectedWorkout(e.target.value)}
        >
          <option value="">Select a workout</option>
          {workouts.map((workout) => (
            <option key={workout.id} value={workout.id}>
              {workout.name}
            </option>
          ))}
        </select>
  
        <select
          value={intensity}
          onChange={(e) => setIntensity(e.target.value)}
        >
          <option value="light">Light</option>
          <option value="moderate">Moderate</option>
          <option value="intense">Intense</option>
        </select>
  
        <input
          type="number"
          placeholder="Time spent (minutes)"
          value={time}
          onChange={(e) => setTime(e.target.value)}
        />
  
        <button type="button" onClick={handleLogWorkout}>
          Log Workout
        </button>
      </form>
  
      <button
        className="create-workout-button"
        onClick={() => navigate('/create-workout')}
      >
        Create Workout!
      </button>
  
      <button className="back-button" onClick={() => navigate('/dashboard')}>
        Back to Dashboard
      </button>
    </div>
  );
  
};

export default LogWorkout;
