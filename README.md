# 🎵 Telegram Qo'shiq Bot (@musiqazuxibot)

Ushbu bot Telegram orqali istalgan qo'shiqni qidirish, eng yaxshi top 10 ta variantni taqdim etish va bir bosishda MP3 formatida yuklab berish imkoniyatiga ega.

---

## ⚡ Asosiy Xususiyatlari

- **Tezkor qidiruv (1-2 soniya):** `yt-dlp` flat-extraction orqali ortiqcha ma'lumotlarsiz eng mos top 10 ta trekni darhol topadi.
- **Top 10 Inline Tugmalar:** Har bir qo'shiq uchun alohida raqamli tugma mavjud.
- **Tezkor MP3 yuklash:** Qo'shiqni eng yaxshi audio sifatda yuklab olib, ijrochi va sarlavhasi bilan Telegram Audio sifatida yuboradi.
- **Xotira va kesh tizimi:** 
  - Yuklangan qo'shiqlar Telegram File ID keshi orqali saqlanadi, qayta so'ralganda 0.1 soniyada yuklab bermasdan yuboradi!
  - Server xotirasi (disk) to'lmasligi uchun yuklangan vaqtinchalik audio fayllar darhol tozalanadi.
- **Render.com ga 100% mos:** Render Web Service port talab qiladi. Bot bilan bir vaqtda yengil HTTP healthcheck serveri ishlaydi.

---

## 💻 Kompyuterda (Lokal) Ishga Tushirish

1. **Kutubxonalarni o'rnatish:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Botni ishga tushirish:**
   ```bash
   python bot.py
   ```

---

## 🌐 Render.com ga Joylash (Deploy) Qo'llanmasi

Bot Render.com bepul tarifida 24/7 ishlashi uchun to'liq moslashtirilgan.

### 1-Usul: GitHub orqali Render Web Service (Docker bilan - Eng yaxshi usul)

1. Ushbu loyiha fayllarini o'zingizning **GitHub** akkauntingizdagi yangi repository'ga yuklang:
   ```bash
   git init
   git add .
   git commit -m "Telegram music bot"
   git branch -M main
   git remote add origin https://github.com/USERNAME/REPO_NAME.git
   git push -u origin main
   ```

2. [Render.com](https://dashboard.render.com/) ga kiring va **"New +" -> "Web Service"** tugmasini bosing.
3. GitHub repository'ingizni ulang.
4. Sozlamalarda:
   - **Language / Environment:** `Docker` (loyihadagi `Dockerfile` avtomatik aniqlanadi va FFmpeg bilan birga o'rnatiladi).
   - **Instance Type:** `Free` (bepul).
5. **Environment Variables** (Muhit o'zgaruvchilari) bo'limiga:
   - `BOT_TOKEN` = `8539604514:AAGz3fFAI1WHOYFkyS0SAk74RMs00bjh1es`
   - `PORT` = `8080`
6. **"Deploy Web Service"** tugmasini bosing!

Render loyihangizni bir necha daqiqada qurib, botni ishga tushiradi.

---

### 💡 Botni 24/7 uxlab qolmasdan ishlashini ta'minlash (Render Free Tier)
Render bepul xizmatlari 15 daqiqa davomida so'rov kelmasa uxlab qolishi mumkin. Buni oldini olish uchun:
- Render bergan manzilni (masalan: `https://telegram-music-bot.onrender.com/health`) oling.
- [UptimeRobot.com](https://uptimerobot.com/) saytiga bepul a'zo bo'lib, ushbu manzilni har 5 daqiqada ping (HTTP monitor) qilib turadigan qilib qo'ying. Bot hech qachon to'xtamaydi!
