"""
Test script for verifying Centralized AI Chatbot + In-Chat Resume Analysis + Follow-ups.
"""
import sys, os, io, json, zipfile
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app
import chatbot
import resume_analyzer

app.testing = True
client = app.test_client()

def run_tests():
    print("=" * 70)
    print("  RUNNING CENTRALIZED AI CHATBOT + IN-CHAT RESUME NLP TESTS")
    print("=" * 70)

    # 1. Health check
    print("\n[1] GET /api/health")
    r = client.get('/api/health')
    assert r.status_code == 200, f"Health check failed: {r.status_code}"
    print("    PASSED -> Backend is healthy:", r.get_json())

    # 2. Empty / Greeting Chat queries
    print("\n[2] POST /api/chat (Greetings & Empty Prompts)")
    test_session = "test_session_central_1"
    
    # 2a. Greeting
    r = client.post('/api/chat', json={"message": "Hello!", "session_id": test_session})
    d = r.get_json()
    assert d.get("success"), "Greeting failed"
    print("    Greeting answer:", d.get("answer")[:60] + "...")

    # 2b. 5 Quick-start prompts (no resume in session yet)
    quick_prompts = [
        "📄 Analyze my Resume",
        "🎯 Check my ATS Score",
        "💼 Find suitable jobs",
        "🎤 Prepare for an Interview",
        "🚀 What skills should I learn?"
    ]
    for qp in quick_prompts:
        r = client.post('/api/chat', json={"message": qp, "session_id": test_session})
        d = r.get_json()
        assert d.get("success"), f"Quick prompt failed: {qp}"
        print(f"    Quick Prompt '{qp}': Category={d.get('category')} | Answer len={len(d.get('answer'))}")

    # 3. Create a test DOCX resume in-memory
    print("\n[3] In-Memory DOCX Creation & Parsing Test")
    docx_buffer = io.BytesIO()
    with zipfile.ZipFile(docx_buffer, 'w') as z:
        doc_xml = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
        <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
          <w:body>
            <w:p><w:r><w:t>Alex Morgan - Senior Software Engineer</w:t></w:r></w:p>
            <w:p><w:r><w:t>Summary: 5+ years experience building scalable web applications.</w:t></w:r></w:p>
            <w:p><w:r><w:t>Technical Skills: Python, React, JavaScript, Node.js, SQL, Docker, AWS, Git, REST API.</w:t></w:r></w:p>
            <w:p><w:r><w:t>Experience: Senior Developer at TechCorp (2021-Present). Led architecture of microservices handling 1M daily requests.</w:t></w:r></w:p>
            <w:p><w:r><w:t>Education: Bachelor of Science in Computer Science, University of California, GPA 3.8.</w:t></w:r></w:p>
            <w:p><w:r><w:t>Projects: Developed open-source analytics engine using Flask and Scikit-learn.</w:t></w:r></w:p>
          </w:body>
        </w:document>"""
        z.writestr('word/document.xml', doc_xml)
    docx_bytes = docx_buffer.getvalue()

    # Save to uploads for test
    os.makedirs('uploads', exist_ok=True)
    test_docx_path = 'uploads/test_generated_resume.docx'
    with open(test_docx_path, 'wb') as f:
        f.write(docx_bytes)

    extracted_docx_text = resume_analyzer.extract_text_from_file(test_docx_path)
    assert "Alex Morgan" in extracted_docx_text, "DOCX extraction failed to find candidate name"
    print("    DOCX Text Extracted successfully:", len(extracted_docx_text), "characters")

    # 4. In-Chat Resume Upload & Analysis via /api/chat
    print("\n[4] POST /api/chat with Attached Resume (.docx)")
    r = client.post('/api/chat',
                    data={
                        'file': (io.BytesIO(docx_bytes), 'alex_morgan_resume.docx'),
                        'message': 'Please analyze my resume and evaluate my ATS score',
                        'session_id': test_session
                    },
                    content_type='multipart/form-data')
    d = r.get_json()
    assert d.get("success"), f"In-chat upload failed: {d}"
    assert "resume_analysis" in d, "Expected resume_analysis in response"
    res_analysis = d["resume_analysis"]
    print("    ATS Score:", res_analysis.get("score"), "/ 100")
    print("    Extracted Skills:", res_analysis.get("skills"))
    print("    Strengths:", res_analysis.get("strengths"))
    print("    Weaknesses:", res_analysis.get("weaknesses"))
    print("    Missing Skills:", res_analysis.get("missing_skills"))
    print("    Suggestions:", res_analysis.get("suggestions"))
    print("    Matched Roles Count:", len(res_analysis.get("recommendations", [])))

    # 5. Contextual Follow-up Queries with Active Session Memory
    print("\n[5] Contextual Follow-Up Queries (Active Session Context)")
    follow_ups = [
        "What are my strengths and weaknesses?",
        "How can I improve my ATS score to 95+?",
        "What jobs match my profile?",
        "Prepare for an interview for my skills",
        "What skills should I learn next?"
    ]
    for fu in follow_ups:
        r = client.post('/api/chat', json={"message": fu, "session_id": test_session})
        d = r.get_json()
        assert d.get("success"), f"Follow up failed: {fu}"
        assert d.get("source") == "resume_memory", f"Expected resume_memory source, got {d.get('source')}"
        print(f"\n    Q: '{fu}'")
        print(f"    A: {d.get('answer')[:120]}...")

    # 6. Existing PDF Analysis with test PDF
    print("\n[6] POST /api/resume/analyze with PDF")
    test_pdf = 'uploads/advanced_test_resume.pdf'
    if os.path.exists(test_pdf):
        with open(test_pdf, 'rb') as f:
            r = client.post('/api/resume/analyze',
                            data={'file': (f, 'advanced_test_resume.pdf'), 'session_id': 'pdf_sess'},
                            content_type='multipart/form-data')
            d = r.get_json()
            assert d.get("success"), f"PDF analyze failed: {d}"
            print("    PDF Score:", d.get("score"), "Skills:", len(d.get("skills", [])))

    # 7. Job Directory & Analytics endpoints
    print("\n[7] GET /api/jobs & GET /api/dashboard & GET /api/feedback/sentiment")
    r_jobs = client.get('/api/jobs')
    assert r_jobs.status_code == 200 and r_jobs.get_json().get("success"), "GET /api/jobs failed"
    print("    Jobs count:", len(r_jobs.get_json().get("jobs", [])))

    r_dash = client.get('/api/dashboard')
    assert r_dash.status_code == 200 and r_dash.get_json().get("success"), "GET /api/dashboard failed"
    print("    Dashboard summary:", r_dash.get_json().get("summary"))

    r_feed = client.get('/api/feedback/sentiment')
    assert r_feed.status_code == 200 and r_feed.get_json().get("success"), "GET /api/feedback/sentiment failed"
    print("    Feedback count:", len(r_feed.get_json().get("feedback", [])))

    print("\n" + "=" * 70)
    print("  ALL CENTRALIZED CHATBOT + RESUME NLP TESTS PASSED SUCCESSFULLY!")
    print("=" * 70)

if __name__ == "__main__":
    run_tests()
