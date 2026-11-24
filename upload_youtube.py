"""Upload a reel to YouTube as a Short.

Needs: YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN (from get_youtube_token.py). Skips if not set.
Note: until Google approves the API project (YouTube API audit), YouTube keeps API uploads private.
Set YT_PRIVACY=private while waiting, then public after approval."""
import json, os, sys

def main(base):
    cid, sec, ref = (os.environ.get(k, '').strip() for k in ('YT_CLIENT_ID', 'YT_CLIENT_SECRET', 'YT_REFRESH_TOKEN'))
    if not (cid and sec and ref):
        print('YouTube secrets not set, skipping YouTube.'); return 0
    from google.oauth2.credentials import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    creds = Credentials(None, refresh_token=ref, token_uri='https://oauth2.googleapis.com/token', client_id=cid, client_secret=sec,
                        scopes=['https://www.googleapis.com/auth/youtube.upload'])
    meta = json.load(open(base + '.json', encoding='utf8'))
    yt = build('youtube', 'v3', credentials=creds, cache_discovery=False)
    body = {'snippet': {'title': meta['title'][:100], 'description': meta['caption'][:4900], 'categoryId': '27',
                        'tags': ['Quran', 'Quran quiz', 'Guess the Surah', 'Islamic quiz', 'Zikartone']},
            'status': {'privacyStatus': os.environ.get('YT_PRIVACY', 'public'), 'selfDeclaredMadeForKids': False}}
    req = yt.videos().insert(part='snippet,status', body=body, media_body=MediaFileUpload(base + '.mp4', chunksize=-1, resumable=True))
    resp = None
    while resp is None:
        _, resp = req.next_chunk()
    print('YouTube posted:', resp.get('id'))
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main(sys.argv[1]))
    except Exception as e:
        print('YouTube FAILED:', e); sys.exit(1)
