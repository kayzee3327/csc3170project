import functools
import mysql.connector

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from libsys.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']
        fullname = request.form['fullname']
        email = request.form['email']
        db = get_db()
        c = db.cursor()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif not password == confirm:
            error = 'Please confirm your password.'

        if error is None:
            try:
                c.execute(
                    "INSERT INTO users (username, password, role, full_name, email) VALUES (%s, %s, %s, %s, %s)",
                    (username, password, 'patron', fullname, email),
                )
                db.commit()
                return redirect(url_for("auth.login"))
            except mysql.connector.IntegrityError:
                error = f"Username {username} is registered."
        
        flash(error)
        return redirect(url_for('auth.register'))
    return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        c = db.cursor()
        error = None

        c.execute(
            'SELECT * FROM users WHERE username = %s and role = \'patron\'', (username,)
        )

        user = c.fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not user[2] == password:
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user[0]
            return redirect(url_for('index'))
        else:
            flash(error)
            return redirect(url_for('auth.login'))

    return render_template('auth/login.html')

@bp.route('/librarian', methods=('GET', 'POST'))
def librarian():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        c = db.cursor()
        error = None

        c.execute(
            'SELECT * FROM users WHERE username = %s and role = \'librarian\'', (username,)
        )

        user = c.fetchone()

        if user is None:
            error = 'Incorrect librarian username.'
        elif not user[2] == password:
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user[0]
            return redirect(url_for('librarian.index'))
        else:
            flash(error)
            return redirect(url_for('auth.librarian'))

    return render_template('auth/librarian.html')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        db = get_db()
        c = db.cursor()

        c.execute(
            'SELECT * FROM users WHERE id = %s', (user_id,)
        )

        u = c.fetchone()
        g.user = {
            'username': u[1],
            'password': u[2],
            'role': u[3],
            'fullname': u[4],
            'email': u[5]
        }

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None or g.user['role'] != 'patron':
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

def admin_login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None or g.user['role'] != 'librarian':
            return redirect(url_for('auth.librarian'))
        return view(**kwargs)
    return wrapped_view