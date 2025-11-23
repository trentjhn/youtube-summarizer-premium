import React, { useEffect, useState } from 'react';
import io from 'socket.io-client';

/**
 * ProgressIndicator Component
 * 
 * Displays real-time progress updates for video processing.
 * Connects to WebSocket server to receive progress updates.
 */
export const ProgressIndicator = ({ videoId, onComplete, onError }) => {
  const [progress, setProgress] = useState({
    stage: 'queued',
    progress_percent: 0,
    message: 'Waiting to start processing...',
    estimated_time_remaining: null
  });
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (!videoId) return;

    // Connect to WebSocket server
    const newSocket = io(window.location.origin, {
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5
    });

    newSocket.on('connect', () => {
      console.log('Connected to progress tracker');
      setIsConnected(true);
      
      // Subscribe to progress updates for this video
      newSocket.emit('subscribe_progress', { video_id: videoId });
    });

    newSocket.on('progress_update', (data) => {
      console.log('Progress update:', data);
      setProgress(data);
      
      // Call onComplete callback when processing is done
      if (data.stage === 'completed' && onComplete) {
        onComplete(data);
      }
    });

    newSocket.on('error', (data) => {
      console.error('Processing error:', data);
      if (onError) {
        onError(data.message);
      }
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from progress tracker');
      setIsConnected(false);
    });

    setSocket(newSocket);

    // Cleanup on unmount
    return () => {
      if (newSocket) {
        newSocket.emit('unsubscribe_progress', { video_id: videoId });
        newSocket.disconnect();
      }
    };
  }, [videoId, onComplete, onError]);

  const getStageLabel = (stage) => {
    const labels = {
      'queued': 'Queued',
      'extracting_transcript': 'Extracting Transcript',
      'generating_summary': 'Generating Summary',
      'completed': 'Completed',
      'failed': 'Failed'
    };
    return labels[stage] || stage;
  };

  const formatTimeRemaining = (seconds) => {
    if (!seconds) return '';
    if (seconds < 60) return `${seconds}s remaining`;
    const minutes = Math.ceil(seconds / 60);
    return `${minutes}m remaining`;
  };

  return (
    <div className="w-full max-w-2xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      <div className="mb-6">
        <div className="flex justify-between items-center mb-2">
          <h3 className="text-lg font-semibold text-gray-800">
            {getStageLabel(progress.stage)}
          </h3>
          <span className="text-sm text-gray-600">
            {progress.progress_percent}%
          </span>
        </div>
        
        {/* Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
          <div
            className={`h-full transition-all duration-300 ${
              progress.stage === 'failed'
                ? 'bg-red-500'
                : progress.stage === 'completed'
                ? 'bg-green-500'
                : 'bg-blue-500'
            }`}
            style={{ width: `${progress.progress_percent}%` }}
          />
        </div>
      </div>

      {/* Status Message */}
      <div className="mb-4">
        <p className="text-gray-700 text-sm">
          {progress.message}
        </p>
        {progress.estimated_time_remaining && progress.progress_percent < 100 && (
          <p className="text-gray-500 text-xs mt-1">
            {formatTimeRemaining(progress.estimated_time_remaining)}
          </p>
        )}
      </div>

      {/* Error Message */}
      {progress.error && (
        <div className="bg-red-50 border border-red-200 rounded p-3 mb-4">
          <p className="text-red-700 text-sm">
            <strong>Error:</strong> {progress.error}
          </p>
        </div>
      )}

      {/* Connection Status */}
      <div className="flex items-center text-xs text-gray-500">
        <span
          className={`inline-block w-2 h-2 rounded-full mr-2 ${
            isConnected ? 'bg-green-500' : 'bg-gray-400'
          }`}
        />
        {isConnected ? 'Connected' : 'Connecting...'}
      </div>

      {/* Stage Indicators */}
      <div className="mt-6 flex justify-between text-xs">
        {['queued', 'extracting_transcript', 'generating_summary', 'completed'].map((stage) => (
          <div
            key={stage}
            className={`flex flex-col items-center ${
              ['queued', 'extracting_transcript', 'generating_summary', 'completed'].indexOf(stage) <=
              ['queued', 'extracting_transcript', 'generating_summary', 'completed'].indexOf(progress.stage)
                ? 'text-blue-600'
                : 'text-gray-400'
            }`}
          >
            <div
              className={`w-6 h-6 rounded-full flex items-center justify-center mb-1 ${
                ['queued', 'extracting_transcript', 'generating_summary', 'completed'].indexOf(stage) <
                ['queued', 'extracting_transcript', 'generating_summary', 'completed'].indexOf(progress.stage)
                  ? 'bg-green-500 text-white'
                  : ['queued', 'extracting_transcript', 'generating_summary', 'completed'].indexOf(stage) ===
                    ['queued', 'extracting_transcript', 'generating_summary', 'completed'].indexOf(progress.stage)
                  ? 'bg-blue-500 text-white'
                  : 'bg-gray-200'
              }`}
            >
              {['queued', 'extracting_transcript', 'generating_summary', 'completed'].indexOf(stage) <
              ['queued', 'extracting_transcript', 'generating_summary', 'completed'].indexOf(progress.stage)
                ? '✓'
                : ['queued', 'extracting_transcript', 'generating_summary', 'completed'].indexOf(stage) + 1}
            </div>
            <span className="text-center">{getStageLabel(stage)}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProgressIndicator;

