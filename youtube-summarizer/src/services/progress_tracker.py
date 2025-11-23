"""
Progress Tracker - Real-time progress tracking for video processing

Tracks processing stages and provides progress updates for WebSocket communication.
"""

import logging
import time
from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


class ProcessingStage(Enum):
    """Stages of video processing."""
    QUEUED = "queued"
    EXTRACTING_TRANSCRIPT = "extracting_transcript"
    GENERATING_SUMMARY = "generating_summary"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class ProgressUpdate:
    """Data class for progress updates."""
    video_id: str
    stage: str
    progress_percent: int
    message: str
    timestamp: str
    estimated_time_remaining: Optional[int] = None
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class ProgressTracker:
    """
    Tracks progress of video processing operations.
    
    Maintains state for each video being processed and provides
    progress updates for real-time UI updates.
    """
    
    def __init__(self):
        """Initialize progress tracker."""
        self.progress_data: Dict[str, Dict[str, Any]] = {}
    
    def start_processing(self, video_id: str) -> None:
        """
        Mark a video as starting processing.
        
        Args:
            video_id: YouTube video ID
        """
        self.progress_data[video_id] = {
            'stage': ProcessingStage.QUEUED.value,
            'progress_percent': 0,
            'start_time': time.time(),
            'stage_start_time': time.time(),
            'message': 'Processing queued...'
        }
        logger.info(f"Started tracking progress for video {video_id}")
    
    def update_stage(
        self,
        video_id: str,
        stage: ProcessingStage,
        message: str,
        progress_percent: int = None
    ) -> ProgressUpdate:
        """
        Update processing stage for a video.
        
        Args:
            video_id: YouTube video ID
            stage: Current processing stage
            message: Human-readable status message
            progress_percent: Progress percentage (0-100)
            
        Returns:
            ProgressUpdate: Current progress state
        """
        if video_id not in self.progress_data:
            self.start_processing(video_id)
        
        data = self.progress_data[video_id]
        data['stage'] = stage.value
        data['message'] = message
        data['stage_start_time'] = time.time()
        
        # Calculate progress percentage based on stage
        if progress_percent is not None:
            data['progress_percent'] = progress_percent
        else:
            stage_progress = {
                ProcessingStage.QUEUED: 10,
                ProcessingStage.EXTRACTING_TRANSCRIPT: 40,
                ProcessingStage.GENERATING_SUMMARY: 80,
                ProcessingStage.COMPLETED: 100,
                ProcessingStage.FAILED: 0
            }
            data['progress_percent'] = stage_progress.get(stage, 0)
        
        logger.info(f"Updated {video_id} to stage {stage.value}: {message}")
        
        return self._create_progress_update(video_id)
    
    def complete_processing(self, video_id: str) -> ProgressUpdate:
        """
        Mark processing as completed.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            ProgressUpdate: Final progress state
        """
        return self.update_stage(
            video_id,
            ProcessingStage.COMPLETED,
            "Processing completed successfully",
            100
        )
    
    def fail_processing(self, video_id: str, error: str) -> ProgressUpdate:
        """
        Mark processing as failed.
        
        Args:
            video_id: YouTube video ID
            error: Error message
            
        Returns:
            ProgressUpdate: Final progress state with error
        """
        if video_id not in self.progress_data:
            self.start_processing(video_id)
        
        data = self.progress_data[video_id]
        data['stage'] = ProcessingStage.FAILED.value
        data['message'] = f"Processing failed: {error}"
        data['error'] = error
        data['progress_percent'] = 0
        
        logger.error(f"Processing failed for {video_id}: {error}")
        
        return self._create_progress_update(video_id)
    
    def get_progress(self, video_id: str) -> Optional[ProgressUpdate]:
        """
        Get current progress for a video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            ProgressUpdate: Current progress state or None if not found
        """
        if video_id not in self.progress_data:
            return None
        
        return self._create_progress_update(video_id)
    
    def _create_progress_update(self, video_id: str) -> ProgressUpdate:
        """
        Create a ProgressUpdate object from stored data.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            ProgressUpdate: Progress update object
        """
        data = self.progress_data[video_id]
        
        # Calculate estimated time remaining
        elapsed = time.time() - data['start_time']
        progress = data['progress_percent']
        
        estimated_remaining = None
        if progress > 0 and progress < 100:
            total_estimated = (elapsed / progress) * 100
            estimated_remaining = int(total_estimated - elapsed)
        
        return ProgressUpdate(
            video_id=video_id,
            stage=data['stage'],
            progress_percent=data['progress_percent'],
            message=data['message'],
            timestamp=datetime.now().isoformat(),
            estimated_time_remaining=estimated_remaining,
            error=data.get('error')
        )
    
    def cleanup(self, video_id: str) -> None:
        """
        Clean up progress data for a video.
        
        Args:
            video_id: YouTube video ID
        """
        if video_id in self.progress_data:
            del self.progress_data[video_id]
            logger.info(f"Cleaned up progress data for {video_id}")


# Global progress tracker instance
progress_tracker = ProgressTracker()

