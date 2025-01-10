import sqlite3
from cachelib import FileSystemCache

from flask import Flask, render_template, request, redirect, url_for, flash, session, redirect, url_for
from future.backports.datetime import timedelta

from flask_session import Session
conn = sqlite3.connect('data.db', check_same_thread=False)
cursor = conn.cursor()

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'cachelib'
app.config['SESSION_CACHELIB'] = FileSystemCache(cache_dir='flask_session', threshold=500)
Session(app)



@app.route('/')
def main():
    cursor.execute('SELECT * FROM data')
    data = cursor.fetchall()
    return render_template('main.html', data=data)

@app.route('/register/', methods=['POST', 'GET'])
def page_reg():
    return render_template('register.html')

@app.route('/login/')
def login():
    data = cursor.fetchall()
    return render_template('login.html',data=data)

@app.route('/add/')
def add():
    #if 'login' not in session:
    #    flash('Необ')
    return render_template('add.html')

@app.route('/upload/', methods=['POST'])
def save_post():
    image = request.files.get('image')
    title = request.form['title']
    file_name = f'static/uploads/{image.filename}'
    description = request.form['description']
    image.save(file_name)
    cursor.execute(f'INSERT INTO data (title, file_name, description) VALUES (?,?,?)',
                        [title, file_name, description])
    conn.commit()

    return redirect(url_for('main'))

@app.route('/save_register/', methods=['POST', "GET"])
def save_reg():
    if request.method == 'POST':
        last_name = request.form['last_name']
        name = request.form['name']
        patronymic = request.form['patronymic']
        gender = request.form['gender']
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']
        cursor.execute(f'INSERT INTO autorisation (last_name, name, patronymic, gender, email, username, password) VALUES (?,?,?,?,?,?,?)',
                        [last_name, name, patronymic, gender, email, username, password])
        conn.commit()
        return redirect(url_for('login'))

@app.route('/authorization/', methods=['GET', 'POST'])
def autorisation():
    if request.method == 'POST':
        login = request.form['username']
        cursor.execute('select username, password from autorisation where username=(?)',[login])
        data = cursor.fetchall()

        if len(data) != 0:
            session['login'] = True
            session['username'] = login
            session.permanent = False
            app.permanent_session_lifetime = timedelta(minutes=1)
            session.modified = True
            flash('Вход выполнен успешно!', 'success')
            return redirect(url_for('main'))
        else:
            flash('неправильный логин или пароль', 'danger')
            return render_template('login.html')
        return render_template('autorisation.html')

@app.route("/logout/")
def logout():
    session.clear()
    flash('Вы вышли из профиля', 'danger')
    return redirect(url_for("login"))

app.run(debug=True)