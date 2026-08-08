"""Data visualization module — prepares Chart.js-ready JSON data from datasets."""

import pandas as pd
import numpy as np
import data_processor as dp
import sentiment as snt


def _safe_int(val) -> int:
    """Convert numpy/pandas int types to native Python int."""
    return int(val)


def _safe_float(val) -> float:
    """Convert numpy/pandas float types to native Python float."""
    return round(float(val), 2)


def get_feedback_chart_data() -> dict:
    """Return overall sentiment counts for a doughnut/pie chart."""
    df = dp.load_feedback()
    df = snt.analyze_feedback_dataframe(df)
    counts = df['sentiment'].value_counts()

    return {
        "labels": ["Positive", "Negative", "Neutral"],
        "values": [
            _safe_int(counts.get("Positive", 0)),
            _safe_int(counts.get("Negative", 0)),
            _safe_int(counts.get("Neutral", 0)),
        ]
    }


def get_department_sentiment_data() -> list:
    """Return department-wise positive/negative/neutral counts for a grouped bar chart."""
    df = dp.load_feedback()
    df = snt.analyze_feedback_dataframe(df)
    dept_summary = snt.get_department_summary(df)

    return [
        {
            "department": d["department"],
            "positive": d["positive"],
            "negative": d["negative"],
            "neutral": d["neutral"],
        }
        for d in dept_summary
    ]


def get_rating_distribution() -> list:
    """Return count of feedback records per rating (1–5) for a bar chart."""
    df = dp.load_feedback()
    all_ratings = pd.Series(range(1, 6), dtype="int64")
    counts = df['rating'].value_counts().reindex(all_ratings, fill_value=0)

    return [
        {"rating": _safe_int(rating), "count": _safe_int(count)}
        for rating, count in sorted(counts.items())
    ]


def get_job_distribution() -> list:
    """Return number of jobs per department for a bar/pie chart."""
    df = dp.load_jobs()
    counts = df['department'].value_counts()

    return [
        {"department": str(dept), "count": _safe_int(count)}
        for dept, count in counts.items()
    ]


def get_job_location_distribution() -> list:
    """Return number of jobs per location for a bar/pie chart."""
    df = dp.load_jobs()
    counts = df['location'].value_counts()

    return [
        {"location": str(loc), "count": _safe_int(count)}
        for loc, count in counts.items()
    ]


def get_dashboard_summary() -> dict:
    """Return high-level summary statistics for the dashboard header cards."""
    jobs_df = dp.load_jobs()
    feedback_df = dp.load_feedback()
    analyzed_df = snt.analyze_feedback_dataframe(feedback_df)

    total_jobs = _safe_int(len(jobs_df))
    total_feedback = _safe_int(len(analyzed_df))

    avg_rating = _safe_float(analyzed_df['rating'].mean()) if total_feedback > 0 else 0.0

    sentiment_summary = snt.get_sentiment_summary(analyzed_df)

    return {
        "total_jobs": total_jobs,
        "total_feedback": total_feedback,
        "average_rating": avg_rating,
        "positive_percentage": _safe_float(sentiment_summary["positive_percentage"]),
        "negative_percentage": _safe_float(sentiment_summary["negative_percentage"]),
        "neutral_percentage": _safe_float(sentiment_summary["neutral_percentage"]),
        "positive": _safe_int(sentiment_summary["positive"]),
        "negative": _safe_int(sentiment_summary["negative"]),
        "neutral": _safe_int(sentiment_summary["neutral"]),
    }
