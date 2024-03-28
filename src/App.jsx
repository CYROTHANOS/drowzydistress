import React from "react";
import "./App.css"; // Import the CSS file

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Live Video Feed</h1>
      </header>
      <main className="App-main">
        <iframe
          src="http://localhost:5000/video_feed"
          title="ML Model Feed"
          width="100%"
          height="400px"
        ></iframe>
      </main>
    </div>
  );
}

export default App;
