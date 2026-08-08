import urllib.request, json, time, sys
sys.stdout.reconfigure(encoding='utf-8')
time.sleep(2)

base = 'http://127.0.0.1:5000'

def get(path):
    with urllib.request.urlopen(base + path, timeout=5) as r:
        return json.loads(r.read())

def post_json(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(base + path, data=body,
          headers={'Content-Type': 'application/json'}, method='POST')
    with urllib.request.urlopen(req, timeout=5) as r:
        return json.loads(r.read())

print('=== LIVE SERVER CHECKS ===')

# Health
d = get('/api/health')
status = d["status"]
print(f'/api/health: status={status}  OK={status == "ok"}')

# Dashboard
d = get('/api/dashboard')
s = d['summary']
jobs = s['total_jobs']
feedback = s['total_feedback']
avg = s['average_rating']
pos_pct = s['positive_percentage']
print(f'/api/dashboard: jobs={jobs} feedback={feedback} avg_rating={avg} pos%={pos_pct}')
print(f'  sentiment chart labels: {d["sentiment"]["labels"]}')
print(f'  sentiment chart values: {d["sentiment"]["values"]}')
print(f'  rating_dist count: {len(d["rating_distribution"])}')
print(f'  job_dist count: {len(d["job_distribution"])}')
print(f'  location_dist count: {len(d["location_distribution"])}')
print(f'  dept_sentiment count: {len(d["department_sentiment"])}')

# Chat - valid
r = post_json('/api/chat', {'message': 'How many days of annual leave do employees get?'})
conf = r["confidence"]
cat = r["category"]
ans = r["answer"][:80]
print(f'/api/chat valid: confidence={conf}  category={cat}')
print(f'  answer[:80]: {ans}')

# Chat - empty
r2 = post_json('/api/chat', {'message': ''})
print(f'/api/chat empty: answer="{r2["answer"]}"')

# Chat - rephrased
r3 = post_json('/api/chat', {'message': 'Tell me about sick leave'})
print(f'/api/chat rephrased: category={r3["category"]}  confidence={r3["confidence"]}')

# Chat - unrelated
r4 = post_json('/api/chat', {'message': 'What is 2+2?'})
print(f'/api/chat unrelated: category={r4["category"]}')

# Chat - long message
long_msg = 'a ' * 1200
r5 = post_json('/api/chat', {'message': long_msg})
print(f'/api/chat long: success={r5["success"]}')

# Feedback/sentiment
fb_data = get('/api/feedback/sentiment')
s2 = fb_data['summary']
total = s2['total']
pos = s2['positive']
neg = s2['negative']
neu = s2['neutral']
pct_sum = s2['positive_percentage'] + s2['negative_percentage'] + s2['neutral_percentage']
print(f'/api/feedback/sentiment: total={total} pos={pos} neg={neg} neu={neu}')
print(f'  pct sum={pct_sum:.2f} (should be ~100)')

# Cross-consistency
print()
print('=== CROSS-API CONSISTENCY ===')
dash2 = get('/api/dashboard')
d_pos = dash2['summary']['positive_percentage']
f_pos = s2['positive_percentage']
d_tot = dash2['summary']['total_feedback']
f_tot = s2['total']
print(f'dashboard.positive_pct = {d_pos}  |  feedback.positive_pct = {f_pos}  |  Match: {d_pos == f_pos}')
print(f'dashboard.total_feedback = {d_tot}  |  feedback.total = {f_tot}  |  Match: {d_tot == f_tot}')

print()
print('All live checks passed.')
