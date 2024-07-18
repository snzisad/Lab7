from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import re

app = Flask(__name__)

app.config['SECRET_KEY'] = '8f42a73054b1749f8f58848be5e6502c'
app.config['SESSION_TYPE'] = 'filesystem'

def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')
        conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    username = request.form['username']
    password = request.form['password']

    if 'failed_attempts' not in session:
        session['failed_attempts'] = 0

    errors = check_password(password)
    warning = ""
    if not errors:
        try:
            with sqlite3.connect('database.db') as conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO user (username, password) VALUES (?, ?)', (username, password))
                conn.commit()
            session['failed_attempts'] = 0
            return redirect(url_for('report', result='success'))
        except sqlite3.IntegrityError:
            flash('Username already exists.')
            return redirect(url_for('index'))
    else:
        session['failed_attempts'] += 1
        if session['failed_attempts'] >= 3:
            flash('3 consecutive failed attempts. Please try again later.')
            warning = "3 consecutive failed attempts. Please try again later."
            session['failed_attempts'] = 0
        return redirect(url_for('report', result='failure', errors=errors, warning=warning))

def check_password(password):
    errors = []
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain a lowercase letter.")
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain an uppercase letter.")
    if not re.search(r'\d$', password):
        errors.append("Password must end with a number.")
    return errors

@app.route('/report/<result>')
def report(result):
    errors = request.args.getlist('errors')
    return render_template('report.html', result=result, errors=errors)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
