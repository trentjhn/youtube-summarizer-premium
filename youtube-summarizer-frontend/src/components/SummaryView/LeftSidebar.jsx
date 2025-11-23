import React from 'react';
import QuickTakeaway from './QuickTakeaway';
import KeyPointsList from './KeyPointsList';
import TopicsList from './TopicsList';
import TimestampsList from './TimestampsList';

const LeftSidebar = ({ summary, videoId, onKeyPointHover, onTopicClick }) => {
  return (
    <aside className="left-sidebar">
      <QuickTakeaway text={summary.quick_takeaway} />
      
      <section className="sidebar-section">
        <h3>Key Points</h3>
        <KeyPointsList 
          points={summary.key_points} 
          onHover={onKeyPointHover}
        />
      </section>
      
      <section className="sidebar-section">
        <h3>Topics</h3>
        <TopicsList 
          topics={summary.topics} 
          onClick={onTopicClick}
        />
      </section>
      
      {summary.timestamps && summary.timestamps.length > 0 && (
        <section className="sidebar-section">
          <h3>Key Moments</h3>
          <TimestampsList 
            timestamps={summary.timestamps}
            videoId={videoId}
          />
        </section>
      )}
    </aside>
  );
};

export default LeftSidebar;

