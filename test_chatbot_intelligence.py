import sys
import time
import pandas as pd

sys.path.insert(0, 'backend')
import chatbot

def run_test_suite():
    print("=" * 80)
    print(" AI HR CHATBOT V2 INTELLIGENCE & ROBUSTNESS TEST SUITE")
    print("=" * 80)
    
    test_cases = [
        # Category A: Exact question
        {"group": "A. Exact Question", "query": "What is the sick leave policy?"},
        
        # Category B: Lowercase version
        {"group": "B. Lowercase Version", "query": "what is the sick leave policy"},
        
        # Category C: Uppercase version
        {"group": "C. Uppercase Version", "query": "WHAT IS THE SICK LEAVE POLICY"},
        
        # Category D: No punctuation
        {"group": "D. No Punctuation", "query": "What is the sick leave policy"},
        
        # Category E: Excess punctuation
        {"group": "E. Excess Punctuation", "query": "What is the sick leave policy???!!!"},
        
        # Category F: Extra whitespace
        {"group": "F. Extra Whitespace", "query": "   what   is   the   sick   leave   policy   "},
        
        # Category G: Minor typo
        {"group": "G. Minor Typo", "query": "whats the sick leav polic"},
        
        # Category H: Singular/Plural variation
        {"group": "H. Singular/Plural Variation", "query": "how many sick leave can i take"},
        
        # Category I: Natural paraphrase
        {"group": "I. Natural Paraphrase", "query": "how much sick leave am i allowed to take per year"},
        
        # Category J: Short query
        {"group": "J. Short Query", "query": "sick leave policy?"},
        
        # Category K: Unrelated query
        {"group": "K. Unrelated Query 1", "query": "What is the capital of India?", "expect_fallback": True},
        {"group": "K. Unrelated Query 2", "query": "Write a Python script to sort a list.", "expect_fallback": True},
        {"group": "K. Unrelated Query 3", "query": "Who won the cricket world cup?", "expect_fallback": True},
        
        # Category L: Greeting
        {"group": "L. Greeting 1", "query": "HELLO!!!"},
        {"group": "L. Greeting 2", "query": "good morning"},
        
        # Category M: Thank-you message
        {"group": "M. Thank-you Message", "query": "thank you very much!"},
    ]

    passed_count = 0
    total_count = len(test_cases)
    
    for tc in test_cases:
        t0 = time.time()
        res = chatbot.get_chatbot_response(tc["query"])
        t1 = time.time()
        
        group = tc["group"]
        q = tc["query"]
        conf = res["confidence"]
        level = res["confidence_level"]
        source = res["source"]
        matched_q = res["matched_question"]
        ans = res["answer"]
        
        print(f"\n[{group}]")
        print(f"  Input        : '{q}'")
        print(f"  Confidence   : {conf:.4f} ({level}) | Source: {source}")
        print(f"  Matched FAQ  : {matched_q}")
        print(f"  Answer       : {ans[:90]}...")
        print(f"  Latency      : {(t1 - t0) * 1000:.2f} ms")
        
        if tc.get("expect_fallback"):
            assert level == "low" and source == "fallback", f"Expected fallback, got {level} ({source})"
        
        passed_count += 1

    # Category N: Contextual Follow-up Test
    print("\n[N. Contextual Follow-up Test]")
    session_id = "test_intelligence_sess_1"
    
    # Message 1
    q1 = "How many casual leave days do I get?"
    res1 = chatbot.get_chatbot_response(q1, session_id=session_id)
    print(f"  Msg 1 Input  : '{q1}'")
    print(f"  Msg 1 Matched: {res1['matched_question']} (Cat: {res1['category']})")
    
    # Message 2 (Follow-up)
    q2 = "How many days?"
    res2 = chatbot.get_chatbot_response(q2, session_id=session_id)
    print(f"  Msg 2 Input  : '{q2}' (Follow-up)")
    print(f"  Msg 2 Matched: {res2['matched_question']} (Cat: {res2['category']}, Conf: {res2['confidence']:.4f})")
    
    assert res2['category'] == 'Casual Leave', f"Expected Casual Leave context, got {res2['category']}"
    total_count += 1
    passed_count += 1

    print("\n" + "=" * 80)
    print(f" RESULTS: {passed_count}/{total_count} Intelligence Test Cases Passed!")
    print("=" * 80)

if __name__ == "__main__":
    run_test_suite()
