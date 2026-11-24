"""Question bank + one-year schedule for "Guess the Surah" reels.
Every question is built from the Qur'an data itself, so every answer can be checked by code (see verify())."""
import json, os, random, re, datetime
from collections import defaultdict

Q = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'quran_en.json'), encoding='utf8'))
S = {c['id']: c for c in Q}
FAMOUS = set(range(78, 115)) | {1, 2, 3, 12, 18, 19, 36, 55, 56, 67, 71}
ORD = {1: 'pehli', 2: 'doosri', 3: 'teesri'}

def norm(t):
    t = re.sub(r'[ً-ٰٟۖ-ۭـ]', '', t)
    t = re.sub('[ٱأإآءؤئا]', '', t).replace('ى', 'ي').replace('ة', 'ه')
    return re.sub(r'\s+', ' ', re.sub(r'[^ء-ي ]', ' ', t)).strip()

def nwords(t): return len(norm(t).split())

# ayah text -> set of surahs where that exact (normalised) text occurs; used to drop ambiguous ayaat
WHERE = defaultdict(set)
for c in Q:
    for v in c['verses']:
        WHERE[norm(v['text'])].add(c['id'])
def unique_ayah(sid, a):
    return len(WHERE[norm(S[sid]['verses'][a - 1]['text'])]) == 1

def short(t): return 3 <= nwords(t) <= 9 and len(t) <= 72

def near(sid, span=25): return [x for x in range(max(1, sid - span), min(114, sid + span) + 1) if x != sid]

# ---------------- pools ----------------
POOL = defaultdict(list)
for c in Q:
    sid = c['id']; vs = c['verses']; n = len(vs)
    if sid != 1 and short(vs[0]['text']) and unique_ayah(sid, 1):
        POOL['first'].append((sid, 1))
    if n > 1 and short(vs[-1]['text']) and unique_ayah(sid, n):
        POOL['last'].append((sid, n))
    if sid in FAMOUS or sid >= 50:
        for a in range(2, n):
            if short(vs[a - 1]['text']) and unique_ayah(sid, a):
                POOL['ayah'].append((sid, a))
    if c['total_verses'] <= 60:
        POOL['count'].append((sid, 0))
    POOL['meaning'].append((sid, 0))
    POOL['number'].append((sid, 0))

def make(kind, sid, a, rnd):
    c = S[sid]; name = c['transliteration']
    if kind in ('first', 'last', 'ayah'):
        others = rnd.sample([x for x in near(sid) if sid not in WHERE[norm(c['verses'][a - 1]['text'])] or x != sid], 3)
        q = {'first': 'Yeh kis surah ki pehli ayat hai?', 'last': 'Yeh kis surah ki aakhri ayat hai?', 'ayah': 'Yeh ayat kis surah ki hai?'}[kind]
        ar = re.sub(r'\s*[\u06de\u06e9]\s*', ' ', c['verses'][a - 1]['text'].replace('\u065e', '\u064c')).strip(); ref = f'Surah {name} · {sid}:{a}'
    elif kind == 'count':
        n = c['total_verses']
        others = rnd.sample([x for x in near(sid, 40) if S[x]['total_verses'] != n], 3)
        q = f'In mein se kis surah mein {n} ayaat hain?'; ar = ''; ref = f'Surah {name} · {n} ayaat'
    elif kind == 'meaning':
        others = rnd.sample([x for x in near(sid, 40) if S[x]['translation'] != c['translation']], 3)
        q = f"Kis surah ke naam ka matlab hai \"{c['translation']}\"?"; ar = ''; ref = f"Surah {name} = {c['translation']}"
    else:  # number
        others = rnd.sample(near(sid, 6), 3)
        q = f"Qur'an ki surah number {sid} kaunsi hai?"; ar = ''; ref = f'Surah {name} · surah {sid}'
    opts = others + [sid]; rnd.shuffle(opts)
    return {'kind': kind, 'sid': sid, 'a': a, 'q': q, 'ar': ar,
            'opts': [S[x]['transliteration'] for x in opts], 'optIds': opts, 'ans': opts.index(sid), 'ref': ref}

# reel recipe: 8 questions, easier first
RECIPES = [
    ['first', 'meaning', 'ayah', 'count', 'ayah', 'number', 'ayah', 'ayah'],
    ['ayah', 'count', 'meaning', 'ayah', 'number', 'ayah', 'last', 'ayah'],
    ['meaning', 'ayah', 'number', 'ayah', 'count', 'ayah', 'ayah', 'meaning'],
    ['ayah', 'number', 'count', 'ayah', 'meaning', 'ayah', 'ayah', 'count'],
]
MIN_GAP = 30   # days before the same question may come back

def schedule(start, days, seed='zikartone'):
    rnd = random.Random(seed)
    queues = {}; used_today = set()
    last_day = {}
    def draw(kind, easy, d):
        q = queues.setdefault(kind, [])
        def refill():
            q.extend(POOL[kind]); rnd.shuffle(q)
        if not q: refill()
        def fresh(i):
            return d - last_day.get((kind,) + q[i], -10**6) >= MIN_GAP and q[i][0] not in used_today
        cand = [i for i in range(len(q)) if fresh(i)]
        if not cand:
            refill(); cand = [i for i in range(len(q)) if fresh(i)] or list(range(len(q)))
        pref = [i for i in cand if kind == 'number' or (q[i][0] in FAMOUS) == easy] or cand
        item = q.pop(pref[0]); last_day[(kind,) + item] = d
        return item
    out = []
    for d in range(days):
        day = start + datetime.timedelta(days=d)
        recipe = RECIPES[d % len(RECIPES)]
        qs = []; used_today.clear()
        for i, kind in enumerate(recipe):
            sid, a = draw(kind, easy=(i < 4), d=d)
            used_today.add(sid)
            qs.append(make(kind, sid, a, rnd))
        out.append({'date': day.isoformat(), 'no': d + 1, 'questions': qs})
    return out

def verify(sched):
    """Independent check of every question against the data."""
    bad = 0
    for day in sched:
        for q in day['questions']:
            ids = q['optIds']; sid = q['sid']; c = S[sid]
            ok = len(set(ids)) == 4 and ids[q['ans']] == sid
            if q['kind'] in ('first', 'last', 'ayah'):
                t = norm(q['ar'])
                ok &= norm(c['verses'][q['a'] - 1]['text']) == t
                ok &= all(x == sid or x not in WHERE[t] for x in ids)
                if q['kind'] == 'first': ok &= q['a'] == 1
                if q['kind'] == 'last': ok &= q['a'] == c['total_verses']
            elif q['kind'] == 'count':
                ok &= sum(S[x]['total_verses'] == c['total_verses'] for x in ids) == 1
            elif q['kind'] == 'meaning':
                ok &= sum(S[x]['translation'] == c['translation'] for x in ids) == 1
            if not ok: bad += 1; print('BAD', day['date'], q)
    return bad

START = datetime.date(2026, 12, 1)
DAYS = 365

def year():
    """The full schedule, checked. Stops with an error if any question fails the check."""
    sch = schedule(START, DAYS)
    bad = verify(sch)
    if bad:
        raise SystemExit(f'{bad} questions failed the check; no reel made.')
    return sch

if __name__ == '__main__':
    for k, v in POOL.items(): print(k, len(v))
    s = year(); print('ok, days:', len(s), s[0]['date'], '->', s[-1]['date'])
