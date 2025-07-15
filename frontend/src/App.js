import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [file, setFile] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    try {
      const response = await axios.post('http://127.0.0.1:5000/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResult(response.data);
    } catch (error) {
      console.error('Error:', error);
      setResult({ error: 'Upload failed' });
    }
    setLoading(false);
  };

  const simulateSteer = (position) => {
    if (position < -0.2) return 'Steer right';
    if (position > 0.2) return 'Steer left';
    return 'Straight';
  };

  return (
    <div style={{ padding: '20px', maxWidth: '600px', margin: 'auto' }}>
      <h1>AV Lane Detection Simulator</h1>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} accept="image/*,video/*" />
        <button type="submit" disabled={loading}>Process</button>
      </form>
      {loading && <p>Processing...</p>}
      {result && (
        <div>
          <p>Lane Position: {result.lane_position.toFixed(4)}</p>
          <p>FPS: {result.fps.toFixed(2)}</p>
          <p>Steering: {simulateSteer(result.lane_position)}</p>
          {result.output_path && (
            <div>
              <h3>Output:</h3>
              <img src={`http://127.0.0.1:5000/${result.output_path}`} alt="Processed" style={{ maxWidth: '100%' }} />
            </div>
          )}
          {result.error && <p>Error: {result.error}</p>}
        </div>
      )}
    </div>
  );
}

export default App;