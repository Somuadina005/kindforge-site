# KINDFORGE website + contact backend

Flask serves the site (`static/index.html`) and receives the "Let's connect" form at `POST /api/contact`.
Each submission is emailed to kindforgetech@gmail.com. The Reply-To is the visitor's email, so hitting Reply in Gmail answers them.

## Set up the Gmail app password
1. Sign in to kindforgetech@gmail.com and turn on 2-Step Verification.
2. Go to https://myaccount.google.com/apppasswords and create an app password named "KINDFORGE website".
3. Copy the 16 characters into `GMAIL_APP_PASSWORD` (no spaces needed).

## Run locally
    pip install -r requirements.txt
    cp .env.example .env     # then fill in GMAIL_APP_PASSWORD
    python app.py            # http://localhost:5000

## Deploy (Render, Railway, Fly.io, or any host that runs Python)
- Start command: `gunicorn app:app`
- Set the three variables from `.env.example` in the host's environment settings. Never commit `.env`.
- Point kindforge.org at the deployed app. HTTPS is provided by the host.

## Notes
- Spam protection: a hidden honeypot field and 5 messages per hour per IP (in memory, resets on restart).
- If you run more than one worker, move the rate limit to Redis or add a form-level captcha.
