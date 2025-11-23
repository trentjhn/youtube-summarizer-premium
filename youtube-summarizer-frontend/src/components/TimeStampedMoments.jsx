import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { Clock, ChevronDown, ChevronUp } from 'lucide-react'

/**
 * TimeStampedMoments Component
 * 
 * Displays time-stamped key moments from the video transcript.
 * Allows users to quickly navigate to important sections.
 * 
 * Props:
 *   - timestamps (array): Array of timestamp objects with time, topic, and key_point
 *   - isLoading (boolean): Whether data is being fetched
 *   - error (string): Error message if extraction failed
 *   - onTimestampClick (function): Callback when user clicks a timestamp
 */
export const TimeStampedMoments = ({ 
  timestamps = [], 
  isLoading = false, 
  error = null,
  onTimestampClick = null 
}) => {
  const [expandedIndex, setExpandedIndex] = useState(null)

  const toggleExpanded = (index) => {
    setExpandedIndex(expandedIndex === index ? null : index)
  }

  const handleTimestampClick = (timestamp) => {
    if (onTimestampClick) {
      onTimestampClick(timestamp)
    }
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-start">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <h3 className="text-sm font-medium text-red-800">Failed to load timestamps</h3>
            <p className="mt-1 text-sm text-red-700">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Key Moments</h2>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-20 bg-gray-200 rounded animate-pulse"></div>
          ))}
        </div>
      </div>
    )
  }

  if (!timestamps || timestamps.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Key Moments</h2>
        <p className="text-gray-500 text-sm">No timestamps found in the video</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg p-6 border border-gray-200 shadow-sm">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Key Moments</h2>
      <div className="space-y-3">
        {timestamps.map((timestamp, index) => (
          <div
            key={index}
            className="border border-gray-200 rounded-lg overflow-hidden hover:border-blue-300 transition-colors"
            role="article"
            aria-label={`Timestamp at ${timestamp.time}: ${timestamp.topic}`}
          >
            <button
              onClick={() => toggleExpanded(index)}
              className="w-full px-4 py-3 flex items-center justify-between bg-gray-50 hover:bg-gray-100 transition-colors"
              aria-expanded={expandedIndex === index}
              aria-controls={`timestamp-content-${index}`}
            >
              <div className="flex items-center flex-1 text-left">
                <Clock className="h-5 w-5 text-blue-600 mr-3 flex-shrink-0" />
                <div className="flex-1">
                  <div className="font-semibold text-gray-900">{timestamp.topic}</div>
                  <div className="text-sm text-gray-600">{timestamp.time}</div>
                </div>
              </div>
              <div className="ml-2 flex-shrink-0">
                {expandedIndex === index ? (
                  <ChevronUp className="h-5 w-5 text-gray-400" />
                ) : (
                  <ChevronDown className="h-5 w-5 text-gray-400" />
                )}
              </div>
            </button>

            {expandedIndex === index && (
              <div
                id={`timestamp-content-${index}`}
                className="px-4 py-3 bg-white border-t border-gray-200"
              >
                <p className="text-gray-700 text-sm leading-relaxed mb-3">
                  {timestamp.key_point}
                </p>
                <button
                  onClick={() => handleTimestampClick(timestamp)}
                  className="text-sm font-medium text-blue-600 hover:text-blue-700 transition-colors"
                  aria-label={`Jump to ${timestamp.time}`}
                >
                  Jump to this moment →
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

TimeStampedMoments.propTypes = {
  timestamps: PropTypes.arrayOf(
    PropTypes.shape({
      time: PropTypes.string.isRequired,
      topic: PropTypes.string.isRequired,
      key_point: PropTypes.string.isRequired
    })
  ),
  isLoading: PropTypes.bool,
  error: PropTypes.string,
  onTimestampClick: PropTypes.func
}

export default TimeStampedMoments

