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

def post_instagram(mp4, caption, token, ig):
    r = requests.post(f'{G}/{ig}/media', data={'media_type': 'REELS', 'upload_type': 'resumable', 'caption': caption,
                                               'share_to_feed': 'true', 'access_token': token}, timeout=60).json()
    if 'id' not in r: raise RuntimeError(f'Instagram container failed: {r}')
    cid, uri = r['id'], r.get('uri') or f'https://rupload.facebook.com/ig-api-upload/{V}/{r["id"]}'
    data = open(mp4, 'rb').read()
    up = requests.post(uri, headers={'Authorization': f'OAuth {token}', 'offset': '0', 'file_size': str(len(data))}, data=data, timeout=300).json()
    if not up.get('success', True): raise RuntimeError(f'Instagram upload failed: {up}')
    for _ in range(60):                     # wait up to ~10 minutes for processing
        st = requests.get(f'{G}/{cid}', params={'fields': 'status_code,status', 'access_token': token}, timeout=30).json()
        if st.get('status_code') == 'FINISHED': break
        if st.get('status_code') == 'ERROR': raise RuntimeError(f'Instagram processing error: {st}')
        time.sleep(10)
    pub = requests.post(f'{G}/{ig}/media_publish', data={'creation_id': cid, 'access_token': token}, timeout=60).json()
    if 'id' not in pub: raise RuntimeError(f'Instagram publish failed: {pub}')
    return pub['id']

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
    failed = False
    for name, fn, target in [('Instagram', post_instagram, ig), ('Facebook', post_facebook, page)]:
        try:
            print(name, 'posted:', fn(base + '.mp4', meta['caption'], token, target))
        except Exception as e:
            failed = True; print(name, 'FAILED:', e)
    sys.exit(1 if failed else 0)
