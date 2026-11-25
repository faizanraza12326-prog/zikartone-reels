"""Upload a reel to TikTok with autotok (TikTok's own web upload, no app audit needed).

Needs GitHub secrets: TIKTOK_SESSIONID and TIKTOK_IDC (the tt-target-idc cookie), copied from
a Chrome that is logged in to TikTok. Optional: TIKTOK_UA (that Chrome's user agent).
Skips if not set. Exits with an error if the upload fails, so GitHub emails the owner.

Usage:
  python upload_tiktok.py out/2026-12-05            normal daily post (public)
  python upload_tiktok.py --check                   only checks that the login still works
  python upload_tiktok.py out/2026-12-05 --private  test upload, visible only to you
"""
import json, os, sys

DEFAULT_UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
              '(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36')


def client():
    sid = os.environ.get('TIKTOK_SESSIONID', '').strip()
    if not sid:
        return None
    from autotok import Client
    return Client.from_session_id(sid, datacenter=os.environ.get('TIKTOK_IDC', '').strip() or None,
                                  user_agent=os.environ.get('TIKTOK_UA', '').strip() or DEFAULT_UA, proxy=False)


def main(args):
    c = client()
    if c is None:
        print('TikTok secrets not set, skipping TikTok.'); return 0
    if '--check' in args:
        ok = c.check_session()
        print('TikTok login OK' if ok else 'TikTok login EXPIRED: copy a fresh sessionid into the TIKTOK_SESSIONID secret')
        return 0 if ok else 1
    base = [a for a in args if not a.startswith('--')][0]
    private = '--private' in args
    meta = json.load(open(base + '.json', encoding='utf8'))
    log = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'posted.log')
    mark = f"tiktok {meta['date']}"
    if not private and os.path.exists(log) and mark in open(log, encoding='utf8').read().split('\n'):
        print('TikTok already posted for', meta['date'], '- skipping'); return 0
    if not c.check_session():
        print('TikTok login EXPIRED: copy a fresh sessionid into the TIKTOK_SESSIONID secret'); return 1
    res = c.upload(base + '.mp4', meta['caption'][:2000], visibility='private' if private else 'public')
    print('TikTok posted', '(private test)' if private else '', res, flush=True)
    if not private:
        open(log, 'a', encoding='utf8').write(mark + '\n')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1:]))
    except Exception as e:
        print('TikTok FAILED:', type(e).__name__, e); sys.exit(1)
