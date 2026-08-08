import sys
sys.path.insert(0, 'backend')
import chatbot

queries = [
    "How many sick leaves can I take?",
    "how many sick leaves can i take",
    "HOW MANY SICK LEAVES CAN I TAKE",
    "how many sick leaves can i take!!!",
    "how many sick leavs can i take",
    "how much sick leave am i allowed",
    "HELLO!!!",
    "What is the capital of France?"
]

for q in queries:
    res = chatbot.get_chatbot_response(q)
    print(f"Q: {q:<42} | Conf: {res['confidence']:<6} | Level: {res['confidence_level']:<6} | Source: {res['source']:<12} | Matched: {res['matched_question']}")
