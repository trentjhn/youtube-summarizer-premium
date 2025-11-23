import React from 'react';

const KeyPointsList = ({ points, onHover }) => {
  return (
    <ul className="key-points-list">
      {points.map((point, index) => (
        <li 
          key={index}
          className="key-point-item"
          onMouseEnter={() => onHover && onHover(index + 1)}
          onMouseLeave={() => onHover && onHover(null)}
        >
          <span className="key-point-bullet">•</span>
          <span className="key-point-text">{point}</span>
        </li>
      ))}
    </ul>
  );
};

export default KeyPointsList;

