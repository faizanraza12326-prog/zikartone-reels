# Zikartone Reels: poore saal ki automatic "Guess the Surah" reels

Har roz shaam 7 baje (Pakistan time) GitHub khud ek nayi reel banata hai aur **Instagram, Facebook aur YouTube Shorts** par post karta hai. TikTok har 10 din mein haath se schedule hota hai. Sab free hai.

- Schedule: 1 December 2026 se 30 November 2027, 365 reels, 2920 sawal (har sawal code se check hua).
- Har reel ki copy 30 din tak Actions > run > Artifacts mein rehti hai.
- `posted.log` yaad rakhta hai kya post ho chuka hai, is liye koi reel do dafa post nahi hoti.

## Kya kahan se chalta hai

| Platform | Kaise | Secrets |
|---|---|---|
| Facebook Page "Zikartone" | Khud, roz 7 PM | META_PAGE_TOKEN, FB_PAGE_ID |
| Instagram zikartone.official | Khud, roz 7 PM (video GitHub Pages ke public link se jati hai) | META_PAGE_TOKEN, IG_USER_ID |
| YouTube Zikartone.official | Khud, roz 7 PM | YT_CLIENT_ID, YT_CLIENT_SECRET, YT_REFRESH_TOKEN |
| TikTok | Har 10 din, TikTok Studio se schedule (neeche dekho) | koi nahi |

Repo **Public** hai taa ke GitHub Pages chale (Instagram ko video ka public link chahiye). Secrets phir bhi kisi ko nazar nahi aate.

## TikTok (har 10 din, 10 minute)

TikTok apne free scheduler mein sirf 10 din aage tak schedule karne deta hai.
1. GitHub > Actions > **Batch of reels** > Run workflow > `from` = agli tareekh (maslan 2026-12-05), `days` = 10.
2. Run khatam ho to Artifacts se zip download karo. Har din ki `.mp4` aur caption `.txt` mile gi.
3. Laptop par tiktok.com/tiktokstudio/upload > video select karo > caption paste karo > **Schedule** > woh tareekh, 19:00 > Schedule.

## Kabhi kuch toot jaye

- **Facebook/Instagram band:** Zikar Tone Facebook account ka password badla ya app hatayi to token band ho jata hai. developers.facebook.com/tools/explorer > app "Zikartone Reels" > Generate Access Token > Access Token Debugger mein "Extend" > `me/accounts` se naya Page token > GitHub Secrets mein META_PAGE_TOKEN update.
- **YouTube band:** faizanraza12326@gmail.com ka password badla ya "Zikartone Reels" app ka access hataya to refresh token band. developers.google.com/oauthplayground (apna client ID/secret, scope youtube.upload) se naya refresh token > YT_REFRESH_TOKEN update. Google Cloud project: zikartone-reels (sirf faizanraza12326@gmail.com par). Koi aur account use nahi karna.
- **Kisi din ki reel dobara:** Actions > Daily reel > Run workflow > woh date. Jo platform pehle ho chuka hai woh skip hoga.
- **Waqt badalna:** `.github/workflows/daily.yml` mein `cron: '0 14 * * *'` (UTC; Pakistan = UTC+5).
- **Caption badalna:** `make_reel.py` mein `HOOKS` aur `TAGS`.
- **Koi aur masla:** Actions mein run kholo, "Instagram + Facebook" ya "YouTube Shorts" step ka text copy karke kisi developer ya AI ko dikhao.

## Files

| File | Kaam |
|---|---|
| `bank.py` | 365 din ke sawal banata aur check karta hai |
| `make_reel.py` | Us din ki reel: video, caption, title |
| `assets/template.html`, `audio.py` | Design aur awaaz (music nahi) |
| `upload_meta.py` | Facebook + Instagram |
| `upload_youtube.py` | YouTube Shorts |
| `.github/workflows/daily.yml` | Roz ka kaam |
| `.github/workflows/batch.yml` | Ek saath kai din ki reels (TikTok ke liye) |
