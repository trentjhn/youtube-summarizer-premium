/**
 * ToneSelector Component
 * 
 * Allows users to select the output tone/style for the summary.
 * 
 * Tone Options:
 * - Objective (Default): Faithful to speaker's original tone
 * - Academic: Formal, structured, precise terminology
 * - Casual: Conversational, easy-to-read, friendly
 * - Skeptical: Critical evaluation, highlights assumptions
 * - Provocative: Strong language, controversial emphasis
 */

import React from 'react'
import { MessageSquare } from 'lucide-react'
import './ToneSelector.css'

const TONE_OPTIONS = [
  {
    value: 'Objective',
    label: 'Objective',
    description: 'Faithful to the speaker\'s original tone and intent',
    icon: '🎯'
  },
  {
    value: 'Academic',
    label: 'Academic',
    description: 'Formal language with precise terminology',
    icon: '🎓'
  },
  {
    value: 'Casual',
    label: 'Casual',
    description: 'Conversational and easy-to-read',
    icon: '💬'
  },
  {
    value: 'Skeptical',
    label: 'Skeptical',
    description: 'Critical evaluation of claims and assumptions',
    icon: '🤔'
  },
  {
    value: 'Provocative',
    label: 'Provocative',
    description: 'Strong language that stimulates debate',
    icon: '⚡'
  }
]

function ToneSelector({ tone, onToneChange, disabled }) {
  return (
    <div className="tone-selector">
      <div className="tone-header">
        <MessageSquare size={16} />
        <span className="tone-title">Output Tone</span>
      </div>

      <div className="tone-options">
        {TONE_OPTIONS.map((option) => (
          <label
            key={option.value}
            className={`tone-option ${tone === option.value ? 'selected' : ''} ${disabled ? 'disabled' : ''}`}
          >
            <input
              type="radio"
              name="tone"
              value={option.value}
              checked={tone === option.value}
              onChange={(e) => onToneChange(e.target.value)}
              disabled={disabled}
            />
            <div className="tone-content">
              <div className="tone-label">
                <span className="tone-icon">{option.icon}</span>
                <span className="tone-name">{option.label}</span>
              </div>
              <div className="tone-description">{option.description}</div>
            </div>
          </label>
        ))}
      </div>

      <div className="tone-hint">
        <small>
          The AI will adjust its writing style to match your selected tone across all summary components.
        </small>
      </div>
    </div>
  )
}

export default ToneSelector

