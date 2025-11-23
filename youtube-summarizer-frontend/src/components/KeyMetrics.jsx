import React from 'react'
import PropTypes from 'prop-types'
import { TrendingUp, DollarSign, Calendar, Ruler, BarChart3, Hash } from 'lucide-react'

/**
 * KeyMetrics Component
 * 
 * Displays structured metrics extracted from the video summary.
 * Supports 6 metric types: percentage, currency, numeric, date, measurement, statistic
 * 
 * Props:
 *   - metrics (array): Array of metric objects with name, value, and type
 *   - isLoading (boolean): Whether data is being fetched
 *   - error (string): Error message if extraction failed
 */
export const KeyMetrics = ({ metrics = [], isLoading = false, error = null }) => {
  const getMetricIcon = (type) => {
    const iconProps = { className: 'h-5 w-5' }
    switch (type) {
      case 'percentage':
        return <TrendingUp {...iconProps} />
      case 'currency':
        return <DollarSign {...iconProps} />
      case 'date':
        return <Calendar {...iconProps} />
      case 'measurement':
        return <Ruler {...iconProps} />
      case 'statistic':
        return <BarChart3 {...iconProps} />
      case 'numeric':
      default:
        return <Hash {...iconProps} />
    }
  }

  const getMetricColor = (type) => {
    switch (type) {
      case 'percentage':
        return 'bg-blue-50 border-blue-200 text-blue-700'
      case 'currency':
        return 'bg-green-50 border-green-200 text-green-700'
      case 'date':
        return 'bg-purple-50 border-purple-200 text-purple-700'
      case 'measurement':
        return 'bg-orange-50 border-orange-200 text-orange-700'
      case 'statistic':
        return 'bg-pink-50 border-pink-200 text-pink-700'
      case 'numeric':
      default:
        return 'bg-gray-50 border-gray-200 text-gray-700'
    }
  }

  const getMetricBadgeColor = (type) => {
    switch (type) {
      case 'percentage':
        return 'bg-blue-100 text-blue-800'
      case 'currency':
        return 'bg-green-100 text-green-800'
      case 'date':
        return 'bg-purple-100 text-purple-800'
      case 'measurement':
        return 'bg-orange-100 text-orange-800'
      case 'statistic':
        return 'bg-pink-100 text-pink-800'
      case 'numeric':
      default:
        return 'bg-gray-100 text-gray-800'
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
            <h3 className="text-sm font-medium text-red-800">Failed to load metrics</h3>
            <p className="mt-1 text-sm text-red-700">{error}</p>
          </div>
        </div>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg p-6 border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Key Metrics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-24 bg-gray-200 rounded animate-pulse"></div>
          ))}
        </div>
      </div>
    )
  }

  if (!metrics || metrics.length === 0) {
    return (
      <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Key Metrics</h2>
        <p className="text-gray-500 text-sm">No metrics found in the video summary</p>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg p-6 border border-gray-200 shadow-sm">
      <h2 className="text-lg font-semibold text-gray-900 mb-4">Key Metrics</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {metrics.map((metric, index) => (
          <div
            key={index}
            className={`rounded-lg p-4 border-2 transition-all hover:shadow-md ${getMetricColor(metric.type)}`}
            role="article"
            aria-label={`Metric: ${metric.name} is ${metric.value}`}
          >
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center flex-1">
                <div className="text-gray-600 mr-2">
                  {getMetricIcon(metric.type)}
                </div>
                <h3 className="text-sm font-medium text-gray-900 truncate">
                  {metric.name}
                </h3>
              </div>
              <span className={`ml-2 px-2 py-1 rounded text-xs font-medium whitespace-nowrap ${getMetricBadgeColor(metric.type)}`}>
                {metric.type}
              </span>
            </div>
            <p className="text-2xl font-bold text-gray-900 break-words">
              {metric.value}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}

KeyMetrics.propTypes = {
  metrics: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string.isRequired,
      value: PropTypes.string.isRequired,
      type: PropTypes.oneOf(['percentage', 'currency', 'numeric', 'date', 'measurement', 'statistic']).isRequired
    })
  ),
  isLoading: PropTypes.bool,
  error: PropTypes.string
}

export default KeyMetrics

