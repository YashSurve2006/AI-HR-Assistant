import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def sep(label):
    print(f"\n{'='*50}")
    print(f"  {label}")
    print('='*50)

def test_health():
    sep("GET /api/health")
    r = requests.get(f"{BASE_URL}/api/health")
    print(r.json())

def test_chat():
    sep("POST /api/chat")
    r = requests.post(f"{BASE_URL}/api/chat", json={"message": "What is the leave policy?"})
    data = r.json()
    print("success:", data.get("success"))
    print("category:", data.get("category"))

def test_feedback_sentiment():
    sep("GET /api/feedback/sentiment")
    r = requests.get(f"{BASE_URL}/api/feedback/sentiment")
    data = r.json()
    print("success:", data.get("success"))
    print("summary:", data.get("summary"))

def test_dashboard():
    sep("GET /api/dashboard")
    r = requests.get(f"{BASE_URL}/api/dashboard")
    data = r.json()
    print("success:", data.get("success"))
    print()
    print("[summary]")
    print(json.dumps(data.get("summary"), indent=2))
    print()
    print("[sentiment chart]")
    print(json.dumps(data.get("sentiment"), indent=2))
    print()
    print("[rating_distribution]")
    for item in data.get("rating_distribution", []):
        print(f"  Rating {item['rating']}: {item['count']} feedback(s)")
    print()
    print("[job_distribution]")
    for item in data.get("job_distribution", []):
        print(f"  {item['department']}: {item['count']} job(s)")
    print()
    print("[location_distribution]")
    for item in data.get("location_distribution", []):
        print(f"  {item['location']}: {item['count']} job(s)")
    print()
    print("[department_sentiment (first 3)]")
    for item in data.get("department_sentiment", [])[:3]:
        print(f"  {item['department']}: +{item['positive']} / -{item['negative']} / ~{item['neutral']}")

if __name__ == "__main__":
    test_health()
    test_chat()
    test_feedback_sentiment()
    test_dashboard()
    print("\nAll tests completed.")
