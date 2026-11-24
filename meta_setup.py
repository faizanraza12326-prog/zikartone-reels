"""One-time helper (run on your laptop): turns a short-lived token from Graph API Explorer
into a Page token that does not expire, and prints the three values for GitHub secrets.

    python meta_setup.py APP_ID APP_SECRET SHORT_LIVED_USER_TOKEN
"""
import sys, requests
G = 'https://graph.facebook.com/v21.0'
app_id, app_secret, short = sys.argv[1:4]
long = requests.get(f'{G}/oauth/access_token', params={'grant_type': 'fb_exchange_token', 'client_id': app_id,
                    'client_secret': app_secret, 'fb_exchange_token': short}, timeout=30).json()
if 'access_token' not in long: sys.exit(f'Could not extend token: {long}')
pages = requests.get(f'{G}/me/accounts', params={'access_token': long['access_token']}, timeout=30).json().get('data', [])
if not pages: sys.exit('No Facebook Page found for this account. Make sure the token has pages_show_list.')
for p in pages:
    ig = requests.get(f"{G}/{p['id']}", params={'fields': 'instagram_business_account', 'access_token': p['access_token']}, timeout=30).json()
    igid = (ig.get('instagram_business_account') or {}).get('id', '(no Instagram linked)')
    print(f"\nPage: {p['name']}\n  FB_PAGE_ID      = {p['id']}\n  IG_USER_ID      = {igid}\n  META_PAGE_TOKEN = {p['access_token']}")
print('\nCopy the three values for the Zikartone page into GitHub > Settings > Secrets and variables > Actions.')
