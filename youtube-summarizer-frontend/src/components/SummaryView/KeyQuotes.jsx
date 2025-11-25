/**
 * KeyQuotes Component
 * 
 * Displays the key_quotes section for in-depth mode summaries.
 * Shows important verbatim quotes with context and attribution.
 */

import React from 'react';

const KeyQuotes = ({ quotes }) => {
  if (!quotes || quotes.length === 0) {
    return null;
  }

  return (
    <section className="key-quotes-section">
      <div className="section-header">
        <h2 className="section-title">
          <span className="section-icon">💬</span>
          Key Quotes
        </h2>
        <p className="section-description">
          Important verbatim quotes from the video
        </p>
      </div>
      
      <div className="quotes-list">
        {quotes.map((item, index) => (
          <div key={index} className="quote-item">
            <div className="quote-mark">"</div>
            <blockquote className="quote-text">
              {item.quote}
            </blockquote>
            <div className="quote-attribution">
              <span className="quote-speaker">— {item.speaker}</span>
              {item.context && (
                <span className="quote-context">{item.context}</span>
              )}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};

export default KeyQuotes;

