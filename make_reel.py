"""Make today's Zikartone "Guess the Surah" reel.

    python make_reel.py                 # today's reel (Pakistan date)
    python make_reel.py --date 2026-12-05
    python make_reel.py --from 2026-12-01 --days 30   # a batch, e.g. for YouTube/TikTok scheduling

Writes out/<date>.mp4 and out/<date>.txt (caption) and out/<date>.json (title etc.)."""
import argparse, datetime, json, os, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import audio

FPS = 15
CHROME = os.environ.get('CHROME_PATH', '/usr/bin/google-chrome')
SITE = 'zikartone.netlify.app'
import bank
SCHEDULE = bank.year()
BY_DATE = {d['date']: d for d in SCHEDULE}

HOOKS = [
    "Guess the Surah! 🌙\n8 sawal, har sawal ke liye sirf 8 second. Kitne sahi bata sakte ho?",
    "Qur'an se kitni mohabbat hai? Aaj check karte hain! 📖\n8 sawal, 8-8 second.",
    "Sirf asli Qur'an lovers 8/8 karenge 👀\nAyat dekh kar surah pehchano!",
    "Aaj ka Qur'an quiz 🌙\nHar sawal ke liye 8 second. Pause mat karna, imandari se!",
    "Bachpan mein jo surahs yaad ki thin, kya ab bhi pehchaan lete ho? 🤲\n8 sawal, 8 second.",
    "Qur'an quiz time! ✨\nAyat, naam aur ayaat ki tadaad, sab se surah pehchano.",
    "Kya aap apne dost se zyada jaante ho? 😄\nAaj ka Guess the Surah, 8 sawal.",
]
TAGS = "#guessthesurah #quranquiz #islamicquiz #quran #zikartone #muslimreels #islamicreels #quranlover"

def caption(day):
    hook = HOOKS[(day['no'] - 1) % len(HOOKS)]
    return (f"{hook}\n\nComment mein apna score likho (X/8) 👇\n"
            f"Us dost ko tag karo jo Qur'an aap se zyada jaanta hai!\n\n"
            f"Qur'an Urdu tarjume ke saath, Hadith aur Duas, sab free: {SITE}\n\n{TAGS}")

def title(day):
    return f"Guess the Surah #{day['no']} | Qur'an Quiz 🌙 #Shorts"

def render(day, out_mp4):
    from playwright.sync_api import sync_playwright
    quiz = day['questions']
    work = os.path.join(ROOT, 'out', '_frames'); shutil.rmtree(work, ignore_errors=True); os.makedirs(work)
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=CHROME if os.path.exists(CHROME) else None, args=['--no-sandbox', '--allow-file-access-from-files'])
        pg = b.new_page(viewport={'width': 1080, 'height': 1920})
        pg.add_init_script('window.QUIZ = ' + json.dumps(quiz, ensure_ascii=False))
        pg.goto('file://' + os.path.join(ROOT, 'assets', 'template.html'))
        pg.evaluate('document.fonts.ready'); pg.wait_for_timeout(600)
        total = pg.evaluate('window.TOTAL')
        for i in range(int(total * FPS)):
            pg.evaluate(f'render({i / FPS})')
            pg.screenshot(path=os.path.join(work, f'{i:05d}.jpg'), type='jpeg', quality=88)
        b.close()
    wav = os.path.join(work, 'audio.wav')
    audio.build(len(quiz), wav)
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-framerate', str(FPS), '-i', os.path.join(work, '%05d.jpg'), '-i', wav,
                    '-vf', 'fps=30,format=yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20',
                    '-c:a', 'aac', '-b:a', '160k', '-ar', '48000', '-ac', '2', '-shortest', '-movflags', '+faststart', '-use_editlist', '0', out_mp4], check=True)
    shutil.rmtree(work, ignore_errors=True)

def make(date_str):
    day = BY_DATE.get(date_str)
    if not day:
        print(f'No reel scheduled for {date_str} (schedule runs {SCHEDULE[0]["date"]} to {SCHEDULE[-1]["date"]}).'); return None
    os.makedirs(os.path.join(ROOT, 'out'), exist_ok=True)
    base = os.path.join(ROOT, 'out', date_str)
    render(day, base + '.mp4')
    open(base + '.txt', 'w', encoding='utf8').write(caption(day))
    json.dump({'date': date_str, 'no': day['no'], 'title': title(day), 'caption': caption(day)}, open(base + '.json', 'w', encoding='utf8'), ensure_ascii=False)
    print('made', base + '.mp4')
    return base

def pk_today():
    return (datetime.datetime.utcnow() + datetime.timedelta(hours=5)).date()

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--date'); ap.add_argument('--from', dest='frm'); ap.add_argument('--days', type=int, default=1)
    a = ap.parse_args()
    if a.frm:
        start = datetime.date.fromisoformat(a.frm)
        for k in range(a.days): make((start + datetime.timedelta(days=k)).isoformat())
    else:
        base = make(a.date or pk_today().isoformat())
        if base and os.environ.get('GITHUB_OUTPUT'):
            open(os.environ['GITHUB_OUTPUT'], 'a').write(f'base={base}\n')
