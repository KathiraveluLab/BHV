"""Sentiment analysis module."""
from app.sentiment.textblob_provider import TextBlobProvider

# Default sentiment analyzer
sentiment_analyzer = TextBlobProvider()

def analyze_sentiment(text):
    """Analyze sentiment of text using the default provider."""
    return sentiment_analyzer.analyze(text)

