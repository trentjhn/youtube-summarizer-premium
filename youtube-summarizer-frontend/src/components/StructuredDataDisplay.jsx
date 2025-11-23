import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { AlertCircle, Loader2 } from 'lucide-react'
import ExecutiveSummary from './ExecutiveSummary'
import KeyMetrics from './KeyMetrics'
import TimeStampedMoments from './TimeStampedMoments'

/**
 * StructuredDataDisplay Component
 * 
 * Fetches structured data from the API endpoint and displays it using
 * the ExecutiveSummary, KeyMetrics, and TimeStampedMoments components.
 * 
 * Props:
 *   - videoId (string): YouTube video ID to fetch structured data for
 *   - title (string): Video title for display
 */
export const StructuredDataDisplay = ({ videoId, title }) => {
  const [structuredData, setStructuredData] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!videoId) {
      setError('No video ID provided')
      setIsLoading(false)
      return
    }

    const fetchStructuredData = async () => {
      try {
        setIsLoading(true)
        setError(null)

        const response = await fetch(`/api/video/${videoId}/structured`)

        if (!response.ok) {
          const errorData = await response.json()
          throw new Error(errorData.error || `Failed to fetch structured data (${response.status})`)
        }

        const data = await response.json()
        setStructuredData(data.structured_data)
      } catch (err) {
        console.error('Error fetching structured data:', err)
        setError(err.message || 'Failed to load structured data')
      } finally {
        setIsLoading(false)
      }
    }

    fetchStructuredData()
  }, [videoId])

  if (isLoading) {
    return (
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <div className="flex items-center">
          <Loader2 className="animate-spin h-5 w-5 text-blue-600 mr-3" />
          <div>
            <h3 className="text-lg font-medium text-blue-800">Extracting Structured Data</h3>
            <p className="text-blue-700 text-sm mt-1">
              Analyzing video summary to extract key insights...
            </p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-6">
        <div className="flex items-start">
          <AlertCircle className="h-5 w-5 text-red-600 mr-3 flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="text-lg font-medium text-red-800">Error Loading Structured Data</h3>
            <p className="text-red-700 text-sm mt-1">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  if (!structuredData) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
        <p className="text-gray-600">No structured data available</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Executive Summary */}
      <ExecutiveSummary
        summary={structuredData.executive_summary}
        isLoading={false}
        error={null}
      />

      {/* Key Metrics */}
      <KeyMetrics
        metrics={structuredData.key_metrics || []}
        isLoading={false}
        error={null}
      />

      {/* Key Points */}
      {structuredData.key_points && structuredData.key_points.length > 0 && (
        <div className="bg-white rounded-lg p-6 border border-gray-200 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Key Points</h2>
          <ul className="space-y-3">
            {structuredData.key_points.map((point, index) => (
              <li key={index} className="flex items-start">
                <span className="flex-shrink-0 h-6 w-6 flex items-center justify-center rounded-full bg-blue-100 text-blue-700 text-sm font-medium mr-3">
                  {index + 1}
                </span>
                <span className="text-gray-700 leading-relaxed">{point}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Action Items */}
      {structuredData.action_items && structuredData.action_items.length > 0 && (
        <div className="bg-white rounded-lg p-6 border border-gray-200 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Action Items</h2>
          <ul className="space-y-3">
            {structuredData.action_items.map((item, index) => (
              <li key={index} className="flex items-start">
                <input
                  type="checkbox"
                  className="h-5 w-5 text-blue-600 rounded mt-0.5 mr-3 cursor-pointer"
                  aria-label={`Action item: ${item}`}
                />
                <span className="text-gray-700 leading-relaxed">{item}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Time-Stamped Moments */}
      <TimeStampedMoments
        timestamps={structuredData.timestamps || []}
        isLoading={false}
        error={null}
      />
    </div>
  )
}

StructuredDataDisplay.propTypes = {
  videoId: PropTypes.string.isRequired,
  title: PropTypes.string
}

export default StructuredDataDisplay

