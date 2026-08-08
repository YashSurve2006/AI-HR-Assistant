"""Data preprocessing and loading utilities for AI HR Assistant."""

import re
from pathlib import Path
from typing import List, Optional, Union

import numpy as np
import pandas as pd

import config

# NLTK resources — downloaded on first use
_NLTK_INITIALIZED = False

DATASET_DIR = Path(config.DATASET_DIR)

DATASET_FILES = {
    "hr_faq": "hr_faq.csv",
    "jobs": "jobs.csv",
    "feedback": "feedback.csv",
}

HR_FAQ_COLUMNS = ["question", "answer", "category"]
JOBS_COLUMNS = ["job_id", "title", "department", "description", "required_skills", "experience", "location"]
FEEDBACK_COLUMNS = ["feedback_id", "employee_name", "department", "rating", "feedback", "date"]

EXPECTED_RANGES = {
    "hr_faq": (40, 150),
    "jobs": (15, 20),
    "feedback": (30, 40),
}


def _ensure_nltk_data() -> None:
    """Download required NLTK corpora if not already present."""
    global _NLTK_INITIALIZED
    if _NLTK_INITIALIZED:
        return

    import nltk

    resources = [
        ("tokenizers/punkt", "punkt"),
        ("tokenizers/punkt_tab", "punkt_tab"),
        ("corpora/stopwords", "stopwords"),
        ("corpora/wordnet", "wordnet"),
        ("corpora/omw-1.4", "omw-1.4"),
    ]

    for lookup_path, download_name in resources:
        try:
            nltk.data.find(lookup_path)
        except LookupError:
            nltk.download(download_name, quiet=True)

    _NLTK_INITIALIZED = True


def _dataset_path(name: str) -> Path:
    """Return the path to a dataset CSV file."""
    return DATASET_DIR / DATASET_FILES[name]


