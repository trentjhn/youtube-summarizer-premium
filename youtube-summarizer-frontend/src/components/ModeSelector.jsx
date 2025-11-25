/**
 * ModeSelector Component
 * 
 * Allows users to choose between two summarization modes:
 * - Quick Summary: Fast, concise summary (5 components)
 * - In-Depth Analysis: Comprehensive, detailed analysis (8 components)
 * 
 * Props:
 *   - selectedMode: Current selected mode ("quick" or "indepth")
 *   - onSelectMode: Callback function when mode is changed
 */

import React from 'react';
import './ModeSelector.css';

const ModeSelector = ({ selectedMode, onSelectMode }) => {
  return (
    <div className="mode-selector-container">
      <label className="mode-selector-label">
        Choose Summarization Mode
      </label>
      
      <div className="mode-cards-wrapper">
        {/* Quick Summary Mode Card */}
        <div
          className={`mode-card ${selectedMode === 'quick' ? 'selected' : ''}`}
          onClick={() => onSelectMode('quick')}
          role="button"
          tabIndex={0}
          onKeyPress={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              onSelectMode('quick');
            }
          }}
        >
          <div className="mode-card-header">
            <span className="mode-icon">🚀</span>
            <h3 className="mode-title">Quick Summary</h3>
          </div>
          
          <p className="mode-description">
            Fast and concise overview of the video's key points
          </p>
          
          <ul className="mode-features">
            <li>✓ Essential insights only</li>
            <li>✓ 5-7 key points</li>
            <li>✓ ~30 seconds processing</li>
            <li>✓ Perfect for quick reviews</li>
          </ul>
          
          <div className="mode-footer">
            <span className="mode-time">⏱️ Fast</span>
            <span className="mode-detail">5 components</span>
          </div>
        </div>

        {/* In-Depth Analysis Mode Card */}
        <div
          className={`mode-card ${selectedMode === 'indepth' ? 'selected' : ''}`}
          onClick={() => onSelectMode('indepth')}
          role="button"
          tabIndex={0}
          onKeyPress={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              onSelectMode('indepth');
            }
          }}
        >
          <div className="mode-card-header">
            <span className="mode-icon">🔍</span>
            <h3 className="mode-title">In-Depth Analysis</h3>
          </div>
          
          <p className="mode-description">
            Comprehensive breakdown with detailed analysis and quotes
          </p>
          
          <ul className="mode-features">
            <li>✓ Comprehensive coverage</li>
            <li>✓ 10-15 detailed points</li>
            <li>✓ Key quotes & arguments</li>
            <li>✓ Perfect for research</li>
          </ul>
          
          <div className="mode-footer">
            <span className="mode-time">⏱️ Thorough</span>
            <span className="mode-detail">8 components</span>
          </div>
        </div>
      </div>
      
      {/* Mode Description */}
      <div className="mode-info">
        {selectedMode === 'quick' ? (
          <p className="mode-info-text">
            <strong>Quick mode</strong> provides a fast, concise summary perfect for getting the main points quickly.
          </p>
        ) : (
          <p className="mode-info-text">
            <strong>In-Depth mode</strong> provides comprehensive analysis including detailed breakdowns, key quotes, and argument structures.
          </p>
        )}
      </div>
    </div>
  );
};

export default ModeSelector;

