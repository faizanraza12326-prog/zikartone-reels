"""Upload a reel to TikTok by driving TikTok's own upload page in a headless browser.

Uses the tiktok-uploader library (Playwright). Login = your TikTok session cookie.
Needs GitHub secrets: TIKTOK_SESSIONID and TIKTOK_IDC (the tt-target-idc cookie), copied from
a Chrome that is logged in to TikTok. Optional: TIKTOK_UA (that Chrome's user agent).
Skips if not set. Exits with an error if the upload fails, so GitHub emails the owner.

Usage:
  python upload_tiktok.py out/2026-12-05            normal daily post (public)
  python upload_tiktok.py --check                   only checks that the login still works
  python upload_tiktok.py out/2026-12-05 --private  test upload, visible only to you
"""
import json, os, re, sys

DEFAULT_UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/158.0.0.0 Safari/537.36')


def env(k):
    return os.environ.get(k, '').strip()


def check_login():
    """Cheap check: TikTok's upload-auth endpoint answers only for a logged-in session."""
    import requests
    s = requests.Session()
    s.cookies.set('sessionid', env('TIKTOK_SESSIONID'), domain='.tiktok.com')
    if env('TIKTOK_IDC'):
        s.cookies.set('tt-target-idc', env('TIKTOK_IDC'), domain='.tiktok.com')
    r = s.get('https://www.tiktok.com/api/v1/video/upload/auth/?aid=1988',
              headers={'User-Agent': env('TIKTOK_UA') or DEFAULT_UA}, timeout=30)
    try:
        return r.status_code == 200 and 'video_token_v5' in r.json()
    except ValueError:
        return False


def short_caption(full):
    """TikTok's upload box takes ~150 chars here; first line of the hook + a few hashtags, single spaces."""
    first = re.sub(r'\s+', ' ', full.split('\n')[0]).strip()
    tags = re.findall(r'#\w+', full)
    cap = first
    for t in tags:
        if len(cap) + 1 + len(t) > 145:
            break
        cap += ' ' + t
    return cap


def upload(mp4, caption, private):
    import tiktok_uploader.auth as tauth
    from tiktok_uploader import config
    from tiktok_uploader.upload import TikTokUploader
    tauth.print = lambda *a, **k: None          # the library prints cookies; never let that reach the log
    config.disguising.user_agent = env('TIKTOK_UA') or DEFAULT_UA
    cookies = [{'name': 'sessionid', 'value': env('TIKTOK_SESSIONID'), 'domain': '.tiktok.com', 'path': '/'}]
    if env('TIKTOK_IDC'):
        cookies.append({'name': 'tt-target-idc', 'value': env('TIKTOK_IDC'), 'domain': '.tiktok.com', 'path': '/'})
    up = TikTokUploader(cookies_list=cookies, browser='chromium', headless=True)
    page = up.page                              # opens the browser and logs in
    # TikTok shows one-time popups (content check, new features...) that block the buttons. Close them whenever they appear.
    def close_popup(overlay):
        for name in ('Turn on', 'Got it', 'Not now', 'Cancel', 'OK', 'Continue', 'Close', 'Confirm'):
            btn = page.locator('[data-floating-ui-portal] button, .TUXModal button, [role=dialog] button').filter(has_text=re.compile('^' + name + '$', re.I))
            if btn.count():
                try:
                    btn.first.click(timeout=3000, force=True); print('Closed TikTok popup with', name, flush=True); return
                except Exception:
                    pass
        page.keyboard.press('Escape')
    page.add_locator_handler(page.locator('.TUXModal-overlay').first, close_popup, no_wait_after=True)
    # "New features" guided tour (react-joyride) also covers the page: hide it with CSS (removing it could break the page).
    hide_tour = """() => { if (document.getElementById('zk-hide-tour')) return;
        const st = document.createElement('style'); st.id = 'zk-hide-tour';
        st.textContent = '#react-joyride-portal, .react-joyride__overlay, .react-joyride__spotlight, .__floater' +
                         ' { display: none !important; pointer-events: none !important; }';
        (document.head || document.documentElement).appendChild(st); }"""
    page.context.add_init_script(f"setInterval({hide_tour}, 300);")
    page.add_locator_handler(page.locator('.react-joyride__overlay').first,
                             lambda o: page.evaluate(hide_tour), no_wait_after=True)
    try:
        failed = up.upload_videos([{'path': mp4, 'description': caption,
                                    **({'visibility': 'only_you'} if private else {})}])
        if failed:
            try:
                page.screenshot(path='tiktok_fail.png', full_page=True)
            except Exception:
                pass
    finally:
        try:
            up.close()
        except Exception:
            pass
    return not failed


def main(args):
    if not env('TIKTOK_SESSIONID'):
        print('TikTok secrets not set, skipping TikTok.'); return 0
    if not check_login():
        print('TikTok login EXPIRED: copy a fresh sessionid into the TIKTOK_SESSIONID secret (see README)'); return 1
    if '--check' in args:
        print('TikTok login OK'); return 0
    base = [a for a in args if not a.startswith('--')][0]
    private = '--private' in args
    meta = json.load(open(base + '.json', encoding='utf8'))
    log = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'posted.log')
    mark = f"tiktok {meta['date']}"
    if not private and os.path.exists(log) and mark in open(log, encoding='utf8').read().split('\n'):
        print('TikTok already posted for', meta['date'], '- skipping'); return 0
    cap = short_caption(meta['caption'])
    print('TikTok caption:', cap, flush=True)
    if not upload(base + '.mp4', cap, private):
        print('TikTok FAILED: the upload page did not finish (see the lines above)'); return 1
    print('TikTok posted', '(private test)' if private else '', flush=True)
    if not private:
        open(log, 'a', encoding='utf8').write(mark + '\n')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except Exception as e:
        print('TikTok FAILED:', type(e).__name__, e); sys.exit(1)
