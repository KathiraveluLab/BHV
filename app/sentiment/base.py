"""Base class for sentiment analysis providers."""
from abc import ABC, abstractmethod


class SentimentProvider(ABC):
    """Abstract base class for sentiment analysis providers."""
    
    @abstractmethod
    def analyze(self, text):
        """
        Analyze sentiment of text.
        
        Args:
            text: Input text to analyze
            
        Returns:
            dict: Dictionary with 'polarity' (float), 'label' (str: 'positive', 'neutral', 'negative')
        """
        pass
    
    @staticmethod
    def label_sentiment(polarity):
        """
        Convert polarity score to label.
        
        Args:
            polarity: Float between -1 (negative) and 1 (positive)
            
        Returns:
            str: 'positive', 'neutral', or 'negative'
        """
        if polarity > 0.1:
            return 'positive'
        elif polarity < -0.1:
            return 'negative'
        else:
            return 'neutral'

