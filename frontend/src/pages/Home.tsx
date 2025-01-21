import React from 'react';
import { Link } from 'react-router-dom';
import "../styles/Home.css"
//Home page of the app
const Home: React.FC = () => {
  return (
    <div className='homeStyle'>
      <h1>Welcome to Fitness Tracker</h1>
      <p>Track your calories and workouts seamlessly!</p>
      <Link to="/dashboard">
        <button className='buttonStyle'>Get Started</button>
      </Link>
    </div>
  );
};

export default Home;
