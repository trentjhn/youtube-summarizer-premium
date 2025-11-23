import React, { useEffect, useRef } from 'react';
import SummaryParagraph from './SummaryParagraph';

const MainContent = ({ summary, highlightedParagraphId, onScroll }) => {
  const contentRef = useRef(null);
  
  useEffect(() => {
    const handleScroll = () => {
      if (contentRef.current) {
        const { scrollTop, scrollHeight, clientHeight } = contentRef.current;
        const progress = (scrollTop / (scrollHeight - clientHeight)) * 100;
        onScroll(Math.min(progress, 100));
      }
    };
    
    const element = contentRef.current;
    element?.addEventListener('scroll', handleScroll);
    return () => element?.removeEventListener('scroll', handleScroll);
  }, [onScroll]);
  
  return (
    <main className="main-content" ref={contentRef}>
      <div className="main-content__inner">
        {summary.full_summary.map((paragraph) => (
          <SummaryParagraph 
            key={paragraph.id}
            paragraph={paragraph}
            isHighlighted={paragraph.id === highlightedParagraphId}
          />
        ))}
      </div>
    </main>
  );
};

export default MainContent;

