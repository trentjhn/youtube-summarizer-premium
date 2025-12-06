/**
 * VideoSegmentSelector Component
 * 
 * Allows users to specify a time range (start/end) for summarizing
 * only a specific segment of the video.
 * 
 * Features:
 * - MM:SS or HH:MM:SS format input
 * - "Summarize entire video" checkbox to disable inputs
 * - Real-time validation
 * - Clear visual feedback
 */

import React from 'react'
import { Clock } from 'lucide-react'
import './VideoSegmentSelector.css'

function VideoSegmentSelector({ startTime, endTime, onStartTimeChange, onEndTimeChange, disabled }) {
  const [useFullVideo, setUseFullVideo] = React.useState(true)
  const [startError, setStartError] = React.useState('')
  const [endError, setEndError] = React.useState('')

  // Validate timestamp format (MM:SS or HH:MM:SS)
  const validateTimestamp = (value, allowEnd = false) => {
    if (allowEnd && value.toLowerCase() === 'end') {
      return true
    }
    
    // MM:SS or HH:MM:SS format
    const timestampRegex = /^\d{1,2}:\d{2}(:\d{2})?$/
    return timestampRegex.test(value)
  }

  const handleStartTimeChange = (e) => {
    const value = e.target.value
    onStartTimeChange(value)
    
    if (value && !validateTimestamp(value, false)) {
      setStartError('Format: MM:SS or HH:MM:SS')
    } else {
      setStartError('')
    }
  }

  const handleEndTimeChange = (e) => {
    const value = e.target.value
    onEndTimeChange(value)
    
    if (value && !validateTimestamp(value, true)) {
      setEndError('Format: MM:SS or HH:MM:SS or "end"')
    } else {
      setEndError('')
    }
  }

  const handleCheckboxChange = (e) => {
    const checked = e.target.checked
    setUseFullVideo(checked)
    
    if (checked) {
      // Reset to defaults
      onStartTimeChange('00:00')
      onEndTimeChange('end')
      setStartError('')
      setEndError('')
    }
  }

  return (
    <div className="video-segment-selector">
      <div className="segment-header">
        <Clock size={16} />
        <span className="segment-title">Video Segment</span>
      </div>

      <div className="segment-checkbox">
        <label>
          <input
            type="checkbox"
            checked={useFullVideo}
            onChange={handleCheckboxChange}
            disabled={disabled}
          />
          <span>Summarize entire video</span>
        </label>
      </div>

      <div className="segment-inputs">
        <div className="time-input-group">
          <label htmlFor="start-time">Start Time</label>
          <input
            id="start-time"
            type="text"
            value={startTime}
            onChange={handleStartTimeChange}
            placeholder="00:00"
            disabled={disabled || useFullVideo}
            className={startError ? 'error' : ''}
          />
          {startError && <span className="error-message">{startError}</span>}
        </div>

        <div className="time-input-group">
          <label htmlFor="end-time">End Time</label>
          <input
            id="end-time"
            type="text"
            value={endTime}
            onChange={handleEndTimeChange}
            placeholder="end"
            disabled={disabled || useFullVideo}
            className={endError ? 'error' : ''}
          />
          {endError && <span className="error-message">{endError}</span>}
        </div>
      </div>

      <div className="segment-hint">
        <small>
          {useFullVideo 
            ? 'Full video will be summarized' 
            : 'Only the selected segment will be summarized (minimum 60 seconds)'}
        </small>
      </div>
    </div>
  )
}

export default VideoSegmentSelector

