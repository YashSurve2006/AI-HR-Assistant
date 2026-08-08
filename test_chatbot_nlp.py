import urllib.request, json, time, sys
sys.stdout.reconfigure(encoding='utf-8')

# Give Flask time to start
time.sleep(2)

base = 'http://127.0.0.1:5000'

def post_chat(msg):
    body = json.dumps({'message': msg}).encode()
    req = urllib.request.Request(base + '/api/chat', data=body,
          headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return json.loads(r.read())
    except Exception as e:
        return {"error": str(e)}

queries = [
    "How many sick leaves can I take?",
    "How many sick leaves are available?",
    "What is the sick leave policy?",
    "I am sick, how much leave can I take?",
    "What is the company leave policy?",
    "Can I work from home?",
    "When is salary processed?",
    "What is the capital of France?"
]

print("=== NLP Chatbot Matching Test ===")
print("Confidence threshold: 0.30\n")

for q in queries:
    res = post_chat(q)
    print(f"Question:              {q}")
    
    if "error" in res:
        print(f"ERROR:                 {res['error']}\n")
        continue

    conf = res.get('confidence', 0.0)
    cat = res.get('category', 'Unknown')
    ans = res.get('answer', '')
    
    # Check if matched or fallback
    if conf >= 0.30 and cat not in ["Unknown", "Unmatched", "Error"]:
        status = "MATCHED"
    else:
        status = "FALLBACK"
        
    print(f"Matched Category:      {cat}")
    print(f"Similarity/Confidence: {conf:.4f}")
    print(f"Status:                {status}")
    print(f"Answer snippet:        {ans[:80]}...\n")

print("Test complete.")
