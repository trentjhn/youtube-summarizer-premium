import React, { useState, useEffect } from 'react';
import Header from './Header';
import LeftSidebar from './LeftSidebar';
import MainContent from './MainContent';
import RightSidebar from './RightSidebar';
import './styles.css';

const SummaryView = ({ videoData }) => {
  const [leftSidebarOpen, setLeftSidebarOpen] = useState(true);
  const [rightSidebarOpen, setRightSidebarOpen] = useState(false);
  const [activeRightTab, setActiveRightTab] = useState('chat'); // 'chat', 'notes', 'export'
  const [readingProgress, setReadingProgress] = useState(0);
  const [highlightedParagraphId, setHighlightedParagraphId] = useState(null);
  
  // Calculate reading time (assuming 200 words per minute)
  const wordCount = videoData.summary.full_summary.reduce((acc, para) => 
    acc + para.content.split(' ').length, 0
  );
  const readingTime = Math.ceil(wordCount / 200);

  return (
    <div className="summary-view">
      <Header 
        videoData={videoData}
        readingTime={readingTime}
        readingProgress={readingProgress}
        onToggleLeftSidebar={() => setLeftSidebarOpen(!leftSidebarOpen)}
        onToggleRightSidebar={() => setRightSidebarOpen(!rightSidebarOpen)}
      />
      
      <div className="summary-view__body">
        {leftSidebarOpen && (
          <LeftSidebar 
            summary={videoData.summary}
            videoId={videoData.video_id}
            onKeyPointHover={setHighlightedParagraphId}
            onTopicClick={(sectionId) => {
              document.getElementById(`paragraph-${sectionId}`)?.scrollIntoView({ 
                behavior: 'smooth' 
              });
            }}
          />
        )}
        
        <MainContent 
          summary={videoData.summary}
          highlightedParagraphId={highlightedParagraphId}
          onScroll={(progress) => setReadingProgress(progress)}
        />
        
        {rightSidebarOpen && (
          <RightSidebar 
            activeTab={activeRightTab}
            onTabChange={setActiveRightTab}
            videoData={videoData}
          />
        )}
      </div>
    </div>
  );
};

export default SummaryView;

