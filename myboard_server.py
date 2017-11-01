#2017.10.05
#merge main.py, googleLogin.py

#flask
import flask
from flask import Flask, render_template,jsonify
from flaskext.mysql import MySQL

#google oauth2
import json
import uuid
import httplib2
from apiclient import discovery
from oauth2client import client
# import API

#
from selenium import webdriver
import time, re
from flask_restful import Resource, Api
from flask_restful import reqparse

app = flask.Flask(__name__, static_folder='assets')
mysql = MySQL()
api = Api(app)

@app.route('/')
def index():
  if 'credentials' not in flask.session:
    return(flask.redirect(flask.url_for('oauth2callback')))
  credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
  if credentials.access_token_expired:
    return(flask.redirect(flask.url_for('oauth2callback')))
  else:
    http_auth = credentials.authorize(httplib2.Http())
    # drive = discovery.build('drive', 'v2', http_auth)
    # files = drive.files().list().execute()
    # return(json.dumps(files))
    return(flask.redirect(flask.url_for('dashboard')))

@app.route('/oauth2callback/')
def oauth2callback():
  #print(flask.url_for('oauth2callback', _external=True))
  flow = client.flow_from_clientsecrets(
      filename='./client_secrets.json',
      # scope='https://www.googleapis.com/auth/drive.metadata.readonly',
      scope = 'email',
      redirect_uri=flask.url_for('oauth2callback', _external=True))
  if 'code' not in flask.request.args:
    auth_uri = flow.step1_get_authorize_url()
    return(flask.redirect(auth_uri))
  else:
    auth_code = flask.request.args.get('code')
    credentials = flow.step2_exchange(auth_code)
    flask.session['credentials'] =  credentials.to_json()
    #DB insert
    googleInfo = json.loads(flask.session['credentials'])
    print(googleInfo['access_token'])
    print(googleInfo['id_token']['email'])
    
    return(flask.redirect(flask.url_for('index')))

@app.route('/dashboard')
def dashboard():
  return(render_template('dashboard.html'))

@app.route('/<name>')
def test(name = None):
  return(render_template(name+'.html'))


#################APIAPIAPIAPIAPIAPIAPIAPIA#########################
def inspector(inputjson):
  driver = webdriver.PhantomJS('./PhantomJS.exe')
  data = json.loads(inputjson)
  driver.get(data["url"])
  body = driver.find_element_by_css_selector(data['body_selector'])
  rst = list()
  for i in range(len(data["segments"])):
    rst.append(body.find_element_by_css_selector(data["segments"][i]['selector']).text)
  driver.close()
  return(rst)

def selectSQL(query): #return
  try:
    cursor.execute(query)
    columns = cursor.description 
    result = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
    return(result)
  except Exception as e:
    return({'error':str(e)})

def executeSQL(query, parameter):
  try:
    cursor.execute(query, parameter)
    conn.commit()
    return({'StatusCode': '200', 'query': query%parameter})
  except Exception as e:
    return({'error':str(e)})

class myboardAPI(Resource):
  def get(self):
    query = "SELECT user_id,name,caption,description,type,url,api_json from myboard.api"
    return(selectSQL(query))
  def post(self):
    try:
      #parsing
      jsondata = request.get_json(force=True)
      _apiUser_id = jsondata['user_id']
      _apiName = jsondata['name']
      _apiCaption = jsondata['caption']
      _apiDescription = jsondata['description']
      _apiType = jsondata['type']
      _apiApi_json = jsondata['api_json']
      _apiUrl = jsondata['url']
      query = "INSERT INTO myboard.api (id, user_id, name, caption, description, type, url, api_json, created_time) VALUES (null, %s, %s, %s, %s, %s, %s, %s, now())"
      return(executeSQL(query, (_apiUser_id, _apiName, _apiCaption, _apiDescription, _apiType, _apiUrl, _apiApi_json)))
    except Exception as e:
      return({'error':str(e)})
  def put(self):
    jsondata = request.get_json(force=True)
    _apiChange_name = jsondata['change_name']
    _apiCaption = jsondata['caption']
    _apiDescription = jsondata['description']
    _apiType = jsondata['type']
    _apiUrl = jsondata['url']
    _apiApi_json = jsondata['api_json']
    _apiUser_id = jsondata['user_id']
    _apiName = jsondata['name']

    query = "UPDATE myboard.api SET name = %s, caption = %s, description = %s, type = %s, url = %s, api_json = %s, created_time = now()  WHERE user_id = %s and name = %s"
    return(executeSQL(query, (_apiChange_name,_apiCaption,_apiDescription,_apiType,_apiUrl,_apiApi_json,_apiUser_id,_apiName )))
  def delete(self):
    jsondata = request.get_json(force=True)
    _apiUser_id = jsondata['user_id']
    _apiName = jsondata['name']
    query = "DELETE FROM myboard.api WHERE user_id = %s and name = %s"
    return(executeSQL(query, (_apiUser_id,_apiName)))

class inspectorAPI(Resource):
  def get(self, user, api):
    user_id = user
    name = api
    query = "SELECT api_json FROM myboard.api WHERE name=%s and user_id=%s"
    getjson = selectSQL(query,(name,user_id))
    return(inspector(str(getjson[0][0])))

class widgetAPI(Resource):
  def get(self): #list, search  #뒤에 변수값 있으면 search, null이면 list
    query = ""
    return(executeSQL(query))
  def post(self): #insert
    query = ""
    return(insertSQL(query))
  def put(self): #update
    query = ""
    return(executeSQL(query))
  def delete(self):
    query = ""
    return(executeSQL(query))

class dashboardAPI(Resource):
  def get(self): #dashboard list
    query = ""
    return(executeSQL(query))
  def post(self): #insert
    query = ""
    return(insertSQL(query))
  def delete(self): #del
    query = ""
    return(executeSQL(query))

api.add_resource(myboardAPI, '/myboardapi')
api.add_resource(inspectorAPI, '/inspectorapi/<user>/<api>')
api.add_resource(widgetAPI, '/widgetapi')
api.add_resource(dashboardAPI, '/dashboardapi')

if __name__ == '__main__':
  #MySQL configurations
  app.config.from_object(__name__)
  app.config.from_envvar('MYBOARD_SETTINGS', silent=False)
  mysql.init_app(app)
  conn = mysql.connect()
  cursor = conn.cursor()

  app.secret_key = str(uuid.uuid4())
  app.debug = False
  app.run()