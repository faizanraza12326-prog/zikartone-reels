#!/usr/bin/env bash
# Downloads the fonts, the Zikartone logo and the Qur'an text. Runs at the start of every GitHub run.
set -e
cd "$(dirname "$0")"
mkdir -p assets/fonts data _tmp
cd _tmp
npm pack @fontsource/amiri-quran@5 @fontsource/poppins@5 quran-json@3 --silent >/dev/null
for t in *.tgz; do mkdir -p x && tar xzf "$t" -C x; done
cp x/package/files/amiri-quran-arabic-400-normal.woff2 x/package/files/poppins-latin-400-normal.woff2 \
   x/package/files/poppins-latin-600-normal.woff2 x/package/files/poppins-latin-800-normal.woff2 ../assets/fonts/
cp x/package/dist/quran_en.json ../data/
cd .. && rm -rf _tmp
curl -fsSL -o assets/logo.png https://zikartone.netlify.app/icon-512.png || echo "logo download failed"
echo "assets ready"
