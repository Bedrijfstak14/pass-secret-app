from flask import Flask, request, redirect, render_template
from models import db, Secret
from utils import encrypt, decrypt
import os
import uuid

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///secrets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form['secret']
        views = int(request.form['views'])   # gebruiker telt ook mee
        data, nonce = encrypt(text.encode())
        unique_id = uuid.uuid4().hex  # moeilijk te raden link
        secret = Secret(id=unique_id, data=data, nonce=nonce, views_left=views)
        db.session.add(secret)
        db.session.commit()
        link = request.host_url + unique_id
        return render_template('confirm.html', link=link, views=views - 1)
    return render_template('index.html')

@app.route('/<secret_id>')
def view(secret_id):
    secret = Secret.query.get_or_404(secret_id)
    if secret.views_left <= 0:
        db.session.delete(secret)
        db.session.commit()
        return render_template('view.html', secret=None, expired=True)
    text = decrypt(secret.data, secret.nonce)
    secret.views_left -= 1
    db.session.add(secret)
    if secret.views_left <= 0:
        db.session.delete(secret)
    db.session.commit()
    return render_template('view.html', secret=text.decode(), expired=False)

@app.route('/cleanup')
def cleanup():
    expired = Secret.query.filter(Secret.views_left <= 0).all()
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
