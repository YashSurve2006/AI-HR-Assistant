import time
import requests
import subprocess
import os
import json
import sys

def run_tests():
    print("Testing /api/health")
    try:
        resp = requests.get("http://127.0.0.1:5000/api/health")
        print("Health Check Response:", resp.json())
        assert resp.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return
        
    # Test Cases for /api/chat
    test_cases = [
        ("A question very similar to an FAQ", "What is the company leave policy?"),
        ("A differently worded HR question", "tell me about sick leaves and if I need a doctors note"),
        ("An unrelated question", "Who won the football world cup?"),
        ("An empty message", ""),
        ("A question from another HR category", "Can I work from home on Mondays?")
    ]
    
    for desc, msg in test_cases:
        print(f"\n--- Testing: {desc} ---")
        print(f"Message: '{msg}'")
        resp = requests.post("http://127.0.0.1:5000/api/chat", json={"message": msg})
        print("Response:", json.dumps(resp.json(), indent=2))
        assert resp.status_code == 200

if __name__ == "__main__":
    run_tests()
