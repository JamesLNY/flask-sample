import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from main.db import getDB

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
  if request.method == 'POST':
    email = request.form['email']
    password = request.form['password']
    db = getDB()
    try:
      db.execute(
        "INSERT INTO user (email, password) VALUES (?, ?)",
        (email, generate_password_hash(password))
      )
      db.commit()
    except db.IntegrityError:
      flash(f"Email {email} is already registered.")
    else:
      return redirect(url_for("auth.login"))
  return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
  if request.method == 'POST':
    email = request.form['email']
    password = request.form['password']
    db = getDB()
    user = db.execute('SELECT * FROM user WHERE email = ?', (email,)).fetchone()
    if user is None:
      flash('Incorrect email')
    elif not check_password_hash(user['password'], password):
      flash('Incorrect password')
    else:
      session.clear()
      session['user_id'] = user['id']
      return redirect(url_for('index'))
  return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
  user_id = session.get('user_id')
  if user_id is None:
    g.user = None
  else:
    g.user = getDB().execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()

@bp.route('/logout')
def logout():
  session.clear()
  return redirect(url_for('auth.login'))

def login_required(view):
  @functools.wraps(view)
  def wrapped_view(**kwargs):
    if g.user is None:
      return redirect(url_for('auth.login'))
    return view(**kwargs)
  return wrapped_view