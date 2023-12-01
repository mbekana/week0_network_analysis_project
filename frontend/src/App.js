// App.js
import React, { useState, useEffect } from "react";
import "./App.css";
import CustomCard from "./components/CustomCard";
import SentimentAnalysisChart from "./components/SentimentAnalysisChart";
import Navbar from "./components/Navbar";
function App() {
  const [userStats, setUserStats] = useState({
    mostMessagesUser: [],
    mostReactionsUser: [],
    mostRepliesUser: [],
  });

  useEffect(() => {
    // Fetch data from your API endpoint
    fetch("http://localhost:5000/api/user_stats")
      .then((response) => response.json())
      .then((data) => setUserStats(data))
      .catch((error) => console.error("Error fetching user stats:", error));
  }, []);

  return (
    <>
      <Navbar />

      <div className="container">
        <div className="sentiment-analysis-container">
          {/* <h1 className="header">Sentiment Analysis</h1> */}
          <SentimentAnalysisChart />
        </div>

        <div>
          <div style={{ display: "block" }}>
            <h2 className="header">User Statistics</h2>
          </div>
          <div className="user-statistics-container">
            <CustomCard
              title="Most Messages User"
              count={userStats.most_messages_user?.[0]?.message_count || 0}
              user={userStats.most_messages_user?.[0]?.user || ""}
            />
            <CustomCard
              title="Most Reactions User"
              count={userStats.most_reactions_user?.[0]?.reaction_count || 0}
              user={userStats.most_reactions_user?.[0]?.user || ""}
            />
            <CustomCard
              title="Most Replies User"
              count={userStats.most_replies_user?.[0]?.reply_count || 0}
              user={userStats.most_replies_user?.[0]?.user || ""}
            />
          </div>
        </div>
      </div>
    </>
  );
}

export default App;
