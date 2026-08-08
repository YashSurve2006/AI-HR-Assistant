"""Test the advanced resume against all backend endpoints."""
import sys, json
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, 'backend')
from app import app

app.testing = True
c = app.test_client()

RESUME = 'uploads/advanced_test_resume.pdf'

print("=" * 70)
print("  ADVANCED RESUME TEST: uploads/advanced_test_resume.pdf")
print("=" * 70)

# ── 1. Text extraction verification ─────────────────────────────
import resume_analyzer
text = resume_analyzer.extract_text_from_pdf(RESUME)
print(f"\n[1] TEXT EXTRACTION")
print(f"    Characters extracted: {len(text)}")
print(f"    First 200 chars:")
print(f"    {text[:200]}...")
print(f"    Last 200 chars:")
print(f"    ...{text[-200:]}")

# ── 2. POST /api/resume/analyze ─────────────────────────────────
print(f"\n{'=' * 70}")
print("[2] POST /api/resume/analyze")
print("=" * 70)

with open(RESUME, 'rb') as f:
    r = c.post('/api/resume/analyze',
               data={'file': (f, 'advanced_test_resume.pdf')},
               content_type='multipart/form-data')

d = r.get_json()
print(f"    HTTP status:  {r.status_code}")
print(f"    success:      {d.get('success')}")
print(f"    filename:     {d.get('filename')}")
print(f"    text_length:  {d.get('text_length')}")
print(f"    skill_count:  {d.get('skill_count')}")
print()

print("    RESUME SCORE: {}/100".format(d.get('score')))
print()

bd = d.get('score_breakdown', {})
print("    SCORE BREAKDOWN:")
total = 0
maxes = {'skills': 25, 'experience': 25, 'education': 20, 'projects': 15, 'content_quality': 15}
for k, v in bd.items():
    mx = maxes.get(k, '?')
    pct = round(v / mx * 100) if mx != '?' else '?'
    print(f"      {k:20s} = {v:3d} / {mx}   ({pct}%)")
    total += v
print(f"      {'TOTAL':20s} = {total:3d} / 100")
print(f"      sum == score: {total == d.get('score')}")
print()

skills = d.get('skills', [])
print(f"    EXTRACTED SKILLS ({len(skills)}):")
for i in range(0, len(skills), 6):
    row = skills[i:i+6]
    print(f"      {', '.join(row)}")
print()

# Check which expected skills were found
expected = [
    'Python', 'Java', 'JavaScript', 'TypeScript', 'React', 'Node.js',
    'Express', 'Flask', 'Django', 'HTML', 'CSS', 'SQL', 'MySQL',
    'PostgreSQL', 'MongoDB', 'Oracle', 'Pandas', 'NumPy', 'Scikit-learn',
    'Machine Learning', 'NLP', 'Git', 'Docker', 'AWS', 'Azure',
    'Linux', 'Power BI', 'Tableau', 'C++', 'Go', 'Rust',
    'Cisco', 'Networking', 'Excel'
]
# The SKILLS_DB from resume_analyzer
db_skills = set(s.lower() for s in resume_analyzer.SKILLS_DB)
found = set(s.lower() for s in skills)
expected_in_db = [s for s in expected if s.lower() in db_skills]
missed = [s for s in expected_in_db if s.lower() not in found]
print(f"    EXPECTED SKILLS IN DB: {len(expected_in_db)}")
print(f"    FOUND:                 {len([s for s in expected_in_db if s.lower() in found])}")
if missed:
    print(f"    MISSED:                {missed}")
else:
    print(f"    MISSED:                None (all expected skills detected!)")

# ── 3. POST /api/resume/recommend ────────────────────────────────
print(f"\n{'=' * 70}")
print("[3] POST /api/resume/recommend")
print("=" * 70)

with open(RESUME, 'rb') as f:
    r2 = c.post('/api/resume/recommend',
                data={'file': (f, 'advanced_test_resume.pdf')},
                content_type='multipart/form-data')

d2 = r2.get_json()
print(f"    HTTP status: {r2.status_code}")
print(f"    success:     {d2.get('success')}")

recs = d2.get('recommendations', [])
print(f"    Total recommendations: {len(recs)}")
print()

for i, rec in enumerate(recs, 1):
    sim = rec.get('similarity', 0)
    mpct = rec.get('match_percentage', 0)
    title = rec.get('title', '?')
    dept = rec.get('department', '?')
    loc = rec.get('location', '?')
    matched = rec.get('matched_skills', [])
    missing = rec.get('missing_skills', [])

    print(f"    --- Recommendation #{i} ---")
    print(f"    Title:            {title}")
    print(f"    Department:       {dept}")
    print(f"    Location:         {loc}")
    print(f"    TF-IDF Similarity: {sim:.4f}  ({sim*100:.1f}%)")
    print(f"    Skill Match:      {mpct}%")
    print(f"    Matched Skills:   {matched}")
    print(f"    Missing Skills:   {missing}")
    print()

# ── Summary ──────────────────────────────────────────────────────
print("=" * 70)
print("  SUMMARY")
print("=" * 70)
print(f"  Text extracted:       {d.get('text_length')} characters")
print(f"  Skills detected:      {d.get('skill_count')}")
print(f"  Resume score:         {d.get('score')}/100")
print(f"  Score breakdown sum:  {total} (match: {total == d.get('score')})")
print(f"  Job recs returned:    {len(recs)}")
print(f"  Top match:            {recs[0]['title'] if recs else 'N/A'} ({recs[0]['similarity']*100:.1f}% sim)")
print(f"  No NaN in analyze:    {'NaN' not in json.dumps(d)}")
print(f"  No NaN in recommend:  {'NaN' not in json.dumps(d2)}")
print("=" * 70)
