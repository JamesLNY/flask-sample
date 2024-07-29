import os
import datetime
from flask import Flask, request, session, render_template
from main.db import getDB

app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
  SECRET_KEY='dev',
  DATABASE=os.path.join(app.instance_path, 'db.sqlite')
)

app.config.from_pyfile('config.py', silent=True)

try:
  os.makedirs(app.instance_path)
except OSError:
  pass

from . import db
db.initApp(app)
from . import auth
app.register_blueprint(auth.bp)

@app.route('/index', methods=('GET', 'POST'))
def index():
  db = getDB()
  user_id = session.get('user_id')
  if request.method == 'POST':
    if 'addRequest' in request.form:
      return render_template('requestForm.html')
    else:
      assignmentLink = request.form['assignmentLink']
      documentLink = request.form['documentLink']
      db.execute(
        "INSERT INTO requests (assignmentLink, documentLink, time, status, id) VALUES (?, ?, ?, ?, ?)",
        (assignmentLink, documentLink, datetime.date.today(), "Not Started", user_id)
      )
      db.commit()
  requests = db.execute('SELECT * FROM requests WHERE id = ?', (user_id,))
  return render_template('index.html', userRequests=requests)

@app.route('/editor', methods=('GET', 'POST'))
def editor():
  db = getDB()
  user_id = session.get('user_id')
  if request.method == 'POST':
    if 'submitApplication' in request.form:
      password = request.form['password']
      if password == 'hello':
        db.execute("UPDATE user SET editor = ? WHERE id = ?", (True, user_id))
        db.commit()
      else:
        flash('Incorrect password')
        return render_template('editorForm.html')
    else:
      requestID = request.form['updateStatus'][7:]
      currentStatus = db.execute('SELECT * FROM requests WHERE requestID = ?', (requestID,)).fetchone()
      if currentStatus['status'] == "Not Started":
        db.execute("UPDATE requests SET status = ?, editorID = ? WHERE requestID = ?", ("In Progress", user_id, requestID))
      else:
        db.execute("UPDATE requests SET status = ? WHERE requestID = ?", ("Finished", requestID))
      db.commit()
  else:
    editor = db.execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()
    if editor == None or editor['editor'] != True:
      return render_template('editorForm.html')
  requests = db.execute('SELECT * FROM requests WHERE status != ?', ("Finished",))
  return render_template('editor.html', userRequests = requests)