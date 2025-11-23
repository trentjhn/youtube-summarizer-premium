"""
Unit tests for DataExtractor service

Tests all extraction methods with diverse content types: educational, tech reviews,
tutorials, documentaries, and more. Verifies general-purpose functionality.
"""

import pytest
from src.services.data_extractor import DataExtractor


@pytest.fixture
def extractor():
    """Create DataExtractor instance for testing."""
    return DataExtractor()


@pytest.fixture
def sample_educational_summary():
    """Sample educational content summary."""
    return """
# Python Programming Fundamentals

## Overview
Learn Python basics with 50,000+ students worldwide. This comprehensive course covers
fundamentals in 40 hours with 95% completion rate and 4.8/5 star rating.

## Key Points
- Variables and data types (strings, integers, floats)
- Functions and modules for code reusability
- Object-oriented programming concepts
- Error handling and debugging techniques
- Real-world project examples

## Action Items
- Complete 40 hours of video content
- Practice with 20+ coding exercises
- Build 3 capstone projects
- Join community forum for support

## Timestamps
- 2:15 - Introduction to Python
- 5:30 - Variables and data types
- 12:45 - Functions and scope
- 25:00 - Object-oriented programming
"""


@pytest.fixture
def sample_tech_review_summary():
    """Sample tech review content."""
    return """
# iPhone 15 Pro Review

## Overview
Apple's latest flagship with 6.1" display, A17 Pro chip, and $999 starting price.
Battery life improved to 26 hours with new efficiency gains.

## Key Points
- 6.1 inch Super Retina XDR display
- A17 Pro chip with 8-core processor
- 48MP main camera with advanced features
- 26 hour battery life
- Starting at $999 for 128GB model

## Action Items
- Compare with previous generation
- Check carrier deals and promotions
- Review camera samples
- Consider trade-in options

## Timestamps
- 1:30 - Design and build quality
- 4:15 - Display and performance
- 8:45 - Camera capabilities
- 12:00 - Battery life testing
"""


@pytest.fixture
def sample_tutorial_summary():
    """Sample tutorial content."""
    return """
# How to Bake Perfect Chocolate Chip Cookies

## Overview
Master the art of baking cookies in 30 minutes. This tutorial covers 15 essential
techniques used by professional bakers with 92% success rate.

## Key Points
- Measure ingredients precisely (2 cups flour, 1 cup butter)
- Cream butter and sugar for 3-5 minutes
- Bake at 375 degrees for 10-12 minutes
- Cool on rack for 5 minutes before serving
- Store in airtight container for 7 days

## Action Items
- Gather all ingredients before starting
- Preheat oven to 375 degrees
- Follow timing precisely
- Let cookies cool completely

## Timestamps
- 1:00 - Ingredient preparation
- 3:30 - Mixing technique
- 8:15 - Baking process
- 12:00 - Cooling and storage
"""


@pytest.fixture
def sample_documentary_summary():
    """Sample documentary content."""
    return """
# The History of Space Exploration

## Overview
Explore 60 years of space exploration from 1961 to 2021. This documentary features
interviews with 25+ astronauts and covers 150+ missions across 8 countries.

## Key Points
- First human spaceflight on April 12, 1961
- Moon landing on July 20, 1969
- Space Shuttle program (1981-2011)
- International Space Station (1998-present)
- Private space companies emerging since 2010

## Action Items
- Watch full documentary series (8 hours)
- Read recommended books on space history
- Visit space museums and exhibits
- Follow current space missions

## Timestamps
- 5:30 - Early space race (1961-1969)
- 15:45 - Apollo program highlights
- 28:00 - Space Shuttle era
- 45:15 - Modern space exploration
"""


class TestExtractExecutiveSummary:
    """Test executive summary extraction."""

    def test_extract_from_overview_section(self, extractor, sample_educational_summary):
        """Test extracting from Overview section."""
        result = extractor._extract_executive_summary(sample_educational_summary)
        assert len(result) > 0
        assert len(result) <= 200

    def test_empty_summary(self, extractor):
        """Test with empty summary."""
        result = extractor._extract_executive_summary("")
        assert result == "Summary not available"

    def test_very_short_summary(self, extractor):
        """Test with very short summary."""
        result = extractor._extract_executive_summary("Short text")
        assert len(result) > 0

    def test_summary_without_overview(self, extractor):
        """Test summary without Overview section."""
        summary = "Some content without overview section"
        result = extractor._extract_executive_summary(summary)
        assert len(result) > 0


