/**
 * PersonalizationControlPanel Component
 * 
 * Unified control panel that consolidates:
 * - Mode selection (Quick vs In-Depth)
 * - Video segment selection (timestamp-based)
 * - Tone preference
 * 
 * Features:
 * - Collapsible "Advanced Options" section
 * - Clean, organized layout
 * - Responsive design
 * - Feature flag support
 */

import React, { useState } from 'react'
import { ChevronDown, ChevronUp, Settings } from 'lucide-react'
import ModeSelector from './ModeSelector'
import VideoSegmentSelector from './VideoSegmentSelector'
import ToneSelector from './ToneSelector'
import './PersonalizationControlPanel.css'

// Feature flag for Phase 4 personalization features
const USE_PERSONALIZATION_SUITE = true

function PersonalizationControlPanel({
  mode,
  onModeChange,
  startTime,
  endTime,
  onStartTimeChange,
  onEndTimeChange,
  tone,
  onToneChange,
  disabled
}) {
  const [showAdvanced, setShowAdvanced] = useState(false)

  const toggleAdvanced = () => {
    setShowAdvanced(!showAdvanced)
  }

  return (
    <div className="personalization-control-panel">
      {/* Mode Selection - Always visible */}
      <div className="panel-section">
        <ModeSelector mode={mode} onModeChange={onModeChange} disabled={disabled} />
      </div>

      {/* Advanced Options - Collapsible */}
      {USE_PERSONALIZATION_SUITE && (
        <div className="panel-section advanced-section">
          <button
            className="advanced-toggle"
            onClick={toggleAdvanced}
            disabled={disabled}
            type="button"
          >
            <Settings size={16} />
            <span>Advanced Options</span>
            {showAdvanced ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
          </button>

          {showAdvanced && (
            <div className="advanced-content">
              <VideoSegmentSelector
                startTime={startTime}
                endTime={endTime}
                onStartTimeChange={onStartTimeChange}
                onEndTimeChange={onEndTimeChange}
                disabled={disabled}
              />

              <ToneSelector
                tone={tone}
                onToneChange={onToneChange}
                disabled={disabled}
              />
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default PersonalizationControlPanel

