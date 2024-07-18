from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, User
import re

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key2'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()
    
def validate_password(password):
    errors = []
    if len(password) < 8:
        errors.append("Password should be at least 8 characters.")
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain a lowercase letter.")
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain an uppercase letter.")
    if not re.search(r'\d$', password):
        errors.append("Password must end with a number.")
    return errors


@app.route('/')
def index():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()
    errors = validate_password(password)
    
    if user and user.password == password and not errors:
        user.failed_attempts = 0
        db.session.commit()
        return render_template('SecretPage.html')
    else:
        if user:
            user.failed_attempts += 1
            db.session.commit()
            if user.failed_attempts >= 3:
                errors.append("3 or more consecutive failed attempts. Please try again later.")

        for error in errors:
            flash(error)
        return redirect(url_for('index'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        errors = validate_password(password)

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            errors.append("Email address is already used.")
        
        if errors:
            for error in errors:
                flash(error)
            return redirect(url_for('signup'))
        
        new_user = User(first_name=first_name, last_name=last_name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return render_template('ThankYou.html')
    
    return render_template('signup.html')


if __name__ == '__main__':
    app.run(debug=True)
