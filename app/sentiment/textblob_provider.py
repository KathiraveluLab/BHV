"""TextBlob-based sentiment analysis provider."""
from textblob import TextBlob
from app.sentiment.base import SentimentProvider


class TextBlobProvider(SentimentProvider):
    """Sentiment analyzer using TextBlob library."""
    
    def analyze(self, text):
        """
        Analyze sentiment using TextBlob.
        
        Args:
            text: Input text to analyze
            
        Returns:
            dict: Dictionary with 'polarity' (float) and 'label' (str)
        """
        if not text or not isinstance(text, str):
            return {'polarity': 0.0, 'label': 'neutral'}
        
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        return {
            'polarity': polarity,
            'label': self.label_sentiment(polarity)
        }

