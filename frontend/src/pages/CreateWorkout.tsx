import React, { useState } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import "../styles/CreateWorkout.css";

const CreateWorkout: React.FC = () => {
  const [name, setName] = useState<string>("");
  const [caloriesPerMinute, setCaloriesPerMinute] = useState<number | "">("");

  const handleCreateWorkout = async () => {
    if (!name || !caloriesPerMinute) {
      alert("Please provide valid input.");
      return;
    }

    try {
      //Sending data to backend to get response
      await axios.post("http://127.0.0.1:8000/create-workout", {
        name,
        calories_per_minute: caloriesPerMinute,
      });

      alert("Workout created successfully!");
      setName(""); 
      setCaloriesPerMinute("");
    } catch (error) {
      console.error("Failed to create workout", error);
      alert("Error creating workout. Please try again.");
    }
  };

  return (
    <div className="create-workout-page">
      <h2>Create Workout</h2>
      <div>
        <label htmlFor="name">Workout Name:</label>
        <input
          type="text"
          id="name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
      </div>
      <div>
        <label htmlFor="calories">Calories per Minute:</label>
        <input
          type="number"
          id="calories"
          value={caloriesPerMinute}
          onChange={(e) => setCaloriesPerMinute(parseFloat(e.target.value) || "")}
        />
      </div>
      <button onClick={handleCreateWorkout} disabled={!name || !caloriesPerMinute}>
        Create Workout
      </button>
      <button>
        <Link to="/log-workout">Back</Link>
      </button>
    </div>
  );
};

export default CreateWorkout;

