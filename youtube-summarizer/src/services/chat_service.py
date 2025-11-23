"""
Chat Service - Context-aware AI chat for video summaries

This module provides AI-powered chat functionality that allows users to ask
questions about video content. The chat is context-aware, using the video's
summary and transcript to provide relevant, accurate responses.
"""

import os
import json
import logging
from typing import List, Dict, Optional
import requests

# Configure logging
logger = logging.getLogger(__name__)

# Maximum conversation history to maintain (to avoid token limits)
MAX_HISTORY_MESSAGES = 10

# Maximum user message length (safety guardrail)
MAX_MESSAGE_LENGTH = 500


class ChatService:
    """
    Context-aware AI chat service for video content.
    
    Provides intelligent chat responses based on video summaries and transcripts,
    with conversation history management and safety guardrails.
    """
    
    def __init__(self):
        """Initialize chat service."""
        self.api_key = os.environ.get('OPENAI_API_KEY')
        if not self.api_key:
            logger.error("OPENAI_API_KEY environment variable not set")
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        logger.info("ChatService initialized")
    
    def chat(
        self,
        message: str,
        video_title: str,
        summary: Dict,
        transcript: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Generate AI chat response based on video context.
        
        Args:
            message: User's question/message
            video_title: Title of the video
            summary: Structured JSON summary of the video
            transcript: Full video transcript
            conversation_history: Previous messages in conversation (optional)
        
        Returns:
            dict: Response with 'response' (AI message) and 'error' (if any)
        
        Raises:
            ValueError: If message is empty or too long
        """
        # Input validation
        if not message or not message.strip():
            raise ValueError("Message cannot be empty")
        
        if len(message) > MAX_MESSAGE_LENGTH:
            raise ValueError(f"Message too long (max {MAX_MESSAGE_LENGTH} characters)")
        
        # Sanitize message (basic XSS prevention)
        message = message.strip()
        
        try:
            # Build context from video content
            context = self._build_context(video_title, summary, transcript)
            
            # Build conversation messages
            messages = self._build_messages(context, message, conversation_history)
            
            # Call OpenAI API
            response = self._call_openai(messages)
            
            logger.info(f"Generated chat response for video: {video_title}")
            return {
                "response": response,
                "error": None
            }
        
        except ValueError as e:
            # Re-raise validation errors
            raise
        
        except Exception as e:
            logger.error(f"Chat generation failed: {e}", exc_info=True)
            return {
                "response": "I apologize, but I'm having trouble processing your question right now. Please try again.",
                "error": str(e)
            }
    
    def _build_context(self, video_title: str, summary: Dict, transcript: str) -> str:
        """
        Build context string from video content.
        
        Args:
            video_title: Title of the video
            summary: Structured JSON summary
            transcript: Full transcript
        
        Returns:
            str: Formatted context for AI
        """
        context_parts = [f"Video Title: {video_title}\n"]
        
        # Add quick takeaway
        if summary.get('quick_takeaway'):
            context_parts.append(f"Quick Takeaway: {summary['quick_takeaway']}\n")
        
        # Add key points
        if summary.get('key_points'):
            context_parts.append("Key Points:")
            for i, point in enumerate(summary['key_points'], 1):
                context_parts.append(f"{i}. {point}")
            context_parts.append("")
        
        # Add topics
        if summary.get('topics'):
            context_parts.append("Main Topics:")
            for topic in summary['topics']:
                context_parts.append(f"- {topic.get('topic_name', '')}")
            context_parts.append("")
        
        # Add full summary paragraphs
        if summary.get('full_summary'):
            context_parts.append("Detailed Summary:")
            for para in summary['full_summary']:
                context_parts.append(para.get('content', ''))
            context_parts.append("")
        
        # Add transcript (truncated to avoid token limits)
        max_transcript_length = 5000
        if transcript:
            truncated_transcript = transcript[:max_transcript_length]
            if len(transcript) > max_transcript_length:
                truncated_transcript += "... [transcript truncated]"
            context_parts.append(f"Transcript:\n{truncated_transcript}")
        
        return "\n".join(context_parts)
    
    def _build_messages(
        self,
        context: str,
        user_message: str,
        conversation_history: Optional[List[Dict]] = None
    ) -> List[Dict]:
        """
        Build message array for OpenAI API.
        
        Args:
            context: Video context string
            user_message: Current user message
            conversation_history: Previous messages
        
        Returns:
            list: Array of message dicts for OpenAI API
        """
        # System message with context
        system_message = {
            "role": "system",
            "content": f"""You are a helpful AI assistant that answers questions about a YouTube video.
You have access to the video's title, summary, and transcript.

Use this information to provide accurate, helpful answers to user questions.
If the user asks about something not covered in the video, politely let them know.
Keep your responses concise but informative.

VIDEO CONTEXT:
{context}
"""
        }
        
        messages = [system_message]
        
        # Add conversation history (limited to avoid token limits)
        if conversation_history:
            # Take only the most recent messages
            recent_history = conversation_history[-MAX_HISTORY_MESSAGES:]
            messages.extend(recent_history)
        
        # Add current user message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        return messages
    
    def _call_openai(self, messages: List[Dict]) -> str:
        """
        Call OpenAI API to generate response.
        
        Args:
            messages: Array of message dicts
        
        Returns:
            str: AI response text
        
        Raises:
            RuntimeError: If API call fails
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-4o-mini",
                "messages": messages,
                "temperature": 0.7,  # Slightly higher for conversational responses
                "max_tokens": 500    # Limit response length
            }
            
            logger.info(f"Sending chat request to OpenAI API")
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code != 200:
                error_msg = response.text
                logger.error(f"OpenAI API error: {response.status_code} - {error_msg}")
                raise RuntimeError(f"OpenAI API error: {response.status_code}")
            
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"].strip()
            
            logger.info(f"Generated chat response ({len(ai_response)} chars)")
            return ai_response
        
        except requests.exceptions.Timeout:
            logger.error("OpenAI API request timed out")
            raise RuntimeError("Request timed out. Please try again.")
        
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenAI API request failed: {e}")
            raise RuntimeError(f"API request failed: {e}")
        
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI API call: {e}")
            raise RuntimeError(f"Unexpected error: {e}")

