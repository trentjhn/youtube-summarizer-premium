/**
 * YouTube Video Summarizer - Main App Component
 * 
 * This is the core MVP interface that provides a simple, clean workflow:
 * 1. User pastes YouTube URL into input field
 * 2. System processes video and generates comprehensive summary
 * 3. Summary is displayed in a visually pleasing, readable format
 */

import React, { useState } from 'react'
import { AlertCircle, Youtube, Loader2, CheckCircle, Copy } from 'lucide-react'
import StructuredDataDisplay from './components/StructuredDataDisplay'
import SummaryView from './components/SummaryView/SummaryView'
import ModeSelector from './components/ModeSelector'
import './App.css'

// Feature flag to toggle between old and new UI
const USE_PREMIUM_UI = true;

function App() {
  // Component state for managing the video processing workflow
  const [videoUrl, setVideoUrl] = useState('')           // User input URL
  const [mode, setMode] = useState('quick')              // Summarization mode (quick/indepth)
  const [isProcessing, setIsProcessing] = useState(false) // Loading state
  const [result, setResult] = useState(null)             // Processed video data
  const [error, setError] = useState(null)               // Error messages
  const [copied, setCopied] = useState(false)            // Copy feedback

  /**
   * Handle form submission and video processing
   */
  const handleSubmit = async (e) => {
    e.preventDefault()
    
    // Reset previous state
    setError(null)
    setResult(null)
    setCopied(false)
    
    // Validate URL input
    if (!videoUrl.trim()) {
      setError('Please enter a YouTube video URL')
      return
    }
    
    // Basic YouTube URL validation
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)/
    if (!youtubeRegex.test(videoUrl)) {
      setError('Please enter a valid YouTube URL')
      return
    }
    
    setIsProcessing(true)

    try {
      // Call backend API to process the video with selected mode
      const response = await fetch('/api/process-video', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          video_url: videoUrl.trim(),
          mode: mode  // Pass the selected mode (quick/indepth)
        })
      })
      
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to process video')
      }
      
      // Success: display the results
      setResult(data)
      
    } catch (err) {
      // Handle errors gracefully
      setError(err.message || 'An unexpected error occurred')
    } finally {
      setIsProcessing(false)
    }
  }
  
  /**
   * Copy summary to clipboard
   */
  const copyToClipboard = async () => {
    if (result?.summary) {
      try {
        await navigator.clipboard.writeText(result.summary)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      } catch (err) {
        console.error('Failed to copy to clipboard:', err)
      }
    }
  }
  
  /**
   * Reset form to initial state
   */
  const resetForm = () => {
    setVideoUrl('')
    setResult(null)
    setError(null)
    setCopied(false)
  }

  /**
   * Check if summary is in new JSON format
   */
  const isJSONSummary = (summary) => {
    return summary && typeof summary === 'object' && 'quick_takeaway' in summary;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header Section */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center mb-6">
            <Youtube className="h-12 w-12 text-red-600 mr-4" />
            <h1 className="text-4xl font-bold text-gray-900">
              YouTube Video Summarizer
            </h1>
          </div>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Transform lengthy YouTube videos into comprehensive, readable summaries. 
            Paste any YouTube URL below to get started.
          </p>
        </div>

        {/* Main Content Area */}
        <div className="max-w-4xl mx-auto">
          
          {/* URL Input Form */}
          <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="videoUrl" className="block text-lg font-medium text-gray-700 mb-3">
                  YouTube Video URL
                </label>
                <div className="relative">
                  <input
                    type="url"
                    id="videoUrl"
                    value={videoUrl}
                    onChange={(e) => setVideoUrl(e.target.value)}
                    placeholder="https://youtube.com/watch?v=..."
                    className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-lg"
                    disabled={isProcessing}
                  />
                  <Youtube className="absolute right-3 top-3 h-6 w-6 text-gray-400" />
                </div>
              </div>

              {/* Mode Selector */}
              <ModeSelector
                selectedMode={mode}
                onSelectMode={setMode}
              />

              <button
                type="submit"
                disabled={isProcessing || !videoUrl.trim()}
                className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200 flex items-center justify-center text-lg"
              >
                {isProcessing ? (
                  <>
                    <Loader2 className="animate-spin h-5 w-5 mr-2" />
                    Processing Video ({mode === 'quick' ? 'Quick' : 'In-Depth'})...
                  </>
                ) : (
                  'Generate Summary'
                )}
              </button>
            </form>
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-xl p-6 mb-8">
              <div className="flex items-center">
                <AlertCircle className="h-6 w-6 text-red-600 mr-3" />
                <div>
                  <h3 className="text-lg font-medium text-red-800">Error</h3>
                  <p className="text-red-700 mt-1">{error}</p>
                </div>
              </div>
            </div>
          )}

          {/* Processing Status */}
          {isProcessing && (
            <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 mb-8">
              <div className="flex items-center">
                <Loader2 className="animate-spin h-6 w-6 text-blue-600 mr-3" />
                <div>
                  <h3 className="text-lg font-medium text-blue-800">Processing Video</h3>
                  <p className="text-blue-700 mt-1">
                    Extracting transcript and generating comprehensive summary...
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Results Display */}
          {result && (
            <>
              {/* Check if we should use the new Premium UI */}
              {USE_PREMIUM_UI && isJSONSummary(result.summary) ? (
                // New Premium UI - Three-Pane Interactive Digest
                <SummaryView videoData={result} />
              ) : (
                // Old UI - Simple Summary Display (Fallback)
                <div className="space-y-8">
                  {/* Result Header */}
                  <div className="bg-white rounded-xl shadow-lg overflow-hidden">
                    <div className="bg-green-50 border-b border-green-200 p-6">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center">
                          <CheckCircle className="h-6 w-6 text-green-600 mr-3" />
                          <div>
                            <h3 className="text-lg font-medium text-green-800">
                              Summary Generated Successfully
                            </h3>
                            <p className="text-green-700 mt-1">
                              Video: {result.title}
                            </p>
                          </div>
                        </div>
                        <div className="flex space-x-3">
                          <button
                            onClick={copyToClipboard}
                            className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors duration-200"
                          >
                            <Copy className="h-4 w-4 mr-2" />
                            {copied ? 'Copied!' : 'Copy Summary'}
                          </button>
                          <button
                            onClick={resetForm}
                            className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors duration-200"
                          >
                            Process Another Video
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* Video Metadata */}
                    <div className="bg-gray-50 border-t border-gray-200 p-6">
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm text-gray-600">
                        <div>
                          <span className="font-medium">Video ID:</span> {result.video_id}
                        </div>
                        <div>
                          <span className="font-medium">Processed:</span> {new Date(result.created_at).toLocaleString()}
                        </div>
                        <div>
                          <span className="font-medium">Status:</span>
                          <span className="ml-1 px-2 py-1 bg-green-100 text-green-800 rounded text-xs">
                            {result.status}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Structured Data Display */}
                  <StructuredDataDisplay videoId={result.video_id} title={result.title} />

                  {/* Full Summary Content */}
                  <div className="bg-white rounded-xl shadow-lg p-8">
                    <h2 className="text-2xl font-bold text-gray-900 mb-6">Full Summary</h2>
                    <div
                      className="prose prose-lg max-w-none"
                      dangerouslySetInnerHTML={{
                        __html: typeof result.summary === 'string'
                          ? result.summary
                              // Convert markdown to basic HTML for display
                              .replace(/^# (.*$)/gm, '<h1 class="text-3xl font-bold text-gray-900 mb-6">$1</h1>')
                              .replace(/^## (.*$)/gm, '<h2 class="text-2xl font-semibold text-gray-800 mt-8 mb-4">$1</h2>')
                              .replace(/^### (.*$)/gm, '<h3 class="text-xl font-medium text-gray-700 mt-6 mb-3">$1</h3>')
                              .replace(/^\*\*(.*?)\*\*/gm, '<strong class="font-semibold text-gray-900">$1</strong>')
                              .replace(/^\* (.*$)/gm, '<li class="ml-4 mb-2">$1</li>')
                              .replace(/\n\n/g, '</p><p class="mb-4">')
                              .replace(/^([^<].*$)/gm, '<p class="mb-4 text-gray-700 leading-relaxed">$1</p>')
                          : JSON.stringify(result.summary, null, 2)
                      }}
                    />
                  </div>
                </div>
              )}
            </>
          )}
        </div>

        {/* Footer */}
        <div className="text-center mt-16 text-gray-500">
          <p>
            Powered by AI • Built for comprehensive video analysis
          </p>
        </div>
      </div>
    </div>
  )
}

export default App
