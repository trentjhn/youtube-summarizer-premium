"""
Services Package - Business Logic Layer

This package contains the core business logic services for the YouTube Video Summarizer.
Each service is responsible for a specific domain of functionality:

- cache_manager: Redis-based caching for performance optimization
- transcript_extractor: YouTube transcript extraction with fallback methods  
- ai_summarizer: LangChain-based AI summarization using OpenAI GPT models
- vector_store: Pinecone integration for semantic search (future feature)
- graph_store: Neo4j integration for concept relationships (future feature)

Services follow dependency injection patterns for testability and modularity.
"""

