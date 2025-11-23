import React from 'react'
import PropTypes from 'prop-types'
import { Lightbulb } from 'lucide-react'

/**
 * ExecutiveSummary Component
 * 
 * Displays a 30-second takeaway of the video content.
 * Provides a quick, high-level overview for busy professionals.
 * 
 * Props:
 *   - summary (string): The executive summary text
 *   - isLoading (boolean): Whether data is being fetched
 *   - error (string): Error message if extraction failed
 */
export const ExecutiveSummary = ({ summary, isLoading = false, error = null }) => {
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
            <h3 className="text-sm font-medium text-red-800">Failed to load summary</h3>
            <p className="mt-1 text-sm text-red-700">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <div className="flex items-center mb-4">
          <Lightbulb className="h-5 w-5 text-yellow-500 mr-2" />
          <h2 className="text-lg font-semibold text-gray-900">30-Second Takeaway</h2>
        </div>
        <div className="space-y-3">
          <div className="h-4 bg-gray-200 rounded animate-pulse w-full"></div>
          <div className="h-4 bg-gray-200 rounded animate-pulse w-5/6"></div>
          <div className="h-4 bg-gray-200 rounded animate-pulse w-4/6"></div>
        </div>
      </div>
    )
  }

  if (!summary) {
    return (
      <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
        <div className="flex items-center mb-4">
          <Lightbulb className="h-5 w-5 text-gray-400 mr-2" />
          <h2 className="text-lg font-semibold text-gray-900">30-Second Takeaway</h2>
        </div>
        <p className="text-gray-500 text-sm">No summary available</p>
      </div>
    )
  }

  return (
    <div className="bg-gradient-to-br from-yellow-50 to-amber-50 rounded-lg p-6 border border-yellow-200 shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start">
        <Lightbulb className="h-6 w-6 text-yellow-500 mr-3 flex-shrink-0 mt-1" />
        <div className="flex-1">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">
            30-Second Takeaway
          </h2>
          <p className="text-gray-700 leading-relaxed text-base">
            {summary}
          </p>
        </div>
      </div>
    </div>
  )
}

ExecutiveSummary.propTypes = {
  summary: PropTypes.string,
  isLoading: PropTypes.bool,
  error: PropTypes.string
}

export default ExecutiveSummary

