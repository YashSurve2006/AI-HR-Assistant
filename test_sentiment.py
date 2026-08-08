import backend.sentiment as sent

if __name__ == "__main__":
    sentences = [
        ("Positive", "I love this company, everything is amazing and great!"),
        ("Negative", "This is the worst experience ever, totally unacceptable."),
        ("Neutral", "I attended the meeting on Tuesday."),
        ("Mixed", "The food is great but the management is terrible.")
    ]
    
    for label, text in sentences:
        res = sent.analyze_sentiment(text)
        print(f"[{label}] {text}")
        print(f"  -> Sentiment: {res['sentiment']} (Polarity: {res['polarity']}, Subjectivity: {res['subjectivity']})\n")
