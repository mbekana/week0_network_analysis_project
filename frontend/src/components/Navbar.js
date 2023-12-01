import React from "react";
import "./Navbar.css"; // Assuming you have a CSS file for styling

const Navbar = () => {
  return (
    <nav className="navbar">
      <div className="navbar-brand">Slack Message Analysis</div>
      <ul className="navbar-nav">
        <li className="nav-item">Home</li>
        <li className="nav-item">Sentiment Analysis</li>
        <li className="nav-item">User Statistics</li>
      </ul>
    </nav>
  );
};

export default Navbar;
