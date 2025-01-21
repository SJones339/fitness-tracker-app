import React, { useState } from 'react';
import axios from 'axios';

interface FoodPreview {
  name: string;
  calories: number;
  protein: number;
  fats: number;
  sugars: number;
}

const LogFood: React.FC = () => {
  const [foodName, setFoodName] = useState<string>('');
  const [foodPreview, setFoodPreview] = useState<FoodPreview | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleSearch = async () => {
    console.log('Search initiated for:', foodName);
    try {
      setError(null);
      setSuccessMessage(null);

        console.log("Making request to:", `/api/search-food?food_name=${foodName}`); //debugging
      //Get the data from teh backend (searching for the food)
      const response = await axios.get(`http://localhost:8000/api/search-food?food_name=${foodName}`);

      console.log('Search response status:', response.status); //debugging items
      console.log('Search response data:', response.data);

      if (response.status === 404) {
        setError('Food not found. Please try a different search term.');
        setFoodPreview(null); //Clear the preview if food is not found
      } else {
        setFoodPreview(response.data);
      }
    } catch (err: any) { //error handling
      console.error('Search error:', err); 
      console.error('Search error response:', err.response); 
      setError(err.response?.data?.detail || err.message || 'Failed to search for food.'); 
      setFoodPreview(null);
    }
  };

  //now moving onto logging food
  const handleLogFood = async () => {
    if (!foodPreview) {
      console.warn('Log food attempted with no preview data.');
      return;
    }

    console.log('Logging food:', foodPreview.name); //debugging
    try {
      setError(null);
      setSuccessMessage(null);
      //Get the data from the backend
      const response = await axios.post('http://localhost:8000/api/log-food', { food_name: foodPreview.name });
      console.log('Log food response:', response.data);
      setSuccessMessage(response.data.message);
      setFoodPreview(null); 
      setFoodName(""); //Clear input field
    } catch (err: any) { //error handling
      console.error('Log food error:', err);
      console.error('Log food error response:', err.response);
      setError(err.response?.data?.detail || err.message || 'Failed to log food.');
    }
  };

  return (
    <div className="log-food-page">
      <h2>Log Food</h2>
      <div className="search-section">
        <input
          type="text"
          placeholder="Enter food name"
          value={foodName}
          onChange={(e) => setFoodName(e.target.value)}
        />
        <button onClick={handleSearch}>Search</button>
      </div>
      {error && <div className="error">{error}</div>}
      {successMessage && <div className="success">{successMessage}</div>}
      {foodPreview && (
        <div className="food-preview">
          <h3>Food Information</h3>
          <p><strong>Name:</strong> {foodPreview.name}</p>
          <p><strong>Calories:</strong> {foodPreview.calories}</p>
          <p><strong>Protein:</strong> {foodPreview.protein}g</p>
          <p><strong>Fats:</strong> {foodPreview.fats}g</p>
          <p><strong>Sugars:</strong> {foodPreview.sugars}g</p>
          <button onClick={handleLogFood}>Log Food</button>
        </div>
      )}
    </div>
  );
};

export default LogFood;