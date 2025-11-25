# Analysis: Long Video Support & Summary Quality Issues

## Current Limitations

### 1. Long Video Support (30min-1hr)

**Token Limits:**
- GPT-4o-mini input limit: 128,000 tokens (~96,000 words)
- A 1-hour video transcript: ~9,000-12,000 words (~12,000-16,000 tokens)
- **Current system CAN handle 1-hour videos** from a token perspective

**Real Issue:**
The problem isn't capacity, it's **quality degradation** with long transcripts:
- AI tries to compress too much information
- Loses important details
- Becomes generic and vague
- Context gets muddled

**Solution Approach:**
1. **Chunking strategy** for very long videos (>45 min)
2. **Hierarchical summarization** (summarize chunks, then summarize summaries)
3. **Adaptive token allocation** based on video length

### 2. Summary Quality Issues

**Problem 1: Verbosity**
- Current prompt doesn't emphasize conciseness
- AI defaults to academic/formal writing style
- Too many filler words and qualifiers

**Problem 2: Context Loss**
- When speaker quotes someone, AI attributes the quote to the speaker
- External references lose their connection to the main argument
- Complex arguments get oversimplified

**Problem 3: Over-Sanitization**
- AI is being "safe" and filtering controversial content
- Softens strong language or direct statements
- Misses the speaker's actual tone and intent
- Loses the "edge" or "punch" of the original message

## Root Cause Analysis

### Why Current Prompt Fails

**Current Prompt Issues:**
1. **Too generic** - Doesn't specify tone or style
2. **No examples** - AI doesn't know what "good" looks like
3. **No context preservation instructions** - Doesn't tell AI to maintain attribution
4. **Implicit safety bias** - AI defaults to "safe" interpretations
5. **No length guidance** - Doesn't specify conciseness requirements

### What We Need

**For Long Videos:**
- Intelligent chunking for 45+ minute videos
- Hierarchical summarization
- Better context preservation across chunks

**For Quality:**
- **Concise, direct language** - No fluff
- **Faithful representation** - Capture actual message, not sanitized version
- **Context preservation** - Maintain attribution and argument structure
- **Tone matching** - Reflect speaker's actual tone (direct, provocative, etc.)

## Solution Strategy

### Approach 1: Enhanced Prompt Engineering (Immediate)

**Changes:**
1. Add explicit instructions for conciseness
2. Add context preservation rules
3. Add "faithful representation" directive
4. Add tone matching instructions
5. Provide examples of good vs. bad summaries

**Impact:** High quality improvement, no architectural changes

### Approach 2: Adaptive Summarization (For Long Videos)

**For videos >45 minutes:**
1. Split transcript into logical chunks (10-15 min each)
2. Summarize each chunk individually
3. Create a "meta-summary" from chunk summaries
4. Generate final structured output

**Impact:** Better quality for long videos, moderate complexity

### Approach 3: Model Upgrade (Optional)

**Current:** GPT-4o-mini  
**Upgrade to:** GPT-4o or Gemini 2.5 Flash

**Benefits:**
- Better context understanding
- More nuanced summarization
- Better at following complex instructions

**Cost Impact:**
- GPT-4o-mini: $0.150/1M input tokens, $0.600/1M output tokens
- GPT-4o: $2.50/1M input tokens, $10.00/1M output tokens
- Gemini 2.5 Flash: Similar to GPT-4o-mini pricing

**Recommendation:** Start with prompt engineering, upgrade model if needed

## Recommended Implementation Plan

### Phase 1: Immediate Improvements (Prompt Engineering)

**Update the prompt to:**
1. **Emphasize conciseness** - "Be direct and concise. No filler words."
2. **Preserve context** - "When the speaker quotes someone, clearly attribute it."
3. **Faithful representation** - "Capture the speaker's actual message, including strong language or controversial points."
4. **Tone matching** - "Match the speaker's tone (direct, provocative, academic, etc.)"

### Phase 2: Long Video Support (Adaptive Chunking)

**For videos >45 minutes:**
1. Detect video length from transcript word count
2. If >45 min, use chunking strategy
3. Otherwise, use standard single-pass summarization

### Phase 3: Testing & Iteration

**Test with:**
- 10-minute video (baseline)
- 30-minute video (moderate length)
- 60-minute video (long form)
- Controversial/direct content (test sanitization)
- Complex argument with quotes (test context preservation)

## Technical Considerations

### Token Management

**Current allocation:**
- Input: ~12,000 tokens (1-hour video)
- Output: 4,000 tokens (~3,000 words)
- Total: ~16,000 tokens per summary

**For chunking approach:**
- Chunk 1: 3,000 input + 1,000 output = 4,000 tokens
- Chunk 2: 3,000 input + 1,000 output = 4,000 tokens
- Chunk 3: 3,000 input + 1,000 output = 4,000 tokens
- Meta-summary: 3,000 input + 4,000 output = 7,000 tokens
- **Total: ~19,000 tokens** (slightly more, but better quality)

### Cost Analysis

**Current (single-pass):**
- 1-hour video: ~$0.015 per summary

**Chunking approach:**
- 1-hour video: ~$0.025 per summary

**Difference:** +$0.01 per video (67% increase, but still very cheap)

## Next Steps

1. **Create improved prompt** with all quality enhancements
2. **Implement adaptive chunking** for long videos
3. **Test thoroughly** with diverse content
4. **Iterate based on results**
