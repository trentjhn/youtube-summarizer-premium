# YouTube Video Summarizer

A comprehensive AI-powered application that transforms lengthy YouTube videos into detailed, readable summaries. Built with Flask, React, and **Google Gemini 2.5 Flash-Lite**, this MVP focuses on providing a simple yet powerful interface for extracting valuable insights from video content.

## Features

**Core MVP Functionality:**
- Simple URL input interface for YouTube videos
- Automatic transcript extraction with multiple fallback methods
- AI-powered comprehensive summarization using **Google Gemini 2.5 Flash-Lite**
- 1M token context window - handles videos up to ~12 hours without chunking
- Visually pleasing summary display with markdown formatting
- Real-time processing status and error handling

**Technical Highlights:**
- Redis caching for performance optimization
- Multi-layer fallback transcript extraction
- Comprehensive error handling and logging
- Responsive React frontend with Tailwind CSS
- Docker containerization for easy deployment
- Comprehensive test suite

## AI Model Information

**Current Model: Google Gemini 2.5 Flash-Lite** (as of February 2026)

| Feature | Value |
|---------|-------|
| Input Cost | $0.10 per 1M tokens |
| Output Cost | $0.40 per 1M tokens |
| Context Window | 1,000,000 tokens |
| Max Video Length | ~12.5 hours (single pass) |
| Quality Benchmark | MMMU 72.9% |

**Why Gemini 2.5 Flash-Lite?**
- **33% cheaper** than GPT-4o-mini ($0.10/$0.40 vs $0.15/$0.60)
- **8x larger context** window (1M vs 128K tokens)
- **Better quality** benchmarks (MMMU 72.9% vs 59.4%)
- **No chunking required** for 99%+ of YouTube videos

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Redis (optional, for caching)
- **Google AI API key** (get one at https://makersuite.google.com/app/apikey)

### Installation

1. **Clone and setup backend:**
```bash
cd youtube-summarizer
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Setup frontend:**
```bash
cd ../youtube-summarizer-frontend
npm install -g pnpm
pnpm install
```

3. **Environment configuration:**
```bash
# Set your Google AI API key (get from https://makersuite.google.com/app/apikey)
export GOOGLE_AI_API_KEY="your-api-key-here"

# Alternative: GEMINI_API_KEY is also supported
# export GEMINI_API_KEY="your-api-key-here"
```

4. **Start services:**
```bash
# Terminal 1: Backend
cd youtube-summarizer
source venv/bin/activate
python src/main.py

# Terminal 2: Frontend (development)
cd youtube-summarizer-frontend
pnpm run dev
```

5. **Access the application:**
   - Open http://localhost:5173 for the React frontend (may use 5174 if 5173 is in use)
   - Backend API runs on http://localhost:5000

## Usage

1. **Process a video:**
   - Paste any YouTube URL into the input field
   - Click "Generate Summary"
   - Wait for processing (transcript extraction + AI summarization)
   - View the comprehensive summary with copy/share options

2. **API usage:**
```bash
curl -X POST http://localhost:5000/api/process-video \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://youtube.com/watch?v=VIDEO_ID"}'
```

## Architecture

The application follows a clean, modular architecture designed for scalability:

**Backend (Flask):**
- `src/models/video.py` - Database models for video data
- `src/services/` - Business logic services (caching, transcript extraction, AI summarization)
- `src/routes/video.py` - API endpoints for video processing

**Frontend (React):**
- Clean, responsive interface built with Tailwind CSS
- Real-time status updates and error handling
- Markdown-to-HTML conversion for rich summary display

**Services Integration:**
- Redis for multi-layer caching (transcripts, summaries)
- YouTube Transcript API for primary transcript extraction
- **Google Gemini 2.5 Flash-Lite** for comprehensive summarization (1M context window)
- Fallback methods for robust transcript extraction

## Development

### Running Tests

```bash
# Backend tests
cd youtube-summarizer
source venv/bin/activate
pytest tests/

# Frontend tests (if added)
cd youtube-summarizer-frontend
pnpm test
```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Production deployment
docker-compose -f docker-compose.yml up -d
```

## Configuration

### Environment Variables

- `GOOGLE_AI_API_KEY` - **Required** for AI summarization (get from https://makersuite.google.com/app/apikey)
- `GEMINI_API_KEY` - Alternative name for Google AI API key (supported for backward compatibility)
- `REDIS_HOST` - Redis server host (default: localhost)
- `REDIS_PORT` - Redis server port (default: 6379)
- `FLASK_ENV` - Flask environment (development/production)

### Caching Strategy

The application implements intelligent multi-layer caching:

- **Transcript Cache (1 hour TTL)** - Avoids repeated YouTube API calls
- **Summary Cache (24 hour TTL)** - Expensive AI operations cached longer
- **Content-based hashing** - Identical content produces identical cache keys

## API Documentation

### POST /api/process-video

Process a YouTube video URL and generate comprehensive summary.

**Request:**
```json
{
  "video_url": "https://youtube.com/watch?v=VIDEO_ID"
}
```

**Response:**
```json
{
  "id": 1,
  "video_id": "VIDEO_ID",
  "title": "Video Title",
  "url": "https://youtube.com/watch?v=VIDEO_ID",
  "transcript": "Full transcript text...",
  "summary": "# Video Title\n\n## Overview\n...",
  "status": "completed",
  "created_at": "2024-01-01T12:00:00",
  "updated_at": "2024-01-01T12:05:00"
}
```

## Future Enhancements

The current MVP provides a solid foundation for advanced features:

- **Batch Processing** - Process multiple videos simultaneously
- **User Accounts** - Personal video libraries and history
- **Advanced Analytics** - Video content insights and trends
- **Vector Search** - Semantic search across processed videos using Pinecone
- **Knowledge Graphs** - Content relationships using Neo4j
- **Custom Prompts** - User-defined summarization styles
- **Export Options** - PDF, Word, and other format exports

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For questions, issues, or feature requests, please open an issue on GitHub or contact the development team.

---

**Built with ❤️ for comprehensive video analysis**

