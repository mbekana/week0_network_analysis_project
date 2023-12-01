// CustomCard.js

import React from "react";
import "./CustomCard.css";

const CustomCard = ({ title, count, user }) => {
  // Define card color based on title
  const getCardClass = () => {
    switch (title.toLowerCase()) {
      case "most messages user":
        return "most-messages-card";
      case "most reactions user":
        return "most-reactions-card";
      case "most replies user":
        return "most-replies-card";
      default:
        return "";
    }
  };

  return (
    <div className="custom-card ">
      <div className="card-header">{title}</div>
      <div className="card-body">
        <h5 className="card-title">{count}</h5>
        <p className="card-subtitle">{user}</p>
      </div>
    </div>
  );
};

export default CustomCard;
