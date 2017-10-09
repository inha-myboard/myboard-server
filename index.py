#2017.10.05
#merge main.py, googleLogin.py

#flask
import flask
from flask import Flask, render_template, request
from flask.ext.mysql import MySQL

#google oauth2
import json
import uuid
import httplib2
from apiclient import discovery
from oauth2client import client

app = flask.Flask(__name__)
mysql = MySQL()

@app.route('/')
def index():
  if 'credentials' not in flask.session:
    return(flask.redirect(flask.url_for('oauth2callback')))
  credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
  if credentials.access_token_expired:
    return(flask.redirect(flask.url_for('oauth2callback')))
  else:
    http_auth = credentials.authorize(httplib2.Http())
    drive = discovery.build('drive', 'v2', http_auth)
    files = drive.files().list().execute()
    return(json.dumps(files))

@app.route('/oauth2callback/')
def oauth2callback():
  #print(flask.url_for('oauth2callback', _external=True))
  flow = client.flow_from_clientsecrets(
      filename='./client_secrets.json',
      scope='https://www.googleapis.com/auth/drive.metadata.readonly',
      redirect_uri=flask.url_for('oauth2callback', _external=True))
  if 'code' not in flask.request.args:
    auth_uri = flow.step1_get_authorize_url()
    return(flask.redirect(auth_uri))
  else:
    auth_code = flask.request.args.get('code')
    credentials = flow.step2_exchange(auth_code)
    flask.session['credentials'] = credentials.to_json()
    #return(flask.redirect(flask.url_for('index')))
    return(flask.redirect(flask.url_for('dashboard')))

@app.route('/dashboard')
def dashboard():
	return(render_template('dashboard.html'))

@app.route('/<name>')
def test(name = None):
	return(render_template(name+'.html'))

if __name__ == '__main__':
	#MySQL configurations
	app.config['MYSQL_DATABASE_USER'] = 'root'
	app.config['MYSQL_DATABASE_PASSWORD'] = '1234'
	app.config['MYSQL_DATABASE_DB'] = 'mydb'
	app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
	mysql.init_app(app)
	mysql.connect()
	
	app.secret_key = str(uuid.uuid4())
	app.debug = False
	app.run()