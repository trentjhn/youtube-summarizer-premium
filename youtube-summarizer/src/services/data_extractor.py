"""
Data Extractor - Structured data extraction from AI-generated summaries

This module extracts structured data from markdown-formatted AI summaries,
transforming them into professional-grade data suitable for UI components.

Works with ANY YouTube video genre: educational content, tech reviews,
tutorials, documentaries, interviews, entertainment, news, and more.

Extracts:
- Executive summary (30-second takeaway)
- Key metrics (numbers, percentages, dates, measurements, statistics)
- Key points (main arguments/insights)
- Action items (actionable takeaways)
- Timestamps (time-stamped key moments)

Design Principles:
- Graceful degradation: Return sensible defaults if extraction fails
- No exceptions: Log warnings instead of raising errors
- Type safety: Use type hints for all functions
- Performance: Compiled regex patterns for efficiency
- General-purpose: Works across all content types
"""

import re
import logging
from typing import Dict, List, Any

# Configure logging
logger = logging.getLogger(__name__)


class DataExtractor:
    """
    Extracts structured data from AI-generated summaries.

    Transforms markdown summaries into structured JSON with professional-grade
    data for UI components. Works with any YouTube video genre. Implements
    graceful degradation and comprehensive error handling.

    Example:
        >>> extractor = DataExtractor()
        >>> summary = "# Python Tutorial\\n\\nLearn Python in 40 hours..."
        >>> data = extractor.extract(summary)
        >>> print(data['key_metrics'])  # [{'name': 'hours', 'value': '40', ...}]
        >>> print(data['key_points'])  # ['Variables and data types', ...]
    """
    
    def __init__(self):
        """Initialize with compiled regex patterns for performance."""
        # General-purpose metric patterns
        self.percentage_pattern = re.compile(r'(\d+\.?\d*)\s*%')
        self.currency_pattern = re.compile(r'\$\s*(\d+\.?\d*)')
        self.numeric_pattern = re.compile(r'(\d+\.?\d*)\s*(million|billion|thousand|k|m|b)')
        self.date_pattern = re.compile(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})')
        self.measurement_pattern = re.compile(
            r'(\d+\.?\d*)\s*(km|miles|kg|lbs|hours|minutes|seconds|degrees|meters|feet|cm|inches)'
        )

        # Timestamp and structure patterns
        self.timestamp_pattern = re.compile(r'(\d{1,2}):(\d{2})(?::(\d{2}))?')
        self.bullet_pattern = re.compile(r'^[\s]*[-*]\s+(.+)$', re.MULTILINE)
        self.section_pattern = re.compile(r'^#+\s+(.+)$', re.MULTILINE)

        logger.info("DataExtractor initialized with compiled patterns")
    
    def extract(self, summary: str, title: str = "") -> Dict[str, Any]:
        """
        Extract structured data from any YouTube video summary.

        Works with all content types: educational, tutorials, tech reviews,
        documentaries, interviews, entertainment, news, and more.

        Args:
            summary: Markdown-formatted AI summary text
            title: Video title (optional, used for context)

        Returns:
            Dict containing extracted structured data with keys:
            - executive_summary: str (30-second takeaway)
            - key_metrics: List[Dict] (numbers, dates, measurements, statistics)
            - key_points: List[str] (main arguments/insights)
            - action_items: List[str] (actionable takeaways)
            - timestamps: List[Dict] (time-stamped key moments)
        """
        # Validate input
        if not summary or not isinstance(summary, str):
            logger.warning("Invalid summary input - returning defaults")
            return self._get_defaults()

        try:
            # Extract each component
            result = {
                "executive_summary": self._extract_executive_summary(summary),
                "key_metrics": self._extract_key_metrics(summary),
                "key_points": self._extract_key_points(summary),
                "action_items": self._extract_action_items(summary),
                "timestamps": self._extract_timestamps(summary)
            }

            logger.info(f"Successfully extracted data: {len(result['key_metrics'])} metrics, "
                       f"{len(result['key_points'])} points")
            return result

        except Exception as e:
            logger.error(f"Unexpected error during extraction: {e}", exc_info=True)
            return self._get_defaults()
    
    def _extract_executive_summary(self, summary: str) -> str:
        """
        Extract 30-second takeaway from summary.
        
        Looks for Overview/Summary section, extracts first 1-2 sentences,
        validates length, and provides sensible fallback.
        
        Args:
            summary: Full summary text
            
        Returns:
            str: Executive summary (1-2 sentences, 20-200 chars)
        """
        try:
            # Look for Overview or Summary section
            lines = summary.split('\n')
            in_overview = False
            overview_text = []
            
            for line in lines:
                if 'overview' in line.lower() or 'summary' in line.lower():
                    in_overview = True
                    continue
                
                if in_overview:
                    if line.startswith('#'):  # New section
                        break
                    if line.strip():
                        overview_text.append(line.strip())
                        if len(overview_text) >= 2:  # Get 1-2 sentences
                            break
            
            if overview_text:
                text = ' '.join(overview_text)
                # Extract first 1-2 sentences
                sentences = re.split(r'[.!?]+', text)
                result = '. '.join(s.strip() for s in sentences[:2] if s.strip())
                if result:
                    result = result[:200]  # Limit to 200 chars
                    logger.debug(f"Extracted executive summary: {result[:50]}...")
                    return result
            
            # Fallback: Use first 150 characters
            fallback = summary.replace('#', '').strip()[:150].strip()
            if fallback:
                logger.debug("Using fallback executive summary")
                return fallback
            
            return "Summary not available"
            
        except Exception as e:
            logger.warning(f"Error extracting executive summary: {e}")
            return "Summary not available"
    
    def _extract_key_metrics(self, summary: str) -> List[Dict[str, str]]:
        """
        Extract important numbers, statistics, and data points.

        Works across all content types:
        - Educational: student counts, test scores, statistics
        - Tech reviews: specs, prices, performance metrics
        - Tutorials: measurements, quantities, durations
        - News: dates, statistics, figures
        - Entertainment: ratings, viewership, records

        Args:
            summary: Full summary text

        Returns:
            List of dicts with keys: name, value, type
        """
        try:
            metrics = []
            seen_values = set()

            # Extract percentages (any domain)
            for match in self.percentage_pattern.finditer(summary):
                value = match.group(1)
                if value not in seen_values:
                    metrics.append({
                        "name": self._extract_context(summary, match),
                        "value": f"{value}%",
                        "type": "percentage"
                    })
                    seen_values.add(value)

            # Extract currency values (any domain)
            for match in self.currency_pattern.finditer(summary):
                value = match.group(1)
                if value not in seen_values:
                    metrics.append({
                        "name": self._extract_context(summary, match),
                        "value": f"${value}",
                        "type": "currency"
                    })
                    seen_values.add(value)

            # Extract dates (NEW)
            for match in self.date_pattern.finditer(summary):
                value = match.group(1)
                if value not in seen_values:
                    metrics.append({
                        "name": "Date",
                        "value": value,
                        "type": "date"
                    })
                    seen_values.add(value)

            # Extract measurements (NEW)
            for match in self.measurement_pattern.finditer(summary):
                value = match.group(0)
                if value not in seen_values:
                    metrics.append({
                        "name": self._extract_context(summary, match),
                        "value": value,
                        "type": "measurement"
                    })
                    seen_values.add(value)

            # Extract large numbers (NEW)
            for match in self.numeric_pattern.finditer(summary):
                value = match.group(0)
                if value not in seen_values:
                    metrics.append({
                        "name": self._extract_context(summary, match),
                        "value": value,
                        "type": "numeric"
                    })
                    seen_values.add(value)

            # Limit to top 5 metrics
            result = metrics[:5]
            logger.debug(f"Extracted {len(result)} key metrics")
            return result

        except Exception as e:
            logger.warning(f"Error extracting key metrics: {e}")
            return []

    def _extract_context(self, summary: str, match) -> str:
        """Extract context around a match for naming."""
        start = max(0, match.start() - 50)
        context = summary[start:match.end()]
        words = context.split()
        return words[-2].strip('*-') if len(words) > 1 else "Value"
    
    def _extract_key_points(self, summary: str) -> List[str]:
        """
        Extract main arguments/insights (3-5 bullet points).
        
        Looks for markdown bullets, cleans formatting, validates length,
        and provides fallback to sentences.
        
        Args:
            summary: Full summary text
            
        Returns:
            List of key point strings
        """
        try:
            # Find bullet points
            bullets = self.bullet_pattern.findall(summary)
            
            if bullets:
                # Clean and validate
                points = []
                for bullet in bullets[:5]:
                    cleaned = bullet.strip('*- ').strip()
                    if 10 < len(cleaned) < 200:  # Validate length
                        points.append(cleaned)
                
                if points:
                    logger.debug(f"Extracted {len(points)} key points from bullets")
                    return points
            
            # Fallback: Extract first 3 sentences
            sentences = re.split(r'[.!?]+', summary)
            points = []
            for sentence in sentences:
                cleaned = sentence.strip()
                if 10 < len(cleaned) < 200:
                    points.append(cleaned)
                    if len(points) >= 3:
                        break
            
            logger.debug(f"Extracted {len(points)} key points from sentences")
            return points
            
        except Exception as e:
            logger.warning(f"Error extracting key points: {e}")
            return []
    
    def _extract_action_items(self, summary: str) -> List[str]:
        """
        Extract actionable takeaways.
        
        Looks for Action Items/Takeaways sections, extracts bullets,
        and provides fallback to imperative verbs.
        
        Args:
            summary: Full summary text
            
        Returns:
            List of action item strings
        """
        try:
            # Look for Action Items section
            action_section = re.search(
                r'(?:action items|takeaways|recommendations)[\s\n]+(.*?)(?=\n#|\Z)',
                summary,
                re.IGNORECASE | re.DOTALL
            )
            
            if action_section:
                section_text = action_section.group(1)
                bullets = self.bullet_pattern.findall(section_text)
                
                if bullets:
                    items = [b.strip('*- ').strip() for b in bullets[:5]]
                    logger.debug(f"Extracted {len(items)} action items")
                    return items
            
            # Fallback: Look for imperative verbs
            imperative_verbs = ['review', 'consider', 'monitor', 'check', 'verify',
                              'update', 'adjust', 'evaluate', 'assess', 'analyze']
            items = []
            
            for sentence in re.split(r'[.!?]+', summary):
                cleaned = sentence.strip()
                if any(verb in cleaned.lower() for verb in imperative_verbs):
                    if 10 < len(cleaned) < 200:
                        items.append(cleaned)
                        if len(items) >= 3:
                            break
            
            logger.debug(f"Extracted {len(items)} action items from verbs")
            return items
            
        except Exception as e:
            logger.warning(f"Error extracting action items: {e}")
            return []
    
    def _extract_timestamps(self, summary: str) -> List[Dict[str, str]]:
        """
        Extract time-stamped key moments from transcript.
        
        Finds timestamp patterns, extracts context, classifies importance,
        and limits to 5-10 timestamps.
        
        Args:
            summary: Full summary text
            
        Returns:
            List of dicts with keys: time, topic, key_point, importance
        """
        try:
            timestamps = []
            
            for match in self.timestamp_pattern.finditer(summary):
                time_str = match.group(0)
                
                # Get context (sentence containing timestamp)
                start = max(0, match.start() - 100)
                end = min(len(summary), match.end() + 100)
                context = summary[start:end]
                
                # Extract topic and key point
                sentences = context.split('.')
                key_point = sentences[0].strip() if sentences else ""
                
                # Classify importance
                importance = "medium"
                for keyword in ['important', 'critical', 'key', 'major', 'significant']:
                    if keyword in context.lower():
                        importance = "high"
                        break
                
                timestamps.append({
                    "time": time_str,
                    "topic": "Key Moment",
                    "key_point": key_point[:100],
                    "importance": importance
                })
                
                if len(timestamps) >= 10:
                    break
            
            logger.debug(f"Extracted {len(timestamps)} timestamps")
            return timestamps
            
        except Exception as e:
            logger.warning(f"Error extracting timestamps: {e}")
            return []
    

    
    def _get_defaults(self) -> Dict[str, Any]:
        """
        Return default values for all fields.

        Used when extraction fails or input is invalid.

        Returns:
            Dict with all fields set to sensible defaults
        """
        return {
            "executive_summary": "Summary not available",
            "key_metrics": [],
            "key_points": [],
            "action_items": [],
            "timestamps": []
        }

