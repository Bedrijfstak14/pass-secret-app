from flask import Flask, request, redirect, render_template, send_from_directory
from models import db, Secret
from utils import encrypt, decrypt
from dotenv import load_dotenv
import os
import uuid
from datetime import datetime, timedelta

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

        # Tijdslimiet verwerken
        expire_at = None
        if expire_minutes:
            try:
                expire_at = datetime.utcnow() + timedelta(minutes=int(expire_minutes))
            except ValueError:
                pass  # Ongeldige invoer negeren

        # Encryptie en opslag
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

    # Tijdslimiet controleren
    if secret.expire_at and datetime.utcnow() > secret.expire_at:
        db.session.delete(secret)
        db.session.commit()
        return render_template('view.html', secret=None, expired=True)

    # Aantal views controleren
    if secret.views_left <= 0:
        db.session.delete(secret)
        db.session.commit()
        return render_template('view.html', secret=None, expired=True)

    # Geheim decrypten en tonen
    text = decrypt(secret.data, secret.nonce)
    secret.views_left -= 1

    if secret.views_left <= 0:
        db.session.delete(secret)
    else:
        db.session.add(secret)

    db.session.commit()
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
        db.session.delete(s)
    db.session.commit()

    return f"✅ Cleaned {count} expired secrets."

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404

def create_app():
    with app.app_context():
        db.create_all()
    return app

if __name__ == '__main__':
    create_app()
    app.run(host="0.0.0.0", port=5000)
