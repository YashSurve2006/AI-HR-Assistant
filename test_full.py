"""
Full integration test for AI HR Assistant backend.
Tests all endpoints with valid, invalid, empty and malformed data.
"""
import sys, os, json, io
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app
app.testing = True
client = app.test_client()

results = []

def test(name, passed, detail=""):
    results.append((name, passed, detail))
    status = "PASS" if passed else "FAIL"
    msg = f"  [{status}]  {name}"
    if detail:
        msg += f"  ({detail})"
    print(msg)

def jget(url):
    r = client.get(url)
    return r, r.get_json()

def jpost(url, json_data=None, data=None):
    if json_data is not None:
        r = client.post(url, json=json_data)
    else:
        r = client.post(url, data=data, content_type='multipart/form-data')
    return r, r.get_json()

# Minimal valid PDF bytes
VALID_PDF = (
    b"%PDF-1.4\n1 0 obj\n<</Type /Catalog /Pages 2 0 R>>\nendobj\n"
    b"2 0 obj\n<</Type /Pages /Kids [3 0 R] /Count 1>>\nendobj\n"
    b"3 0 obj\n<</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]"
    b"/Contents 4 0 R /Resources <</Font <</F1 5 0 R>>>>>>\nendobj\n"
    b"4 0 obj\n<</Length 70>>\nstream\n"
    b"BT /F1 12 Tf 72 720 Td (Python Java SQL Flask Machine Learning Git Docker) Tj ET\n"
    b"endstream\nendobj\n"
    b"5 0 obj\n<</Type /Font /Subtype /Type1 /BaseFont /Helvetica>>\nendobj\n"
    b"xref\n0 6\n0000000000 65535 f \n"
    b"trailer\n<</Size 6 /Root 1 0 R>>\nstartxref\n9\n%%EOF\n"
)

print()
print("=" * 60)
print("  AI HR Assistant - Full Integration Test")
print("=" * 60)

# ─────────────────────────────────────────────────────────────────────
# 1. GET /api/health
# ─────────────────────────────────────────────────────────────────────
print("\n-- /api/health --")
r, d = jget('/api/health')
test("GET /api/health -> 200",       r.status_code == 200)
test("health.status == ok",          d.get('status') == 'ok')
test("health.message present",       bool(d.get('message')))

# ─────────────────────────────────────────────────────────────────────
# 2. POST /api/chat
# ─────────────────────────────────────────────────────────────────────
print("\n-- /api/chat --")
r, d = jpost('/api/chat', json_data={'message': 'What is the leave policy?'})
test("chat valid -> 200",            r.status_code == 200)
test("chat.success == True",         d.get('success') == True)
test("chat.answer present",          bool(d.get('answer')))
test("chat.confidence is float",     isinstance(d.get('confidence'), float))
test("chat.category present",        bool(d.get('category')))

r, d = jpost('/api/chat', json_data={'message': ''})
test("chat empty msg -> 200",        r.status_code == 200)
test("chat empty: answer present",   bool(d.get('answer')))

r, d = jpost('/api/chat', json_data={})
test("chat no field -> 200",         r.status_code == 200)
test("chat no field: answer present",bool(d.get('answer')))

r, d = jpost('/api/chat', json_data={'message': '!@#$%^&*()'})
test("chat junk msg -> no crash",    r.status_code == 200 and d.get('success') == True)

r = client.post('/api/chat', data='not json', content_type='text/plain')
test("chat non-JSON -> no crash",    r.status_code in (200, 400, 415))

# ─────────────────────────────────────────────────────────────────────
# 3. POST /api/resume/analyze
# ─────────────────────────────────────────────────────────────────────
print("\n-- /api/resume/analyze --")
r, d = jpost('/api/resume/analyze', data={})
test("analyze no file -> 400",       r.status_code == 400)
test("analyze: error msg present",   bool(d.get('error')))

r, d = jpost('/api/resume/analyze', data={'file': (io.BytesIO(b'hello'), 'resume.txt')})
test("analyze .txt -> 400",          r.status_code == 400)

r, d = jpost('/api/resume/analyze', data={'file': (io.BytesIO(b'NOT A PDF'), 'bad.pdf')})
test("analyze corrupt PDF -> no 500 crash", r.status_code in (200, 400))
test("analyze corrupt: has success", 'success' in (d or {}))

r, d = jpost('/api/resume/analyze', data={'file': (io.BytesIO(VALID_PDF), 'test_resume.pdf')})
test("analyze valid PDF -> 200 or 400", r.status_code in (200, 400))
if r.status_code == 200:
    test("analyze: success True",    d.get('success') == True)
    test("analyze: score is int",    isinstance(d.get('score'), int))
    test("analyze: skills is list",  isinstance(d.get('skills'), list))
    test("analyze: breakdown dict",  isinstance(d.get('score_breakdown'), dict))
    test("analyze: filename present",bool(d.get('filename')))
    test("analyze: score 0-100",     0 <= d.get('score', -1) <= 100, f"score={d.get('score')}")
    test("analyze: no NaN in JSON",  'NaN' not in json.dumps(d))
    bd = d.get('score_breakdown', {})
    for k in ['skills','experience','education','projects','content_quality']:
        test(f"analyze breakdown.{k} present", k in bd)
else:
    test("analyze: error msg",       bool(d.get('error')))