class TestExtractKeyMetrics:
    """Test key metrics extraction."""

    def test_extract_percentages(self, extractor, sample_educational_summary):
        """Test extracting percentage metrics."""
        result = extractor._extract_key_metrics(sample_educational_summary)
        assert len(result) > 0

        # Check for expected percentages
        values = [m['value'] for m in result]
        assert any('%' in v for v in values)

    def test_extract_currency(self, extractor):
        """Test extracting currency values."""
        summary = "The product costs $999 and the premium version is $1299"
        result = extractor._extract_key_metrics(summary)
        assert len(result) > 0
        assert any('$' in m['value'] for m in result)

    def test_extract_dates(self, extractor):
        """Test extracting date metrics."""
        summary = "The event is on 01/15/2024 and the deadline is 2024-12-31"
        result = extractor._extract_key_metrics(summary)
        assert len(result) > 0
        assert any(m['type'] == 'date' for m in result)

    def test_extract_measurements(self, extractor):
        """Test extracting measurement metrics."""
        summary = "The distance is 100 km and the weight is 50 kg. Duration is 2 hours."
        result = extractor._extract_key_metrics(summary)
        assert len(result) > 0
        assert any(m['type'] == 'measurement' for m in result)

    def test_extract_large_numbers(self, extractor):
        """Test extracting large number metrics."""
        summary = "The company has 50 million users and 2.5 billion in revenue"
        result = extractor._extract_key_metrics(summary)
        assert len(result) > 0
        assert any(m['type'] == 'numeric' for m in result)

    def test_no_metrics(self, extractor):
        """Test with summary containing no metrics."""
        summary = "This is a summary with no numbers or percentages"
        result = extractor._extract_key_metrics(summary)
        assert result == []

    def test_metric_deduplication(self, extractor):
        """Test that duplicate metrics are removed."""
        summary = "The rate is 5% and the rate is 5% again"
        result = extractor._extract_key_metrics(summary)
        # Should not have duplicates
        values = [m['value'] for m in result]
        assert len(values) == len(set(values))

    def test_max_five_metrics(self, extractor):
        """Test that only top 5 metrics are returned."""
        summary = "1% 2% 3% 4% 5% 6% 7% 8% 9% 10%"
        result = extractor._extract_key_metrics(summary)
        assert len(result) <= 5


class TestExtractKeyPoints:
    """Test key points extraction."""

    def test_extract_bullet_points(self, extractor, sample_educational_summary):
        """Test extracting bullet points."""
        result = extractor._extract_key_points(sample_educational_summary)
        assert len(result) > 0
        assert all(isinstance(p, str) for p in result)
    
    def test_fallback_to_sentences(self, extractor):
        """Test fallback to sentences when no bullets."""
        summary = "First sentence. Second sentence. Third sentence."
        result = extractor._extract_key_points(summary)
        assert len(result) > 0
    
    def test_empty_summary(self, extractor):
        """Test with empty summary."""
        result = extractor._extract_key_points("")
        assert result == []
    
    def test_max_five_points(self, extractor):
        """Test that only top 5 points are returned."""
        summary = "- Point 1\n- Point 2\n- Point 3\n- Point 4\n- Point 5\n- Point 6"
        result = extractor._extract_key_points(summary)
        assert len(result) <= 5


class TestExtractActionItems:
    """Test action items extraction."""

    def test_extract_from_action_items_section(self, extractor, sample_educational_summary):
        """Test extracting from Action Items section."""
        result = extractor._extract_action_items(sample_educational_summary)
        assert len(result) > 0
    
    def test_fallback_to_imperative_verbs(self, extractor):
        """Test fallback to imperative verbs."""
        summary = "Review your portfolio. Consider defensive positions. Monitor the market."
        result = extractor._extract_action_items(summary)
        assert len(result) > 0
    
    def test_no_action_items(self, extractor):
        """Test with summary containing no action items."""
        summary = "This is just informational content with no actions"
        result = extractor._extract_action_items(summary)
        # May return empty or find some verbs
        assert isinstance(result, list)


