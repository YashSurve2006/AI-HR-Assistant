import sys, json
sys.path.insert(0, 'backend')
from app import app
app.testing = True
c = app.test_client()

pdfs = ['test_resume.pdf', 'test_resume_strong.pdf', 'test_resume_ds.pdf', 'test_resume_weak.pdf']
for fname in pdfs:
    try:
        with open(fname, 'rb') as f:
            r = c.post('/api/resume/analyze', data={'file': (f, fname)}, content_type='multipart/form-data')
        d = r.get_json()
        if d.get('success'):
            score = d['score']
            skills = d['skills']
            bd = d['score_breakdown']
            total = sum(bd.values())
            print(f"{fname}:")
            print(f"  score={score}  skills={d['skill_count']}  text_len={d['text_length']}")
            print(f"  first skills: {skills[:5]}")
            print(f"  breakdown: {bd}")
            print(f"  sum(breakdown)={total} == score={score}: {'OK' if total == score else 'MISMATCH!'}")
        else:
            print(f"{fname}: FAILED - {d.get('error')}")
    except Exception as ex:
        print(f"{fname}: EXCEPTION - {ex}")
    print()

# Also test recommendations on strong resume
print("=== JOB RECOMMENDATIONS (test_resume_strong.pdf) ===")
with open('test_resume_strong.pdf', 'rb') as f:
    r = c.post('/api/resume/recommend', data={'file': (f, 'test_resume_strong.pdf')}, content_type='multipart/form-data')
d = r.get_json()
if d.get('success'):
    recs = d['recommendations']
    print(f"Total recommendations: {len(recs)}")
    for rec in recs:
        print(f"  [{rec['title']}] dept={rec['department']} loc={rec['location']}")
        print(f"    sim={rec['similarity']}  match_pct={rec['match_percentage']}%")
        print(f"    matched={rec['matched_skills'][:3]}  missing={rec['missing_skills'][:3]}")
else:
    print("FAILED:", d.get('error'))
