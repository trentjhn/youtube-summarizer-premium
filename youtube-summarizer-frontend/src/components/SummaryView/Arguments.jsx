/**
 * Arguments Component
 * 
 * Displays the arguments section for in-depth mode summaries.
 * Shows main claims, supporting evidence, and counterpoints.
 */

import React from 'react';

const Arguments = ({ arguments: argumentsList }) => {
  if (!argumentsList || argumentsList.length === 0) {
    return null;
  }

  return (
    <section className="arguments-section">
      <div className="section-header">
        <h2 className="section-title">
          <span className="section-icon">⚖️</span>
          Arguments & Claims
        </h2>
        <p className="section-description">
          Main arguments, evidence, and counterpoints
        </p>
      </div>
      
      <div className="arguments-list">
        {argumentsList.map((item, index) => (
          <div key={index} className="argument-item">
            <div className="argument-number">{index + 1}</div>
            <div className="argument-content">
              <div className="argument-claim">
                <h4 className="claim-label">Claim</h4>
                <p className="claim-text">{item.claim}</p>
              </div>
              
              {item.evidence && (
                <div className="argument-evidence">
                  <h4 className="evidence-label">Evidence</h4>
                  <p className="evidence-text">{item.evidence}</p>
                </div>
              )}
              
              {item.counterpoint && (
                <div className="argument-counterpoint">
                  <h4 className="counterpoint-label">Counterpoint</h4>
                  <p className="counterpoint-text">{item.counterpoint}</p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};

export default Arguments;