class TestExtractTimestamps:
    """Test timestamp extraction."""

    def test_extract_timestamps(self, extractor, sample_tutorial_summary):
        """Test extracting timestamps."""
        result = extractor._extract_timestamps(sample_tutorial_summary)
        assert len(result) > 0
        assert all('time' in t for t in result)

    def test_timestamp_format(self, extractor, sample_tutorial_summary):
        """Test that timestamps are in correct format."""
        result = extractor._extract_timestamps(sample_tutorial_summary)
        for ts in result:
            assert ':' in ts['time']

    def test_no_timestamps(self, extractor):
        """Test with summary containing no timestamps."""
        summary = "This summary has no timestamps"
        result = extractor._extract_timestamps(summary)
        assert result == []

    def test_max_ten_timestamps(self, extractor):
        """Test that only top 10 timestamps are returned."""
        summary = "\n".join([f"{i}:00 - Point {i}" for i in range(15)])
        result = extractor._extract_timestamps(summary)
        assert len(result) <= 10


class TestExtractIntegration:
    """Integration tests for full extraction."""

    def test_extract_all_fields(self, extractor, sample_educational_summary):
        """Test that extract returns all required fields."""
        result = extractor.extract(sample_educational_summary)

        required_fields = [
            "executive_summary", "key_metrics", "key_points",
            "action_items", "timestamps"
        ]

        for field in required_fields:
            assert field in result

    def test_extract_with_empty_summary(self, extractor):
        """Test extract with empty summary returns defaults."""
        result = extractor.extract("")

        assert result["executive_summary"] == "Summary not available"
        assert result["key_metrics"] == []
        assert result["key_points"] == []
        assert result["action_items"] == []
        assert result["timestamps"] == []

    def test_extract_with_invalid_input(self, extractor):
        """Test extract with invalid input."""
        result = extractor.extract(None)
        assert result["executive_summary"] == "Summary not available"

    def test_extract_educational_content(self, extractor, sample_educational_summary):
        """Test extraction with educational content."""
        result = extractor.extract(sample_educational_summary)

        # Verify we got meaningful data
        assert len(result["executive_summary"]) > 0
        assert len(result["key_points"]) > 0

    def test_extract_tech_review_content(self, extractor, sample_tech_review_summary):
        """Test extraction with tech review content."""
        result = extractor.extract(sample_tech_review_summary)

        # Verify we got meaningful data
        assert len(result["executive_summary"]) > 0
        assert len(result["key_metrics"]) > 0

    def test_extract_tutorial_content(self, extractor, sample_tutorial_summary):
        """Test extraction with tutorial content."""
        result = extractor.extract(sample_tutorial_summary)

        # Verify we got meaningful data
        assert len(result["key_points"]) > 0
        assert len(result["action_items"]) > 0

    def test_extract_documentary_content(self, extractor, sample_documentary_summary):
        """Test extraction with documentary content."""
        result = extractor.extract(sample_documentary_summary)

        # Verify we got meaningful data
        assert len(result["key_metrics"]) > 0
        assert len(result["timestamps"]) > 0

    def test_extract_with_title(self, extractor, sample_educational_summary):
        """Test extract with title parameter."""
        result = extractor.extract(sample_educational_summary, title="Python Tutorial")
        assert "executive_summary" in result


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_very_long_summary(self, extractor):
        """Test with very long summary."""
        summary = "Content. " * 10000
        result = extractor.extract(summary)
        assert isinstance(result, dict)
    
    def test_special_characters(self, extractor):
        """Test with special characters."""
        summary = "Market: $100 (50%) - Very important! #Fed @CNBC"
        result = extractor.extract(summary)
        assert isinstance(result, dict)
    
    def test_unicode_content(self, extractor):
        """Test with unicode content."""
        summary = "Market moved: 📈 up 5% 💰 earnings 🚀"
        result = extractor.extract(summary)
        assert isinstance(result, dict)
    
    def test_malformed_markdown(self, extractor):
        """Test with malformed markdown."""
        summary = "# Unclosed header\n- Bullet without proper format\n## Another header"
        result = extractor.extract(summary)
        assert isinstance(result, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

