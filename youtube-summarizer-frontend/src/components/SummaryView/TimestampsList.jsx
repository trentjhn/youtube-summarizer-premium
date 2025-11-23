import React from 'react';

const TimestampsList = ({ timestamps, videoId }) => {
  const handleTimestampClick = (time) => {
    if (!videoId) return;
    
    // Convert HH:MM:SS or MM:SS to seconds
    const parts = time.split(':').map(Number);
    let seconds = 0;
    
    if (parts.length === 3) {
      // HH:MM:SS
      seconds = parts[0] * 3600 + parts[1] * 60 + parts[2];
    } else if (parts.length === 2) {
      // MM:SS
      seconds = parts[0] * 60 + parts[1];
    }
    
    // Open YouTube video at specific timestamp
    const url = `https://www.youtube.com/watch?v=${videoId}&t=${seconds}s`;
    window.open(url, '_blank');
  };
  
  return (
    <ul className="timestamps-list">
      {timestamps.map((timestamp, index) => (
        <li 
          key={index}
          className="timestamp-item"
          onClick={() => handleTimestampClick(timestamp.time)}
        >
          <span className="timestamp-time">{timestamp.time}</span>
          <span className="timestamp-description">{timestamp.description}</span>
        </li>
      ))}
    </ul>
  );
};

export default TimestampsList;

