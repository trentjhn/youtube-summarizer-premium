/**
 * DetailedAnalysis Component
 * 
 * Displays the detailed_analysis section for in-depth mode summaries.
 * Shows deep dives into major topics with nuanced insights and context.
 */

import React from 'react';

const DetailedAnalysis = ({ analysisItems }) => {
  if (!analysisItems || analysisItems.length === 0) {
    return null;
  }

  return (
    <section className="detailed-analysis-section">
      <div className="section-header">
        <h2 className="section-title">
          <span className="section-icon">🔍</span>
          Detailed Analysis
        </h2>
        <p className="section-description">
          In-depth exploration of major topics and themes
        </p>
      </div>
      
      <div className="analysis-items">
        {analysisItems.map((item, index) => (
          <div key={index} className="analysis-item">
            <h3 className="analysis-topic">
              <span className="topic-number">{index + 1}</span>
              {item.topic}
            </h3>
            <div className="analysis-content">
              {item.analysis}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};

export default DetailedAnalysis;

