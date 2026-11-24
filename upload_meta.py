"""Post a reel to Instagram (as a Reel) and to the Facebook Page (as a Reel).

Needs these environment variables (GitHub secrets):
  META_PAGE_TOKEN  long-lived Page access token (from meta_setup.py)
  FB_PAGE_ID       Facebook Page id
  IG_USER_ID       Instagram professional account id linked to that Page
Skips quietly if they are not set."""
import json, os, sys, time, requests

V = 'v25.0'
G = f'https://graph.facebook.com/{V}'

def need(*names):
    vals = [os.environ.get(n, '').strip() for n in names]
    return vals if all(vals) else None

def ig_wait_publish(cid, token, ig):
    st = {}
    for k in range(90):                     # wait up to ~15 minutes for processing
        st = requests.get(f'{G}/{cid}', params={'fields': 'status_code,status', 'access_token': token}, timeout=30).json()
        if k % 6 == 0: print('Instagram processing:', st, flush=True)
        if st.get('status_code') == 'FINISHED': break
        if st.get('status_code') == 'ERROR': raise RuntimeError(f'Instagram processing error: {st}')
        time.sleep(10)
    else:
        raise RuntimeError(f'Instagram still processing after 15 minutes: {st}')
    pub = requests.post(f'{G}/{ig}/media_publish', data={'creation_id': cid, 'access_token': token}, timeout=60).json()
    if 'id' not in pub: raise RuntimeError(f'Instagram publish failed: {pub}')
    return pub['id']

def fb_video_url(page, token, caption):
    """Public file URL of today's Facebook reel (same video), so Instagram can fetch it itself."""
    for _ in range(30):                     # up to ~5 minutes for Facebook to finish processing
        r = requests.get(f'{G}/{page}/video_reels', params={'fields': 'id,source,description', 'limit': 10, 'access_token': token}, timeout=30).json()
        for v in r.get('data', []):
            if caption.strip()[:40] in (v.get('description') or '') and v.get('source'):
                return v['source']
        time.sleep(10)
    raise RuntimeError(f'Facebook reel file URL not found: {str(r)[:300]}')

def public_url():
    """Today's reel on GitHub Pages (set by the workflow). Waits until the link really serves the file."""
    u = os.environ.get('PUBLIC_VIDEO_URL', '').strip()
    if not u: return None
    for _ in range(36):                     # up to ~6 minutes for Pages to go live
        try:
            r = requests.head(u, timeout=30, allow_redirects=True)
            if r.status_code == 200: return u
        except Exception:
            pass
        time.sleep(10)
    print('Public link never came up:', u, flush=True)
    return None

def ig_from_url(src, caption, token, ig):
    r = requests.post(f'{G}/{ig}/media', data={'media_type': 'REELS', 'video_url': src, 'caption': caption,
                                               'share_to_feed': 'true', 'access_token': token}, timeout=60).json()
    if 'id' not in r: raise RuntimeError(f'Instagram container (video_url) failed: {r}')
    return ig_wait_publish(r['id'], token, ig)

def post_instagram(mp4, caption, token, ig, page=None):
    src = public_url()
    if src:
        print('Instagram: using the public link:', src, flush=True)
        try:
            return ig_from_url(src, caption, token, ig)
        except Exception as e:
            print('Instagram from public link did not work:', e, flush=True)
    try:
        return post_instagram_resumable(mp4, caption, token, ig)
    except Exception as e:
        print('Instagram direct upload did not work:', e, flush=True)
    if not page: raise RuntimeError('Instagram: no way left to upload')
    print('Instagram: trying with the Facebook reel file URL', flush=True)
    return ig_from_url(fb_video_url(page, token, caption), caption, token, ig)

def post_instagram_resumable(mp4, caption, token, ig):
    r = requests.post(f'{G}/{ig}/media', data={'media_type': 'REELS', 'upload_type': 'resumable', 'caption': caption,
                                               'share_to_feed': 'true', 'access_token': token}, timeout=60).json()
    if 'id' not in r: raise RuntimeError(f'Instagram container failed: {r}')
    cid, uri = r['id'], r.get('uri') or f'https://rupload.facebook.com/ig-api-upload/{V}/{r["id"]}'
    data = open(mp4, 'rb').read()
    up = requests.post(uri, headers={'Authorization': f'OAuth {token}', 'offset': '0', 'file_size': str(len(data))}, data=data, timeout=300)
    print('Instagram upload response:', up.status_code, up.text[:500], flush=True)
    if up.status_code != 200 or up.json().get('success') is not True: raise RuntimeError(f'Instagram upload failed: {up.text[:500]}')
    return ig_wait_publish(cid, token, ig)

def post_facebook(mp4, caption, token, page):
    st = requests.post(f'{G}/{page}/video_reels', data={'upload_phase': 'start', 'access_token': token}, timeout=60).json()
    if 'video_id' not in st: raise RuntimeError(f'Facebook start failed: {st}')
    vid = st['video_id']; url = st.get('upload_url') or f'https://rupload.facebook.com/video-upload/{V}/{vid}'
    data = open(mp4, 'rb').read()
    up = requests.post(url, headers={'Authorization': f'OAuth {token}', 'offset': '0', 'file_size': str(len(data))}, data=data, timeout=300).json()
    if not up.get('success', True): raise RuntimeError(f'Facebook upload failed: {up}')
    fin = requests.post(f'{G}/{page}/video_reels', data={'upload_phase': 'finish', 'video_id': vid, 'video_state': 'PUBLISHED',
                                                         'description': caption, 'access_token': token}, timeout=60).json()
    if not fin.get('success'): raise RuntimeError(f'Facebook publish failed: {fin}')
    return vid

if __name__ == '__main__':
    base = sys.argv[1]
    meta = json.load(open(base + '.json', encoding='utf8'))
    creds = need('META_PAGE_TOKEN', 'FB_PAGE_ID', 'IG_USER_ID')
    if not creds:
        print('Meta secrets not set, skipping Instagram and Facebook.'); sys.exit(0)
    token, page, ig = creds
    # posted.log remembers what already went out, so a reel is never posted twice on the same platform
    log = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'posted.log')
    done = set(open(log, encoding='utf8').read().split('\n')) if os.path.exists(log) else set()
    day = meta['date']
    failed = False
    # Facebook first: if Instagram's direct upload fails, Instagram can fetch the same file from the Facebook reel
    jobs = [('Facebook', lambda: post_facebook(base + '.mp4', meta['caption'], token, page)),
            ('Instagram', lambda: post_instagram(base + '.mp4', meta['caption'], token, ig, page))]
    for name, job in jobs:
        mark = f'{name.lower()} {day}'
        if mark in done:
            print(name, 'already posted for', day, '- skipping'); continue
        try:
            print(name, 'posted:', job(), flush=True)
            open(log, 'a', encoding='utf8').write(mark + '\n')
        except Exception as e:
            failed = True; print(name, 'FAILED:', e)
    sys.exit(1 if failed else 0)
