import React, { useState, useEffect } from "react";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

export const options = {
  responsive: true,
  plugins: {
    legend: {
      position: "top",
    },
    title: {
      display: true,
      text: "Sentiment Analysis Chart",
    },
  },
};

const SentimentAnalysisChart = () => {
  const [sentimentData, setSentimentData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await fetch(
          "http://localhost:5000/api/sentiment_analysis"
        );
        const data = await response.json();
        setSentimentData(data);
      } catch (error) {
        console.error("Error fetching sentiment data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <p>Loading...</p>;
  }

  const labels = sentimentData.map((entry) => entry.month);

  const data = {
    labels,
    datasets: [
      {
        label: "Positive Sentiment",
        data: sentimentData.map((entry) => entry.average_positive_sentiment),
        borderColor: "rgb(75,192,192)",
        backgroundColor: "rgba(75,192,192,0.5)",
      },
      {
        label: "Negative Sentiment",
        data: sentimentData.map((entry) => entry.average_negative_sentiment),
        borderColor: "rgb(255, 99, 132)",
        backgroundColor: "rgba(255, 99, 132, 0.5)",
      },
    ],
  };

  return (
    <div style={{ width: "50%", marginLeft: "100px" }}>
      <h2>Sentiment Analysis Chart</h2>
      <Line options={options} data={data} />
    </div>
  );
};

export default SentimentAnalysisChart;
