from flask import Flask, request, redirect, render_template, send_from_directory, Response
from models import db, Secret
from utils import encrypt, decrypt
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime, timedelta, timezone
import sqlite3
from functools import wraps

load_dotenv()
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///secrets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

BACKGROUND_COLOR = os.getenv("BACKGROUND_COLOR", "#ffffff")
BUTTON_COLOR = os.getenv("BUTTON_COLOR", "#007bff")

@app.context_processor
def inject_theme_colors():
    return {
        "background_color": BACKGROUND_COLOR,
        "button_color": BUTTON_COLOR
    }

def log_event(secret_id, event_type):
    conn = sqlite3.connect('secrets.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            secret_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    c.execute(
        "INSERT INTO events (secret_id, event_type) VALUES (?, ?)",
        (secret_id, event_type)
    )
    conn.commit()
    conn.close()

ADMIN_USER = os.getenv("ADMIN_USERNAME")
ADMIN_PASS = os.getenv("ADMIN_PASSWORD")

def check_auth(username, password):
    return username == ADMIN_USER and password == ADMIN_PASS

def authenticate():
    return Response('Toegang geweigerd', 401, {'WWW-Authenticate': 'Basic realm="Beheer"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/static/style.css')
def dynamic_css():
    return render_template("style.css.j2"), 200, {'Content-Type': 'text/css'}

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form['secret']
        views = int(request.form['views'])
        expire_minutes = request.form.get('expire_minutes')

        expire_at = None
        if expire_minutes:
            try:
                expire_at = datetime.now(timezone.utc) + timedelta(minutes=int(expire_minutes))
            except ValueError:
                pass

        data, nonce = encrypt(text.encode())
        unique_id = uuid.uuid4().hex
        secret = Secret(
            id=unique_id,
            data=data,
            nonce=nonce,
            views_left=views,
            expire_at=expire_at
        )
        db.session.add(secret)
        db.session.commit()
        log_event(unique_id, 'created')

        host = request.host_url.replace("http://", "https://")
        link = host + unique_id
        return render_template(
            'confirm.html',
            link=link,
            views=views - 1,
            expire_at=expire_at.strftime("%Y-%m-%d %H:%M UTC") if expire_at else None
        )

    return render_template('index.html')

@app.route('/<secret_id>')
def view(secret_id):
    secret = Secret.query.get_or_404(secret_id)

    if secret.expire_at and datetime.utcnow() > secret.expire_at:
        db.session.delete(secret)
        db.session.commit()
        log_event(secret_id, 'deleted')
        return render_template('view.html', secret=None, expired=True)

    if secret.views_left <= 0:
        db.session.delete(secret)
        db.session.commit()
        log_event(secret_id, 'deleted')
        return render_template('view.html', secret=None, expired=True)

    text = decrypt(secret.data, secret.nonce)
    secret.views_left -= 1

    if secret.views_left <= 0:
        db.session.delete(secret)
        log_event(secret_id, 'deleted')
    else:
        db.session.add(secret)

    db.session.commit()
    log_event(secret_id, 'viewed')

    return render_template(
        'view.html',
        secret=text.decode(),
        expired=False,
        expire_at=secret.expire_at.strftime("%Y-%m-%d %H:%M UTC") if secret.expire_at else None
    )

@app.route('/cleanup')
def cleanup():
    now = datetime.utcnow()
    expired = Secret.query.filter(
        (Secret.views_left <= 0) |
        ((Secret.expire_at != None) & (Secret.expire_at < now))
    ).all()

    count = len(expired)
    for s in expired:
        log_event(s.id, 'deleted')
        db.session.delete(s)
    db.session.commit()

    return f"✅ Cleaned {count} expired secrets."

@app.route('/admin/stats')
@requires_auth
def admin_stats():
    conn = sqlite3.connect('secrets.db')
    c = conn.cursor()

    c.execute("""
        SELECT DATE(timestamp), COUNT(*) FROM events
        WHERE event_type = 'created'
        GROUP BY DATE(timestamp)
        ORDER BY DATE(timestamp) DESC
        LIMIT 7
    """)
    created_per_day = c.fetchall()

    c.execute("SELECT COUNT(*) FROM events WHERE event_type = 'viewed'")
    total_views = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM events WHERE event_type = 'created'")
    total_created = c.fetchone()[0]

    average_views = round(total_views / total_created, 2) if total_created > 0 else 0

    c.execute("SELECT COUNT(DISTINCT secret_id) FROM events WHERE event_type = 'created'")
    created_ids = c.fetchone()[0]
    c.execute("SELECT COUNT(DISTINCT secret_id) FROM events WHERE event_type = 'deleted'")
    deleted_ids = c.fetchone()[0]
    active_secrets = created_ids - deleted_ids

    conn.close()

    return render_template("stats.html",
        created_per_day=created_per_day,
        total_views=total_views,
        total_created=total_created,
        average_views=average_views,
        active_secrets=active_secrets
    )

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

def create_app():
    with app.app_context():
        db.create_all()

        # Extra: events-tabel aanmaken
        conn = sqlite3.connect('secrets.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                secret_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    return app


if __name__ == '__main__':
    create_app()
    app.run(host="0.0.0.0", port=5000)
