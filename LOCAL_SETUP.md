# InstaReposter - Local Setup Guide

Quick guide to run InstaReposter on your local machine.

## Prerequisites

- Python 3.10+
- Redis (or use your Upstash cloud Redis)
- ngrok account (free tier works)

---

## 1. Install Dependencies

```powershell
cd d:\python_projs\reposter_bot
.\venv\Scripts\activate
pip install -r requirements.txt
```

---

## 2. Configure Environment

Edit `.env` file with your credentials:

```env
IG_BUSINESS_ACCOUNT_ID=your_instagram_business_id
IG_PAGE_ACCESS_TOKEN=your_page_access_token
REDIS_URL=redis://localhost:6379/0  # or your Upstash URL
NGROK_URL=  # Will be set in step 4
```

---

## 3. Start Redis (Skip if using Upstash)

**Option A: Docker**
```powershell
docker run -d -p 6379:6379 redis:alpine
```

**Option B: Windows WSL**
```bash
sudo apt install redis-server
sudo service redis-server start
```

**Option C: Upstash (Cloud)**
Your `.env` already has an Upstash URL configured - no local Redis needed!

---

## 4. Start ngrok Tunnel

ngrok creates a public URL so Meta's servers can fetch your downloaded media.

```powershell
ngrok http 8000
```

Copy the HTTPS forwarding URL (e.g., `https://abc123.ngrok-free.app`) and update your `.env`:

```env
NGROK_URL=https://abc123.ngrok-free.app
```

> ⚠️ **Important**: Update `NGROK_URL` every time you restart ngrok (URL changes each time).

---

## 5. Start Django Server

```powershell
cd d:\python_projs\reposter_bot
.\venv\Scripts\activate
python manage.py runserver 8000
```

---

## 6. Start Celery Worker (New Terminal)

```powershell
cd d:\python_projs\reposter_bot
.\venv\Scripts\activate
celery -A myproject worker --loglevel=info --pool=solo
```

> Note: `--pool=solo` is required on Windows.

---

## 7. Use the App

Open your browser to: **http://127.0.0.1:8000**

1. Paste an Instagram Reel/Post/Video URL
2. Click "Start Repost"
3. Watch the progress bar update in real-time
4. Media will be published to your Instagram Business Account

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "NGROK_URL not configured" | Set `NGROK_URL` in `.env` with your ngrok URL |
| "Container Error" from Meta | Check your access token is valid and not expired |
| Celery not receiving tasks | Verify Redis URL is correct and Redis is running |
| Media download fails | Ensure yt-dlp is installed: `pip install yt-dlp` |

---

## Getting Meta API Credentials

1. Go to [Meta for Developers](https://developers.facebook.com)
2. Create/select your app
3. Add Instagram Graph API product
4. Generate a Page Access Token with `instagram_content_publish` permission
5. Get your Instagram Business Account ID from the API Explorer
