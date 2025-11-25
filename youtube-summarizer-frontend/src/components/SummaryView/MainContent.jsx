import React, { useEffect, useRef } from 'react';
import SummaryParagraph from './SummaryParagraph';
import DetailedAnalysis from './DetailedAnalysis';
import KeyQuotes from './KeyQuotes';
import Arguments from './Arguments';

const MainContent = ({ summary, highlightedParagraphId, onScroll }) => {
  const contentRef = useRef(null);

  // Check if this is an in-depth summary (has the additional fields)
  const isIndepthMode = summary.detailed_analysis || summary.key_quotes || summary.arguments;

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
        {/* Full Summary Paragraphs (always shown) */}
        {summary.full_summary.map((paragraph) => (
          <SummaryParagraph
            key={paragraph.id}
            paragraph={paragraph}
            isHighlighted={paragraph.id === highlightedParagraphId}
          />
        ))}

        {/* In-Depth Mode Sections (only shown for in-depth summaries) */}
        {isIndepthMode && (
          <div className="indepth-sections">
            <div className="indepth-divider">
              <span className="indepth-badge">In-Depth Analysis</span>
            </div>

            {summary.detailed_analysis && (
              <DetailedAnalysis analysisItems={summary.detailed_analysis} />
            )}

            {summary.key_quotes && (
              <KeyQuotes quotes={summary.key_quotes} />
            )}

            {summary.arguments && (
              <Arguments arguments={summary.arguments} />
            )}
          </div>
        )}
      </div>
    </main>
  );
};

export default MainContent;

