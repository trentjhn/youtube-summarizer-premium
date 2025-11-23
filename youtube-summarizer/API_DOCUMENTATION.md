# YouTube Summarizer API Documentation

**Version:** 2.0  
**Base URL:** `http://localhost:5001`  
**Last Updated:** November 21, 2025

---

## Table of Contents

1. [Authentication](#authentication)
2. [Endpoints](#endpoints)
   - [POST /api/process-video](#post-apiprocess-video)
   - [POST /api/chat](#post-apichat)
   - [GET /api/video/:video_id/structured](#get-apivideovideo_idstructured)
3. [Data Models](#data-models)
4. [Error Handling](#error-handling)
5. [Rate Limiting](#rate-limiting)
6. [Examples](#examples)

---

## Authentication

Currently, the API does not require authentication. This may change in future versions.

---

## Endpoints

### POST /api/process-video

Process a YouTube video URL and generate a comprehensive JSON-structured summary.

**Endpoint:** `/api/process-video`  
**Method:** `POST`  
**Content-Type:** `application/json`

#### Request Body

```json
{
  "video_url": "https://youtube.com/watch?v=VIDEO_ID"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `video_url` | string | Yes | Full YouTube video URL |

#### Response (Success - 200 OK)

```json
{
  "id": 1,
  "video_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
  "transcript": "Full transcript text...",
  "summary": {
    "quick_takeaway": "A love song about unwavering commitment and loyalty",
    "key_points": [
      "Emphasizes commitment in relationships",
      "Promises of loyalty and support",
      "Rejection of abandonment and betrayal"
    ],
    "topics": [
      {
        "title": "Commitment and Loyalty",
        "content": "The song emphasizes unwavering commitment...",
        "summary_section_id": 1
      }
    ],
    "timestamps": [
      {
        "time": "0:00",
        "description": "Opening verse about commitment"
      }
    ],
    "full_summary": [
      {
        "id": 1,
        "content": "Rick Astley's iconic 1987 hit 'Never Gonna Give You Up' is a powerful declaration..."
      }
    ]
  },
  "status": "completed",
  "created_at": "2025-11-21T12:00:00",
  "updated_at": "2025-11-21T12:05:00"
}
```

#### Response (Error - 400 Bad Request)

```json
{
  "error": "video_url is required"
}
```

#### Response (Error - 500 Internal Server Error)

```json
{
  "error": "Failed to extract transcript: Video unavailable"
}
```

---

### POST /api/chat

Chat with AI about a processed video using context-aware responses based on the video's summary and transcript.

**Endpoint:** `/api/chat`  
**Method:** `POST`  
**Content-Type:** `application/json`

#### Request Body

```json
{
  "video_id": "dQw4w9WgXcQ",
  "message": "What are the main themes of this song?",
  "conversation_history": [
    {
      "role": "user",
      "content": "What is this song about?"
    },
    {
      "role": "assistant",
      "content": "This is a love song about commitment and loyalty."
    }
  ]
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `video_id` | string | Yes | YouTube video ID |
| `message` | string | Yes | User's question (max 500 chars) |
| `conversation_history` | array | No | Previous messages (max 10) |

#### Response (Success - 200 OK)

```json
{
  "success": true,
  "response": "The main themes of 'Never Gonna Give You Up' include unwavering commitment, loyalty in relationships, and the promise to never abandon or betray a loved one. The song emphasizes emotional support and dedication through its repetitive chorus and heartfelt lyrics.",
  "video_id": "dQw4w9WgXcQ"
}
```

#### Response (Error - 400 Bad Request)

```json
{
  "success": false,
  "error": "video_id is required"
}
```

```json
{
  "success": false,
  "error": "message is required"
}
```

```json
{
  "success": false,
  "error": "Message too long (max 500 characters)"
}
```

```json
{
  "success": false,
  "error": "Video does not have a summary or transcript. Please process the video first."
}
```

#### Response (Error - 404 Not Found)

```json
{
  "success": false,
  "error": "Video not found: invalid_video_id"
}
```

#### Response (Error - 500 Internal Server Error)

```json
{
  "success": false,
  "error": "Failed to generate chat response. Please try again."
}
```

---

### GET /api/video/:video_id/structured

Retrieve structured data extracted from a video's summary (legacy endpoint for backward compatibility).

**Endpoint:** `/api/video/:video_id/structured`  
**Method:** `GET`

#### Response (Success - 200 OK)

```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "data_points": [
    {
      "type": "key_point",
      "content": "Emphasizes commitment in relationships"
    }
  ],
  "metrics": []
}
```

---

## Data Models

### Summary Object

The summary object returned by `/api/process-video` contains 5 structured components:

```typescript
interface Summary {
  quick_takeaway: string;        // One-sentence summary (max 150 chars)
  key_points: string[];          // 5-7 critical insights
  topics: Topic[];               // 3-5 main themes
  timestamps: Timestamp[];       // 3-5 key moments
  full_summary: Paragraph[];     // 5-8 detailed paragraphs
}

interface Topic {
  title: string;
  content: string;
  summary_section_id: number;    // For navigation
}

interface Timestamp {
  time: string;                  // Format: "MM:SS" or "HH:MM:SS"
  description: string;
}

interface Paragraph {
  id: number;                    // Unique identifier
  content: string;               // Narrative paragraph
}
```

### Conversation History

```typescript
interface Message {
  role: "user" | "assistant";
  content: string;
}
```

---

## Error Handling

All API endpoints follow consistent error response patterns:

### HTTP Status Codes

- `200 OK` - Request successful
- `400 Bad Request` - Invalid request parameters
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

### Error Response Format

```json
{
  "error": "Human-readable error message",
  "success": false  // Only for /api/chat endpoint
}
```

---

## Rate Limiting

### Chat Endpoint Limits

- **Message Length:** Max 500 characters per message
- **Conversation History:** Max 10 messages
- **Transcript Context:** Max 3000 characters
- **Response Tokens:** Max 500 tokens

### Processing Limits

- **Transcript Length:** Max 15,000 characters for summarization
- **Cache TTL:** 24 hours for summaries

---

## Examples

### Example 1: Process a Video and Chat

```bash
# Step 1: Process the video
curl -X POST http://localhost:5001/api/process-video \
  -H "Content-Type: application/json" \
  -d '{"video_url": "https://youtube.com/watch?v=dQw4w9WgXcQ"}'

# Step 2: Chat about the video
curl -X POST http://localhost:5001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "dQw4w9WgXcQ",
    "message": "What are the main themes?"
  }'
```

### Example 2: Multi-turn Conversation

```bash
# First question
curl -X POST http://localhost:5001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "dQw4w9WgXcQ",
    "message": "What is this song about?"
  }'

# Follow-up question with history
curl -X POST http://localhost:5001/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "dQw4w9WgXcQ",
    "message": "Can you elaborate on the first theme?",
    "conversation_history": [
      {"role": "user", "content": "What is this song about?"},
      {"role": "assistant", "content": "This is a love song about commitment..."}
    ]
  }'
```

---

## Notes

- All timestamps are in ISO 8601 format
- Video IDs are extracted from YouTube URLs automatically
- Summaries are cached for 24 hours
- The API uses OpenAI GPT-4o-mini for summarization and chat
- Backward compatibility is maintained for legacy text summaries

