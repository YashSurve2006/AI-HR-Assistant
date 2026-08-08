"""Sentiment analysis module — employee feedback classification."""

import pandas as pd
from textblob import TextBlob
import data_processor as dp

def analyze_sentiment(text: str, pos_threshold: float = 0.1, neg_threshold: float = -0.1) -> dict:
    """Classify feedback as Positive, Neutral, or Negative using TextBlob."""
    if not text or not isinstance(text, str):
        return {
            "sentiment": "Neutral",
            "polarity": 0.0,
            "subjectivity": 0.0
        }
        
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    
    if polarity > pos_threshold:
        sentiment = "Positive"
    elif polarity < neg_threshold:
        sentiment = "Negative"
    else:
        sentiment = "Neutral"
        
    return {
        "sentiment": sentiment,
        "polarity": round(polarity, 4),
        "subjectivity": round(subjectivity, 4)
    }

def analyze_feedback_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Apply sentiment analysis to an entire feedback DataFrame."""
    if 'feedback' not in df.columns:
        raise ValueError("DataFrame must contain a 'feedback' column")
        
    sentiments = df['feedback'].apply(analyze_sentiment)
    
    df['sentiment'] = [s['sentiment'] for s in sentiments]
    df['polarity'] = [s['polarity'] for s in sentiments]
    df['subjectivity'] = [s['subjectivity'] for s in sentiments]
    
    return df

def get_sentiment_summary(df: pd.DataFrame) -> dict:
    """Generate summary statistics for the analyzed feedback DataFrame."""
    if 'sentiment' not in df.columns:
        df = analyze_feedback_dataframe(df)
        
    total = len(df)
    
    if total == 0:
        return {
            "total": 0,
            "positive": 0,
            "negative": 0,
            "neutral": 0,
            "positive_percentage": 0.0,
            "negative_percentage": 0.0,
            "neutral_percentage": 0.0,
            "average_rating": 0.0
        }
        
    positive = len(df[df['sentiment'] == 'Positive'])
    negative = len(df[df['sentiment'] == 'Negative'])
    neutral = len(df[df['sentiment'] == 'Neutral'])
    
    avg_rating = df['rating'].mean() if 'rating' in df.columns else 0.0
    
    return {
        "total": total,
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "positive_percentage": round((positive / total) * 100, 2),
        "negative_percentage": round((negative / total) * 100, 2),
        "neutral_percentage": round((neutral / total) * 100, 2),
        "average_rating": round(float(avg_rating), 2)
    }

def get_department_summary(df: pd.DataFrame) -> list:
    """Generate department-wise sentiment summary."""
    if 'sentiment' not in df.columns:
        df = analyze_feedback_dataframe(df)
        
    if 'department' not in df.columns:
        return []
        
    dept_summary = []
    
    for dept, group in df.groupby('department'):
        total = len(group)
        positive = len(group[group['sentiment'] == 'Positive'])
        negative = len(group[group['sentiment'] == 'Negative'])
        neutral = len(group[group['sentiment'] == 'Neutral'])
        avg_rating = group['rating'].mean() if 'rating' in group.columns else 0.0
        
        dept_summary.append({
            "department": str(dept),
            "total": total,
            "positive": positive,
            "negative": negative,
            "neutral": neutral,
            "positive_percentage": round((positive / total) * 100, 2),
            "negative_percentage": round((negative / total) * 100, 2),
            "neutral_percentage": round((neutral / total) * 100, 2),
            "average_rating": round(float(avg_rating), 2)
        })
        
    return sorted(dept_summary, key=lambda x: x['total'], reverse=True)
