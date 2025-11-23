import React from 'react';

const Header = ({ videoData, readingTime, readingProgress, onToggleLeftSidebar, onToggleRightSidebar }) => {
  return (
    <header className="summary-header">
      <div className="summary-header__progress-bar" style={{ width: `${readingProgress}%` }} />
      
      <div className="summary-header__content">
        <div className="summary-header__left">
          <button onClick={onToggleLeftSidebar} className="icon-button">
            <span>☰</span>
          </button>
          <div className="summary-header__metadata">
            <h1 className="summary-header__title">{videoData.title}</h1>
            <div className="summary-header__info">
              <span className="reading-time">{readingTime} min read</span>
            </div>
          </div>
        </div>
        
        <div className="summary-header__actions">
          <button 
            className="btn btn-secondary" 
            onClick={() => navigator.clipboard.writeText(JSON.stringify(videoData.summary))}
          >
            Copy Summary
          </button>
          <button className="btn btn-secondary" onClick={onToggleRightSidebar}>
            Tools
          </button>
          <a 
            href={`https://www.youtube.com/watch?v=${videoData.video_id}`} 
            target="_blank" 
            rel="noopener noreferrer" 
            className="btn btn-primary"
          >
            Watch Video
          </a>
        </div>
      </div>
    </header>
  );
};

export default Header;