# ─────────────────────────────────────────────────────────────────────
# 4. POST /api/resume/recommend
# ─────────────────────────────────────────────────────────────────────
print("\n-- /api/resume/recommend --")
r, d = jpost('/api/resume/recommend', data={})
test("recommend no file -> 400",     r.status_code == 400)

r, d = jpost('/api/resume/recommend', data={'file': (io.BytesIO(b'hello'), 'bad.doc')})
test("recommend .doc -> 400",        r.status_code == 400)

r, d = jpost('/api/resume/recommend', data={'file': (io.BytesIO(VALID_PDF), 'test.pdf')})
test("recommend valid PDF -> 200 or 400", r.status_code in (200, 400))
if r.status_code == 200:
    test("recommend: success True",  d.get('success') == True)
    recs = d.get('recommendations', [])
    test("recommend: recs is list",  isinstance(recs, list))
    test("recommend: no NaN",        'NaN' not in json.dumps(d))
    if recs:
        rec = recs[0]
        test("rec[0]: has title",        bool(rec.get('title')))
        test("rec[0]: has similarity",   isinstance(rec.get('similarity'), float))
        test("rec[0]: matched_skills list", isinstance(rec.get('matched_skills'), list))
        test("rec[0]: missing_skills list", isinstance(rec.get('missing_skills'), list))
        test("rec[0]: match_pct 0-100", 0 <= rec.get('match_percentage', -1) <= 100)

# ─────────────────────────────────────────────────────────────────────
# 5. GET /api/feedback/sentiment
# ─────────────────────────────────────────────────────────────────────
print("\n-- /api/feedback/sentiment --")
r, d = jget('/api/feedback/sentiment')
test("GET /api/feedback/sentiment -> 200", r.status_code == 200)
test("sentiment.success == True",    d.get('success') == True)
test("sentiment.summary present",    isinstance(d.get('summary'), dict))
test("sentiment.feedback is list",   isinstance(d.get('feedback'), list))
test("sentiment: no NaN",           'NaN' not in json.dumps(d))

s = d.get('summary', {})
test("summary has total",            'total' in s)
test("summary total > 0",            s.get('total', 0) > 0)
pct = s.get('positive_percentage',0) + s.get('negative_percentage',0) + s.get('neutral_percentage',0)
test("pct sums ~100%",              abs(pct - 100.0) < 1.0, f"sum={pct:.2f}")

fb = d.get('feedback', [])
if fb:
    for k in ['employee_name','department','rating','feedback','sentiment','polarity']:
        test(f"feedback[0].{k} present", k in fb[0])

# ─────────────────────────────────────────────────────────────────────
# 6. GET /api/dashboard
# ─────────────────────────────────────────────────────────────────────
print("\n-- /api/dashboard --")
r, d = jget('/api/dashboard')
test("GET /api/dashboard -> 200",    r.status_code == 200)
test("dashboard.success == True",    d.get('success') == True)
test("dashboard: no NaN",           'NaN' not in json.dumps(d))

summary = d.get('summary', {})
for k in ['total_jobs','total_feedback','average_rating','positive_percentage','positive','negative','neutral']:
    test(f"summary.{k} present",     k in summary)

snt = d.get('sentiment', {})
test("sentiment chart labels",       isinstance(snt.get('labels'), list) and len(snt.get('labels',[])) == 3)
test("sentiment chart values",       isinstance(snt.get('values'), list) and len(snt.get('values',[])) == 3)

rd = d.get('rating_distribution', [])
test("rating_distribution has 5",   len(rd) == 5)

jd = d.get('job_distribution', [])
test("job_distribution is list",     isinstance(jd, list) and len(jd) > 0)
if jd:
    test("job_dist entry has dept",  'department' in jd[0])
    test("job_dist entry has count", isinstance(jd[0].get('count'), int))

ld = d.get('location_distribution', [])
test("location_distribution > 0",   len(ld) > 0)

ds = d.get('department_sentiment', [])
test("dept_sentiment is list",       isinstance(ds, list))
if ds:
    for k in ['department','positive','negative','neutral']:
        test(f"dept_sentiment[0].{k}", k in ds[0])

# ─────────────────────────────────────────────────────────────────────
# Data Consistency Checks
# ─────────────────────────────────────────────────────────────────────
print("\n-- Data Consistency --")
# Cross-check dashboard vs feedback/sentiment
r2, d2 = jget('/api/feedback/sentiment')
dash_pos = summary.get('positive_percentage', -1)
fb_pos   = d2.get('summary', {}).get('positive_percentage', -2)
test("dashboard pos% == feedback pos%", abs(dash_pos - fb_pos) < 0.01, f"{dash_pos} vs {fb_pos}")

dash_total  = summary.get('total_feedback', -1)
fb_total    = d2.get('summary', {}).get('total', -2)
test("dashboard total_feedback == feedback total", dash_total == fb_total, f"{dash_total} vs {fb_total}")

# ─────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────
print()
print("=" * 60)
total  = len(results)
passed = sum(1 for _, p, _ in results if p)
failed = total - passed
print(f"  RESULTS: {passed}/{total} passed  |  {failed} failed")
print("=" * 60)
if failed:
    print("\nFailed tests:")
    for name, p, detail in results:
        if not p:
            print(f"  [FAIL]  {name}" + (f"  ({detail})" if detail else ""))
sys.exit(0 if failed == 0 else 1)
