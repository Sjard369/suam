from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "fallback-secret")

# Sichere DB-URL-Erkennung für Railway
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://")

app.config['SQLALCHEMY_DATABASE_URI'] = db_url or 'sqlite:///db.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(10000), nullable=False)

@app.route('/', methods=['POST', 'GET'])
def homeLogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['username'] = username
            session['user_id'] = user.id
            return redirect('/Startseite')
        else:
            return render_template('login_Error.html')


    return render_template('index.html')

@app.route('/Registrierung', methods=['POST', 'GET'])
def signUp():
    if request.method == 'POST':
        username = request.form['username']
        password1 = request.form['password1']
        password2 = request.form['password2']

        if password1 != password2:
            return render_template('password_Nmatch.html')
        
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            return render_template('existing.html')
        
        hashed_password = generate_password_hash(password1)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return render_template('sign_Erfolg.html')

    return render_template('sign-up.html')

@app.route('/Startseite')
def dashboard():
    if 'user_id' not in session:
        return redirect('/')
    
    return render_template('test.html', username=session['username'])

@app.route('/Kontakt')
def contact():
    if 'user_id' not in session:
        return redirect('/')
    
    return render_template('contact.html', username=session['username'])

@app.route('/Automatisierungen')
def automations():
    if 'user_id' not in session:
        return redirect('/')
    
    return render_template('products.html', username=session['username'])

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)

