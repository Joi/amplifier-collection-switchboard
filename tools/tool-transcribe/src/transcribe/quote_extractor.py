"""Quote Extractor - uses Claude to extract memorable quotes from transcripts."""

import json
import os
from dataclasses import dataclass

from .logger import get_logger

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

logger = get_logger(__name__)


@dataclass
class Quote:
    """A memorable quote with context and timing."""
    text: str
    timestamp: float
    timestamp_link: str | None
    context: str


class QuoteExtractor:
    """Extract memorable quotes from transcripts using Claude."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        """Initialize quote extractor."""
        if not ANTHROPIC_AVAILABLE:
            raise ImportError("anthropic package not available")

        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")

        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
        self.client = Anthropic(api_key=self.api_key)

    def extract(self, transcript, video_url: str | None, video_id: str) -> list[Quote]:
        """Extract memorable quotes from a transcript."""
        transcript_with_timestamps = self._format_transcript_with_timestamps(transcript)

        prompt = f"""Extract 3-5 memorable, insightful quotes from this transcript.

Choose quotes that:
- Capture key ideas or surprising insights
- Are complete thoughts (not fragments)
- Would stand alone as meaningful statements
- Represent different aspects of the content

For each quote, provide:
1. The exact quote text
2. The timestamp (in seconds) when it appears
3. Context explaining why this quote is significant

Transcript:
{transcript_with_timestamps[:15000]}

Please respond in JSON format with an array of quotes:
[
  {{
    "text": "The exact quote here",
    "timestamp": 123.5,
    "context": "Why this quote matters"
  }}
]
"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}],
            )

            content = ""
            for block in response.content:
                if hasattr(block, "text"):
                    content = block.text
                    break
            if not content:
                content = str(response.content[0])
            quotes_data = self._parse_quotes_response(content)

            quotes = []
            for quote_data in quotes_data:
                timestamp_link = None
                if video_url and "youtube.com" in video_url:
                    seconds = int(quote_data.get("timestamp", 0))
                    timestamp_link = f"https://youtube.com/watch?v={video_id}&t={seconds}s"

                quotes.append(Quote(
                    text=quote_data.get("text", ""),
                    timestamp=quote_data.get("timestamp", 0.0),
                    timestamp_link=timestamp_link,
                    context=quote_data.get("context", ""),
                ))

            return quotes

        except Exception as e:
            logger.error(f"Failed to extract quotes: {e}")
            return []

    def _format_transcript_with_timestamps(self, transcript) -> str:
        """Format transcript with timestamps for better quote extraction."""
        if not transcript.segments:
            return transcript.text

        formatted = []
        for i, segment in enumerate(transcript.segments[:100]):
            if i % 5 == 0:
                minutes = int(segment.start // 60)
                seconds = int(segment.start % 60)
                formatted.append(f"\n[{minutes:02d}:{seconds:02d}] ")
            formatted.append(segment.text + " ")

        return "".join(formatted)

    def _parse_quotes_response(self, response_text: str) -> list[dict]:
        """Parse Claude's response to extract quote data."""
        try:
            response_text = response_text.strip()

            if response_text.startswith("```json"):
                response_text = response_text[7:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]
            elif response_text.startswith("```"):
                response_text = response_text[3:]
                if response_text.endswith("```"):
                    response_text = response_text[:-3]

            quotes_data = json.loads(response_text.strip())

            if not isinstance(quotes_data, list):
                logger.warning("Quote response was not a list")
                return []

            return quotes_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse quotes JSON: {e}")
            return []
        except Exception as e:
            logger.error(f"Error parsing quotes response: {e}")
            return []
