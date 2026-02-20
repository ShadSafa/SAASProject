"""
VADER sentiment analysis service for social media comment emotion detection.

VADER (Valence Aware Dictionary and sEntiment Reasoner) is optimized for social media
text, handling emojis, slang, capitalization emphasis, and abbreviations.

Reference: https://www.nltk.org/howto/vader.html
"""

from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

# Download VADER lexicon on first import (idempotent)
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon', quiet=True)

# Initialize VADER analyzer (singleton)
sia = SentimentIntensityAnalyzer()


def analyze_comment_sentiment(comment_text: str) -> dict:
    """
    Analyze sentiment of a single comment using VADER.

    VADER returns polarity scores for negative, neutral, and positive sentiments,
    along with a compound score ranging from -1.0 (most negative) to +1.0 (most positive).

    Args:
        comment_text: The comment text to analyze (supports emojis, slang, abbreviations)

    Returns:
        Dictionary with keys:
        - 'neg': float - Proportion of text that is negative (0.0 to 1.0)
        - 'neu': float - Proportion of text that is neutral (0.0 to 1.0)
        - 'pos': float - Proportion of text that is positive (0.0 to 1.0)
        - 'compound': float - Normalized compound score (-1.0 to 1.0)

    Example:
        >>> result = analyze_comment_sentiment("This is amazing! 🔥🔥🔥")
        >>> result['compound']  # > 0.5 (positive)
    """
    scores = sia.polarity_scores(comment_text)
    return scores


def categorize_sentiment(compound_score: float) -> str:
    """
    Categorize a VADER compound score into sentiment categories.

    Uses VADER's recommended thresholds:
    - compound >= 0.05: positive
    - compound <= -0.05: negative
    - -0.05 < compound < 0.05: neutral

    Args:
        compound_score: The compound score from analyze_comment_sentiment()

    Returns:
        One of: "positive", "negative", or "neutral"

    Example:
        >>> categorize_sentiment(0.6)
        'positive'
        >>> categorize_sentiment(-0.3)
        'negative'
        >>> categorize_sentiment(0.01)
        'neutral'
    """
    if compound_score >= 0.05:
        return "positive"
    elif compound_score <= -0.05:
        return "negative"
    else:
        return "neutral"


def analyze_comment_batch(comments: list[str]) -> dict:
    """
    Analyze sentiment for multiple comments and return summary statistics.

    Processes a batch of comments and returns aggregated sentiment counts and average compound score.

    Args:
        comments: List of comment texts to analyze

    Returns:
        Dictionary with keys:
        - 'positive': int - Count of comments categorized as positive
        - 'neutral': int - Count of comments categorized as neutral
        - 'negative': int - Count of comments categorized as negative
        - 'avg_compound': float - Average compound score across all comments

    Example:
        >>> comments = ["Great!", "Okay", "Terrible"]
        >>> result = analyze_comment_batch(comments)
        >>> result['positive']
        1
        >>> result['negative']
        1
        >>> result['neutral']
        1
    """
    if not comments:
        return {
            "positive": 0,
            "neutral": 0,
            "negative": 0,
            "avg_compound": 0.0
        }

    sentiments = {
        "positive": 0,
        "neutral": 0,
        "negative": 0
    }
    total_compound = 0.0

    for comment in comments:
        scores = analyze_comment_sentiment(comment)
        compound = scores['compound']
        sentiment = categorize_sentiment(compound)
        sentiments[sentiment] += 1
        total_compound += compound

    avg_compound = total_compound / len(comments)

    return {
        "positive": sentiments["positive"],
        "neutral": sentiments["neutral"],
        "negative": sentiments["negative"],
        "avg_compound": avg_compound
    }
