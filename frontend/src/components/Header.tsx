//Header is usable in all pages so keep in components folder
import React from 'react';
import { Link } from 'react-router-dom';
import "../styles/Header.css";

const Header: React.FC = () => {
  return (
    <header className="headerStyle">
      <nav className="navStyle">
        <h1 className="logoStyle">Fitness Tracker</h1>
        <ul className="navListStyle">
          <li><Link to="/" className="linkStyle">Home</Link></li>
          <li><Link to="/dashboard" className="linkStyle">Dashboard</Link></li>
        </ul>
      </nav>
    </header>
  );
};

export default Header;
