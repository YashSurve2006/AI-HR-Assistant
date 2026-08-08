import sys
import time
import requests

API_URL = "http://127.0.0.1:5000/api/chat"
SESSION_ID = "test_session_999"

def test_chat(query: str, expected_category=None, expect_high_conf=False, expect_fallback=False):
    t0 = time.time()
    resp = requests.post(API_URL, json={"message": query, "session_id": SESSION_ID}).json()
    t1 = time.time()
    
    print("-" * 60)
    print(f"Input:            {query}")
    print(f"Matched Question: {resp.get('matched_question')}")
    print(f"Answer:           {resp.get('answer')}")
    print(f"Category:         {resp.get('category')}")
    print(f"Confidence:       {resp.get('confidence')}")
    print(f"Level:            {resp.get('confidence_level')}")
    print(f"Source:           {resp.get('source')}")
    print(f"Time:             {t1-t0:.3f}s")
    
    # Assertions
    if expected_category:
        assert resp["category"] == expected_category, f"Expected {expected_category}, got {resp['category']}"
    if expect_high_conf:
        assert resp["confidence_level"] == "high", f"Expected high confidence, got {resp['confidence_level']}"
    if expect_fallback:
        assert resp["confidence_level"] == "low" and resp["source"] == "fallback", "Expected fallback response"

if __name__ == "__main__":
    print("==================================================")
    print(" AI HR Chatbot V2 - Automated Tests")
    print("==================================================")
    
    print("\n[A] Conversational Tests")
    test_chat("Hello", expected_category="conversation", expect_high_conf=True)
    test_chat("thank you", expected_category="conversation", expect_high_conf=True)
    
    print("\n[B] Exact FAQ matches")
    test_chat("What is the sick leave policy?", expected_category="Sick Leave", expect_high_conf=True)
    test_chat("How is my salary structured?", expected_category="Salary", expect_high_conf=True)
    
    print("\n[C] Natural Variations")
    test_chat("How many days of sick leave can I take per year?", expected_category="Sick Leave")
    test_chat("Can I work remotely or from home?", expected_category="Work From Home")
    
    print("\n[D] Unrelated / Fallback")
    test_chat("What is the capital of France?", expect_fallback=True)
    test_chat("Tell me a joke", expect_fallback=True)
    test_chat("Write me a Python program", expect_fallback=True)
    
    print("\n[E] Contextual Follow-ups")
    # First establish context
    test_chat("How many casual leave days do I get?", expected_category="Casual Leave")
    # Follow up (ambiguous, should lean towards Casual Leave due to session memory)
    test_chat("How many days do I get?", expected_category="Casual Leave")
    
    print("\n==================================================")
    print(" All tests completed successfully!")
    print("==================================================")
