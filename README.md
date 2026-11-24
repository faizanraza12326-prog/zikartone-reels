# Zikartone Reels: poore saal ki automatic "Guess the Surah" reels

Yeh system har roz shaam 7 baje (Pakistan time) khud ek nayi reel banata hai aur Instagram aur Facebook par post karta hai. YouTube ka bhi intezam hai. Claude ki zaroorat nahi: sab GitHub par muft chalta hai.

- Schedule: **1 December 2026 se 30 November 2027**, 365 reels, 2920 sawal.
- Har sawal Qur'an ke data se bana aur code se check hua. Koi sawal 30 din se pehle wapas nahi aata.
- Har reel ki copy 30 din tak GitHub par download ke liye rehti hai (Actions > run > Artifacts).

---

## Qadam 1: GitHub par daalo (10 minute)

1. github.com par account banao ya login karo.
2. Upar **+** > **New repository**. Naam: `zikartone-reels`. **Private** rakho. Private repo mein GitHub har mahine 2000 minute free deta hai; roz ki reel takreeban 4-5 minute leti hai, yani mahine ke ~150 minute.
3. Naye repo mein **"uploading an existing file"** link dabao. Is zip ko unzip karke **saari files aur folders** (`.github` folder samait) wahan drag karo aur **Commit changes**.
   - Agar `.github` folder upload na ho (kuch computers par chhupa hota hai), to repo mein **Add file > Create new file** karo, naam likho `.github/workflows/daily.yml`, aur zip ki `daily.yml` ka text paste kar do. `batch.yml` ke liye bhi yahi.
4. Repo mein **Settings > Actions > General** mein "Workflow permissions" ko **Read and write permissions** karo, Save.
5. **Actions** tab kholo. Agar button aaye "I understand my workflows, go ahead and enable them" to dabao.

**Test:** Actions > **Daily reel** > **Run workflow** > date mein `2026-12-01` likho > Run. 3-4 minute baad run khol ke neeche **Artifacts** se reel download karke dekh lo. Yahan tak sab bina kisi password ke chalta hai.

---

## Qadam 2: Instagram + Facebook automatic (20-30 minute, sirf ek dafa)

Shart: Instagram account **Professional (Creator ya Business)** ho aur Zikartone ke **Facebook Page** se juda ho.
(Instagram app > Settings > Account type and tools > Switch to professional. Phir Facebook Page ki settings > Linked accounts > Instagram connect.)

1. developers.facebook.com par jao, apne Facebook se login karo, **My Apps > Create App**.
   - Use case mein **"Manage everything on your Page"** aur **Instagram** wala (Instagram API with Facebook Login) chuno. App ka naam: `Zikartone Reels`.
   - App **Development mode** mein hi rehne do. Apne khud ke Page aur Instagram par post karne ke liye review nahi chahiye.
2. App ki **Settings > Basic** se **App ID** aur **App Secret** copy karke rakho.
3. developers.facebook.com/tools/explorer kholo (Graph API Explorer):
   - Upar apni app chuno.
   - **Add a Permission** mein yeh sab tick karo: `pages_show_list`, `pages_read_engagement`, `pages_manage_posts`, `instagram_basic`, `instagram_content_publish`, `business_management`.
   - **Generate Access Token** dabao, Zikartone Page aur Instagram ko allow karo, aur token copy karo.
4. Laptop par (Python lagi ho to):
   ```
   pip install requests
   python meta_setup.py APP_ID APP_SECRET TOKEN
   ```
   Yeh teen cheezein print karega: `FB_PAGE_ID`, `IG_USER_ID`, `META_PAGE_TOKEN`. Yeh Page token expire nahi hota.
5. GitHub repo > **Settings > Secrets and variables > Actions > New repository secret**. Teeno isi naam se daalo:
   - `META_PAGE_TOKEN`
   - `FB_PAGE_ID`
   - `IG_USER_ID`
6. Test: Actions > Daily reel > Run workflow (date khaali). Instagram aur Facebook par reel aa jani chahiye.

**Ahem:** Facebook ka password ya App Secret kabhi kisi ko mat do, aur secrets sirf GitHub Secrets mein rakho, kisi file mein nahi.

---

## Qadam 3: YouTube Shorts (do raaste)

**Raasta A, aasaan:** Har mahine ke shuru mein Actions > **Batch of reels** > Run workflow > `from` mein mahine ki pehli tareekh, `days` mein 30. Run khatam hone par Artifacts se 30 reels aur captions download karo, aur YouTube Studio mein ek saath upload karke har din ki tareekh par **schedule** kar do. Mahine mein takreeban 20 minute. **TikTok** ke liye bhi yahi tareeqa.

**Raasta B, automatic:** Google ka API YouTube par seedha upload kar sakta hai, lekin Google naye API projects ki videos ko tab tak **private** rakhta hai jab tak project ka "YouTube API audit" approve na ho (form muft hai, jawab aane mein hafte lag sakte hain).
1. console.cloud.google.com > naya project > **YouTube Data API v3** enable karo.
2. **OAuth consent screen**: External, app ka naam Zikartone, apna email. Phir "Publish app" (Testing mode mein token 7 din mein khatam ho jata hai).
3. **Credentials > Create credentials > OAuth client ID > Desktop app**, JSON download karo.
4. Laptop par:
   ```
   pip install google-auth-oauthlib
   python get_youtube_token.py client_secret.json
   ```
   Browser mein YouTube channel chuno aur allow karo. Teen values print hongi.
5. GitHub Secrets mein daalo: `YT_CLIENT_ID`, `YT_CLIENT_SECRET`, `YT_REFRESH_TOKEN`.
6. Audit approve hone tak repo > Settings > Secrets and variables > Actions > **Variables** mein `YT_PRIVACY` = `private` rakh do. Approve hone ke baad yeh variable hata do.

---

## Roz kya hota hai

- 7:00 PM: GitHub reel banata hai (takreeban 3 minute).
- Phir Instagram, Facebook aur YouTube (jo set ho) par post karta hai. Agar ek jagah fail ho to baqi chalti rehti hain.
- `posted.log` mein ek line likh deta hai. Isi se GitHub ko pata rehta hai ke repo zinda hai, warna GitHub 60 din baad scheduled kaam rok deta hai.

## Kuch badalna ho to

- **Waqt badalna:** `.github/workflows/daily.yml` mein `cron: '0 14 * * *'`. 14 = UTC. Pakistan time = UTC + 5. Maslan raat 9 baje ke liye `0 16 * * *`.
- **Caption badalna:** `make_reel.py` mein `HOOKS` aur `TAGS`.
- **Kisi din ki reel dobara chalani:** Actions > Daily reel > Run workflow > woh date.
- **Koi masla ho:** Actions mein laal nishaan wala run kholo, aakhri laal step ka text copy karke kisi developer ya AI ko dikhao.

## Files

| File | Kaam |
|---|---|
| `bank.py` | Saal bhar ke 365 din ke sawal banata aur har sawal check karta hai (ek bhi ghalat ho to reel nahi banti) |
| `make_reel.py` | Us din ki reel banata hai: video, caption, title |
| `assets/template.html` | Design. Fonts, logo aur Qur'an ka text `setup_assets.sh` har run par download karta hai |
| `audio.py` | Tick, whoosh aur chime ki awaaz (music nahi) |
| `upload_meta.py` | Instagram + Facebook par post |
| `upload_youtube.py` | YouTube Shorts par post |
| `meta_setup.py`, `get_youtube_token.py` | Sirf ek dafa, tokens nikaalne ke liye |
