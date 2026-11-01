import os, re, smtplib, time
from collections import defaultdict, deque
from email.message import EmailMessage
from flask import Flask, jsonify, request

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = Flask(__name__, static_folder="static", static_url_path="")

ROLES = {"Investor", "Funder or grant body", "Partner organization",
         "School or counselor", "Parent", "Press", "Other"}
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
HITS = defaultdict(deque)           # ip -> timestamps
LIMIT, WINDOW = 5, 3600             # 5 messages per hour per IP


def one_line(s, n):
    return re.sub(r"[\r\n]+", " ", str(s)).strip()[:n]


def too_many(ip):
    now, q = time.time(), HITS[ip]
    while q and now - q[0] > WINDOW:
        q.popleft()
    if len(q) >= LIMIT:
        return True
    q.append(now)
    return False


def send_mail(name, email, role, message):
    user = os.environ["GMAIL_USER"]
    password = os.environ["GMAIL_APP_PASSWORD"]
    to = os.environ.get("CONTACT_TO", "kindforgetech@gmail.com")
    msg = EmailMessage()
    msg["Subject"] = f"KINDFORGE inquiry ({role}) from {name}"
    msg["From"] = f"KINDFORGE Website <{user}>"
    msg["To"] = to
    msg["Reply-To"] = f"{name} <{email}>"   # replying goes to the visitor
    msg.set_content(f"Name: {name}\nEmail: {email}\nI am a: {role}\n\n{message}")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=15) as s:
        s.login(user, password)
        s.send_message(msg)


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.post("/api/contact")
def contact():
    data = request.get_json(silent=True) or {}
    if data.get("website"):                      # honeypot: bots fill this
        return jsonify(ok=True)
    ip = (request.headers.get("X-Forwarded-For", request.remote_addr) or "").split(",")[0].strip()
    if too_many(ip):
        return jsonify(error="Too many messages. Try again later."), 429
    name = one_line(data.get("name", ""), 100)
    email = one_line(data.get("email", ""), 200)
    role = one_line(data.get("role", ""), 50)
    message = str(data.get("message", "")).strip()[:5000]
    if not name or not message or not EMAIL_RE.match(email) or role not in ROLES:
        return jsonify(error="Invalid input."), 400
    try:
        send_mail(name, email, role, message)
    except Exception:
        app.logger.exception("Email send failed")
        return jsonify(error="Could not send."), 502
    return jsonify(ok=True)


if __name__ == "__main__":
    app.run(debug=True, port=5000)



