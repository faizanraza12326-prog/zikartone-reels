# Zikartone Reels: poore saal ki automatic "Guess the Surah" reels

Har roz shaam 7 baje (Pakistan time) GitHub khud ek nayi reel banata hai aur **Instagram, Facebook, YouTube Shorts aur TikTok** par post karta hai. Sab free hai.

- Schedule: 1 December 2026 se 30 November 2027, 365 reels, 2920 sawal (har sawal code se check hua).
- Har reel ki copy 30 din tak Actions > run > Artifacts mein rehti hai.
- `posted.log` yaad rakhta hai kya post ho chuka hai, is liye koi reel do dafa post nahi hoti.

## Kya kahan se chalta hai

| Platform | Kaise | Secrets |
|---|---|---|
| Facebook Page "Zikartone" | Khud, roz 7 PM | META_PAGE_TOKEN, FB_PAGE_ID |
| Instagram zikartone.official | Khud, roz 7 PM (video GitHub Pages ke public link se jati hai) | META_PAGE_TOKEN, IG_USER_ID |
| YouTube Zikartone.official | Khud, roz 7 PM | YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN |
| TikTok | Khud, roz 7 PM (tiktok-uploader: TikTok ka upload page khud chalata hai) | TIKTOK_SESSIONID, TIKTOK_IDC (+ variable TIKTOK_UA) |

Repo **Public** hai taa ke GitHub Pages chale (Instagram ko video ka public link chahiye). Secrets phir bhi kisi ko nazar nahi aate.

## TikTok

TikTok ka official API bina audit ke sirf private post karta hai, is liye TikTok wala step tumhare TikTok login (cookie) se upload karta hai. Ye login kuch mahine chalta hai.

- **Login lagana/badalna (5 minute):** laptop Chrome mein tiktok.com par zikartone account se login > F12 > Application > Cookies > https://www.tiktok.com > `sessionid` ki Value copy karke GitHub > Settings > Secrets and variables > Actions mein **TIKTOK_SESSIONID** mein daalo, aur `tt-target-idc` ki Value **TIKTOK_IDC** mein. Phir Actions > **TikTok test** > Run workflow > `check`.
- Us Chrome mein TikTok se **logout mat karna**, warna ye login band ho jata hai.
- TikTok fail ho to us din ka run laal ho jata hai aur GitHub email bhejta hai. Baaki platforms phir bhi post ho chuke hote hain. Login dobara lagao, phir Actions > Daily reel > Run workflow > woh date (sirf TikTok post hoga).
- Agar kabhi bilkul na chale to backup: Actions > **Batch of reels** (`from` = tareekh, `days` = 10) > zip download > tiktok.com/tiktokstudio/upload se har video **Schedule** karo (10 din aage tak).

## Kabhi kuch toot jaye

- **Facebook/Instagram band:** Zikar Tone Facebook account ka password badla ya app hatayi to token band ho jata hai. developers.facebook.com/tools/explorer > app "Zikartone Reels" > Generate Access Token > Access Token Debugger mein "Extend" > `me/accounts` se naya Page token > GitHub Secrets mein META_PAGE_TOKEN update.
- **YouTube band:** faizanraza12326@gmail.com ka password badla ya "Zikartone Reels" app ka access hataya to refresh token band. developers.google.com/oauthplayground (apna client ID/secret, scope youtube.upload) se naya refresh token > YT_REFRESH_TOKEN update. Google Cloud project: zikartone-reels (sirf faizanraza12326@gmail.com par). Koi aur account use nahi karna.
- **Kisi din ki reel dobara:** Actions > Daily reel > Run workflow > woh date. Jo platform pehle ho chuka hai woh skip hoga.
- **Waqt badalna:** `.github/workflows/daily.yml` mein `cron: '0 14 * * *'` (UTC; Pakistan = UTC+5).
- **Caption badalna:** `make_reel.py` mein `HOOKS` aur `TAGS`.
- **Koi aur masla:** Actions mein run kholo, "Instagram + Facebook", "YouTube Shorts" ya "TikTok" step ka text copy karke kisi developer ya AI ko dikhao.

## Files

| File | Kaam |
|---|---|
| `bank.py` | 365 din ke sawal banata aur check karta hai |
| `make_reel.py` | Us din ki reel: video, caption, title |
| `assets/template.html`, `audio.py` | Design aur awaaz (music nahi) |
| `upload_meta.py` | Facebook + Instagram |
| `upload_youtube.py` | YouTube Shorts |
| `upload_tiktok.py` | TikTok |
| `.github/workflows/daily.yml` | Roz ka kaam |
| `.github/workflows/batch.yml` | Ek saath kai din ki reels (backup) |
| `.github/workflows/tiktok_test.yml` | TikTok login check / private test |
