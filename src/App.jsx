import React, { useState, useEffect } from "react";
import "./App.css";

function formatTime(duration) {
  const seconds = Math.floor(duration);
  const milliseconds = Math.floor((duration - seconds) * 1000);
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;

  return `${minutes}:${
    remainingSeconds < 10 ? "0" : ""
  }${remainingSeconds}.${milliseconds}`;
}

function App() {
  const [timerData, setTimerData] = useState({
    activeDuration: 0,
    drowsyDuration: 0,
    sleepingDuration: 0,
    totalSleepingDuration: 0,
    activePercentage: 0,
    drowsyPercentage: 0,
    sleepingPercentage: 0,
  });

  const fetchTimerData = async () => {
    const response = await fetch("http://localhost:5000/timer");
    if (response.ok) {
      const data = await response.json();
      setTimerData(data);
    }
  };

  useEffect(() => {
    const timer = setInterval(fetchTimerData, 1000);
    return () => clearInterval(timer);
  }, []);

  const stopAlarm = async () => {
    await fetch("http://localhost:5000/stop_alarm", {
      method: "POST",
    });
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Live Video Feed</h1>
      </header>
      <main className="App-main">
        <div className="iframe-container">
          <iframe
            src="http://localhost:5000/video_feed"
            title="ML Model Feed"
            width="100%"
            height="480px"
          ></iframe>
        </div>
        <div className="timer-container">
          <p className="timer">
            Active Duration: {formatTime(timerData.activeDuration)},{" "}
            {timerData.activePercentage.toFixed(2)}%
          </p>
          <p className="timer">
            Drowsy Duration: {formatTime(timerData.drowsyDuration)},{" "}
            {timerData.drowsyPercentage.toFixed(2)}%
          </p>
          <p className="timer">
            Sleeping Duration: {formatTime(timerData.sleepingDuration)},{" "}
            {timerData.sleepingPercentage.toFixed(2)}%
          </p>
          <button onClick={stopAlarm}>Stop Alarm</button>
        </div>
      </main>
    </div>
  );
}

export default App;
