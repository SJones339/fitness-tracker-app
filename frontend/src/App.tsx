import React, { Suspense } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';

//lazy loads components only when they are needed. This helps to reduce load
//and only download in small bundles
//Suspense fallback is what is shown when route is loading
const Home = React.lazy(() => import('./pages/Home'));
const Dashboard = React.lazy(() => import('./pages/Dashboard'));
const LogWorkout = React.lazy(() => import('./pages/LogWorkout'));
const CreateWorkout = React.lazy(() => import('./pages/CreateWorkout'));
const LogFood = React.lazy(() => import('./pages/LogFood'))


const App: React.FC = () => {
  return (
    <Router>
      <Header />
      <main>
        <Suspense fallback={<div>Loading...</div>}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/create-workout" element={<CreateWorkout />} />
            <Route path="/log-workout" element={<LogWorkout />} /> 
            <Route path="/create-workout" element={<CreateWorkout />} />
            <Route path="/log-food" element={<LogFood />} />
          </Routes>
        </Suspense>
      </main>
    </Router>
  );
};

export default App;