def _normalize_missing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing/null values while preserving original columns.

    Text columns are filled with empty strings; numeric columns with NaN kept
    for validation to catch, or filled with appropriate defaults where safe.
    """
    result = df.copy()
    for col in result.columns:
        if result[col].dtype == "object":
            result[col] = result[col].replace({np.nan: None})
            result[col] = result[col].apply(
                lambda v: "" if v is None or (isinstance(v, float) and np.isnan(v)) else str(v).strip()
            )
    return result


import unicodedata

_CONTRACTION_MAP = {
    r"\bwhats\b": "what is",
    r"\bwhat's\b": "what is",
    r"\bhows\b": "how is",
    r"\bhow's\b": "how is",
    r"\bwheres\b": "where is",
    r"\bwhere's\b": "where is",
    r"\bwhens\b": "when is",
    r"\bwhen's\b": "when is",
    r"\bwhys\b": "why is",
    r"\bwhy's\b": "why is",
    r"\bwhos\b": "who is",
    r"\bwho's\b": "who is",
    r"\bive\b": "i have",
    r"\bi've\b": "i have",
    r"\bim\b": "i am",
    r"\bi'm\b": "i am",
    r"\bcant\b": "cannot",
    r"\bcan't\b": "cannot",
    r"\bdont\b": "do not",
    r"\bdon't\b": "do not",
    r"\bdoesnt\b": "does not",
    r"\bdoesn't\b": "does not",
    r"\bisnt\b": "is not",
    r"\bisn't\b": "is not",
    r"\barent\b": "are not",
    r"\baren't\b": "are not",
    r"\bwont\b": "will not",
    r"\bwon't\b": "will not",
}

# Key question/structural words preserved during stopword filtering
_PRESERVED_WORDS = {
    "how", "many", "much", "what", "when", "where", "why", "who", "which",
    "can", "could", "should", "would", "is", "are", "do", "does", "did",
    "have", "has", "had", "not", "no", "get", "take", "apply"
}

def clean_text(text: Optional[str]) -> str:
    """
    Clean raw text by normalizing unicode, expanding contractions,
    removing punctuation, and normalizing whitespace.

    Args:
        text: Raw input string.

    Returns:
        Cleaned lowercase string.
    """
    if text is None or (isinstance(text, float) and np.isnan(text)):
        return ""

    text = str(text).strip()
    # Unicode NFKD normalization
    text = unicodedata.normalize("NFKD", text)
    text = text.encode("ASCII", "ignore").decode("utf-8").lower()
    
    # URL stripping
    text = re.sub(r"http\S+|www\S+", "", text)
    
    # Contraction expansion
    for pattern, replacement in _CONTRACTION_MAP.items():
        text = re.sub(pattern, replacement, text)
        
    # Strip symbols and punctuation
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    
    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def tokenize_text(text: Optional[str]) -> List[str]:
    """
    Tokenize cleaned text into alphabetic word tokens using NLTK.

    Args:
        text: Raw or cleaned input string.

    Returns:
        List of word tokens.
    """
    _ensure_nltk_data()

    from nltk.tokenize import word_tokenize

    cleaned = clean_text(text)
    if not cleaned:
        return []

    return [t for t in word_tokenize(cleaned) if t.isalpha()]


def remove_stopwords(tokens: List[str]) -> List[str]:
    """
    Remove English non-semantic stopwords while preserving key question words.

    Args:
        tokens: List of word tokens.

    Returns:
        Filtered token list.
    """
    _ensure_nltk_data()

    from nltk.corpus import stopwords

    stop_words = set(stopwords.words("english")) - _PRESERVED_WORDS
    return [t for t in tokens if t not in stop_words]


def preprocess_text(text: Optional[str]) -> str:
    """
    Full NLP preprocessing pipeline: clean, expand contractions, tokenize,
    selective stopword removal, WordNet lemmatization, and Snowball stemming.

    Returns a space-joined dual-representation string of original, lemmatized,
    and stemmed tokens.

    Args:
        text: Raw input string.

    Returns:
        Preprocessed text string.
    """
    tokens = tokenize_text(text)
    filtered = remove_stopwords(tokens)
    
    _ensure_nltk_data()
    from nltk.stem import WordNetLemmatizer, SnowballStemmer
    
    lemmatizer = WordNetLemmatizer()
    stemmer = SnowballStemmer("english")
    
    # Generate lemmatized and stemmed forms
    lemmas = [lemmatizer.lemmatize(t, pos="n") for t in filtered]
    lemmas = [lemmatizer.lemmatize(t, pos="v") for t in lemmas]
    stems = [stemmer.stem(t) for t in filtered]
    
    # Combine original tokens, lemmas, and stems for multi-representation matching
    combined = filtered + lemmas + stems
    
    # Deduplicate while preserving sequence order
    seen = set()
    deduped = []
    for token in combined:
        if token not in seen:
            seen.add(token)
            deduped.append(token)
            
    return " ".join(deduped)


def _load_csv(name: str, expected_columns: List[str]) -> pd.DataFrame:
    """Load a CSV file and validate required columns."""
    path = _dataset_path(name)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")

    df = pd.read_csv(path)
    missing = [col for col in expected_columns if col not in df.columns]
    if missing:
        raise ValueError(f"{DATASET_FILES[name]} is missing columns: {missing}")

    return _normalize_missing(df[expected_columns].copy())


def _add_processed_columns(df: pd.DataFrame, text_columns: List[str]) -> pd.DataFrame:
    """Add preprocessed columns without modifying original text columns."""
    result = df.copy()
    for col in text_columns:
        if col in result.columns:
            result[f"{col}_processed"] = result[col].apply(preprocess_text)
    return result


def load_hr_faq(preprocess: bool = False) -> pd.DataFrame:
    """
    Load the HR FAQ dataset.

    Args:
        preprocess: If True, add question_processed and answer_processed columns.

    Returns:
        DataFrame with original columns preserved.
    """
    df = _load_csv("hr_faq", HR_FAQ_COLUMNS)

    if preprocess:
        df = _add_processed_columns(df, ["question", "answer"])

    return df.reset_index(drop=True)


def load_jobs(preprocess: bool = False) -> pd.DataFrame:
    """
    Load the jobs dataset.

    Args:
        preprocess: If True, add description_processed and required_skills_processed columns.

    Returns:
        DataFrame with original columns preserved.
    """
    df = _load_csv("jobs", JOBS_COLUMNS)
    df["job_id"] = pd.to_numeric(df["job_id"], errors="coerce").astype("Int64")

    if preprocess:
        df = _add_processed_columns(df, ["description", "required_skills"])

    return df.reset_index(drop=True)


def load_feedback(preprocess: bool = False) -> pd.DataFrame:
    """
    Load the employee feedback dataset.

    Args:
        preprocess: If True, add feedback_processed column.

    Returns:
        DataFrame with original columns preserved.
    """
    df = _load_csv("feedback", FEEDBACK_COLUMNS)
    df["feedback_id"] = pd.to_numeric(df["feedback_id"], errors="coerce").astype("Int64")
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce")

    if preprocess:
        df = _add_processed_columns(df, ["feedback"])

    return df.reset_index(drop=True)


def validate_datasets() -> dict:
    """
    Validate all datasets for file presence, schema, row counts, and data quality.

    Returns:
        Dictionary with 'valid' (bool) and per-dataset validation details.
    """
    report = {"valid": True, "datasets": {}}

    loaders = {
        "hr_faq": (load_hr_faq, HR_FAQ_COLUMNS),
        "jobs": (load_jobs, JOBS_COLUMNS),
        "feedback": (load_feedback, FEEDBACK_COLUMNS),
    }

    for name, (loader, columns) in loaders.items():
        info = {"ok": True, "errors": [], "warnings": []}
        path = _dataset_path(name)

        if not path.exists():
            info["ok"] = False
            info["errors"].append(f"File not found: {path}")
            report["valid"] = False
            report["datasets"][name] = info
            continue

        try:
            df = loader(preprocess=False)
        except Exception as exc:
            info["ok"] = False
            info["errors"].append(str(exc))
            report["valid"] = False
            report["datasets"][name] = info
            continue

        info["rows"] = len(df)
        info["columns"] = list(df.columns)

        min_rows, max_rows = EXPECTED_RANGES[name]
        if not (min_rows <= len(df) <= max_rows):
            info["warnings"].append(
                f"Row count {len(df)} outside expected range ({min_rows}-{max_rows})"
            )

        if list(df.columns) != columns:
            info["ok"] = False
            info["errors"].append(f"Column mismatch. Expected {columns}, got {list(df.columns)}")
            report["valid"] = False

        empty_mask = df.apply(lambda row: row.astype(str).str.strip().eq("").all(), axis=1)
        if empty_mask.any():
            info["ok"] = False
            info["errors"].append(f"{empty_mask.sum()} completely empty row(s) found")
            report["valid"] = False

        if name == "hr_faq":
            if df["question"].duplicated().any():
                dupes = int(df["question"].duplicated().sum())
                info["warnings"].append(f"{dupes} duplicate question(s) found")
            if (df["question"] == "").any() or (df["answer"] == "").any():
                info["ok"] = False
                info["errors"].append("Empty question or answer values found")
                report["valid"] = False

        if name == "jobs":
            if df["job_id"].isna().any():
                info["ok"] = False
                info["errors"].append("Missing job_id values found")
                report["valid"] = False
            if df["job_id"].duplicated().any():
                info["ok"] = False
                info["errors"].append("Duplicate job_id values found")
                report["valid"] = False

        if name == "feedback":
            invalid_ratings = df[~df["rating"].between(1, 5)]
            if not invalid_ratings.empty:
                info["ok"] = False
                info["errors"].append(
                    f"{len(invalid_ratings)} record(s) with invalid rating (must be 1-5)"
                )
                report["valid"] = False
            if (df["feedback"] == "").any():
                info["ok"] = False
                info["errors"].append("Empty feedback text found")
                report["valid"] = False

        report["datasets"][name] = info

    return report


if __name__ == "__main__":
    print("=== AI HR Assistant — Dataset Loader Test ===\n")

    hr_faq = load_hr_faq(preprocess=True)
    jobs = load_jobs(preprocess=True)
    feedback = load_feedback(preprocess=True)

    for label, df in [("HR FAQ", hr_faq), ("Jobs", jobs), ("Feedback", feedback)]:
        print(f"--- {label} ---")
        print(f"  Shape  : {df.shape}")
        print(f"  Columns: {list(df.columns)}")
        print()

    sample = hr_faq.loc[0, "question"]
    print("--- Preprocessing Sample ---")
    print(f"  Original : {sample}")
    print(f"  Cleaned  : {clean_text(sample)}")
    print(f"  Tokens   : {tokenize_text(sample)}")
    print(f"  Processed: {preprocess_text(sample)}")
    print()

    print("--- Validation ---")
    validation = validate_datasets()
    print(f"  Overall valid: {validation['valid']}")
    for name, info in validation["datasets"].items():
        status = "PASS" if info["ok"] else "FAIL"
        print(f"  {name}: {status} ({info.get('rows', '?')} rows)")
        for err in info.get("errors", []):
            print(f"    ERROR: {err}")
        for warn in info.get("warnings", []):
            print(f"    WARN:  {warn}")

    print("\nAll tests completed.")
