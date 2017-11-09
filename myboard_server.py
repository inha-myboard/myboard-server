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
    # print(googleInfo['access_token'])
    # print(googleInfo['id_token']['email'])
    try:
      #같은 이메일이 없으면! 인설트.라는걸 체크해줘야하는데 안해줘도 무방?? -> 기능상 문제는 ㄴ 로그인하면 회원에 또 생김.
      query = "INSERT INTO myboard.user (id,email,nickname,access_token) values (null, %s,%s,%s)"
      cursor.execute(query, (googleInfo['id_token']['email'], "뭔 닉넴임?일단 em`ail @앞부분으로 ㄱ?",googleInfo['access_token']))
      conn.commit()
      return(flask.redirect(flask.url_for('index')))
    except Exception as e:
      return({'error':str(e)})

@app.route('/dashboard')
def dashboard():
  return(render_template('dashboard.html'))

@app.route('/<name>')
def test(name = None):
  return(render_template(name+'.html'))


#################APIAPIAPIAPIAPIAPIAPIAPIA#########################

def inspector(inputjson):
  driver = webdriver.PhantomJS('./PhantomJS')
  data = json.loads(inputjson.replace('\'','"'))#json or str to dict

  driver.get(data["url"])
  ui.WebDriverWait(driver, 10).until(lambda browser: driver.find_element_by_tag_name('body'))
  driver.refresh()
  ui.WebDriverWait(driver, 10).until(lambda browser: driver.find_element_by_tag_name('body'))
  rst = list()

  bodyPath = data['body_selector']
  while 1:
    obj = dict()
    try:
      body = driver.find_element_by_css_selector(bodyPath)
    except:
      break
    for j in range(len(data["segments"])):
      temp = dict()
      if data["segments"][j]['selector'].split(' ')[-1][0:3] == 'img':
        try:
          temp['src'] = body.find_element_by_css_selector(data["segments"][j]['selector']).get_attribute('src')
        except:
          pass
        try: #seg에서 맨 마지막 parent가 a라면
          if data["segments"][j]['selector'].split(' ')[-3][0] == 'a':
            href = body.find_element_by_css_selector(data["segments"][j]['selector'][0:(data["segments"][j]['selector'].rfind('>')-1)]).href
            temp['href'] = href
        except: # seg에서 parent tag가 없다면
          pass
          # if data['body_selector'][i].split(' ')[-1][0] == 'a':
          #   href = body.get_attribute('href')
        obj[data["segments"][j]['name']] = temp
      elif data["segments"][j]['selector'].split(' ')[-1][0] == 'a':
        temp['href'] = body.find_element_by_css_selector(data["segments"][j]['selector']).get_attribute('href')
        temp['text'] = body.find_element_by_css_selector(data["segments"][j]['selector']).text
        obj[data["segments"][j]['name']] = temp
      else:
        # text = body.find_element_by_css_selector(data["segments"][j]['selector']).text
        temp['text'] = body.find_element_by_css_selector(data["segments"][j]['selector']).text
        try: #seg에서 맨 마지막 parent가 a라면
          if data["segments"][j]['selector'].split(' ')[-3][0] == 'a':
            href = body.find_element_by_css_selector(data["segments"][j]['selector'][0:(data["segments"][j]['selector'].rfind('>')-1)]).get_attribute('href')
            temp['href'] = href
        except: # seg에서 parent tag가 없다면
          if data['body_selector'].split(' ')[-1][0] == 'a':
            href = body.get_attribute('href')
            temp['href'] = href
        obj[data["segments"][j]['name']] = temp
    rst.append(obj)
    bodyPath = bodyPath + ' + ' + body.tag_name
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
    query = "SELECT id,user_id,name,caption,description,type,url,api_json from myboard.api"
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
    try:
      jsondata = request.get_json(force=True)
      _apiId = jsondata['id']
      _apiChange_name = jsondata['change_name']
      _apiCaption = jsondata['caption']
      _apiDescription = jsondata['description']
      _apiType = jsondata['type']
      _apiUrl = jsondata['url']
      _apiApi_json = jsondata['api_json']
      _apiUser_id = jsondata['user_id']
      # _apiName = jsondata['name']
      query = "UPDATE myboard.api SET name = %s, caption = %s, description = %s, type = %s, url = %s, api_json = %s, created_time = now()  WHERE user_id = %s and id = %s"
      return(executeSQL(query, (_apiChange_name,_apiCaption,_apiDescription,_apiType,_apiUrl,_apiApi_json,_apiUser_id,_apiId )))
    except Exception as e:
      return({'error':str(e)})
  def delete(self):
    jsondata = request.get_json(force=True)
    _apiUser_id = jsondata['user_id']
    _apiId = jsondata['id']
    query = "DELETE FROM myboard.api WHERE user_id = %s and id = %s"
    return(executeSQL(query, (_apiUser_id,_apiId)))

class inspectorAPI(Resource):
  def get(self, user, api):
    user_id = user
    name = api
    query = "SELECT api_json FROM myboard.api WHERE name=%s and user_id=%s"
    getjson = selectSQL(query,(name,user_id))
    return(inspector(str(getjson[0][0])))

class widgetAPI(Resource):
  def get(self): #list, search  #뒤에 변수값 있으면 search, null이면 list
    query = "SELECT id,api_id,user_id,caption,description,mapping_json,created_time from myboard.widget"
    return(selectSQL(query))
  def post(self): #insert 사용자가 위젯을 등록. 현재 DB구조로는 컴포넌트 먼저 등록하고 위젯 등록.
    try:
      #parsing
      jsondata = request.get_json(force=True)
      _apiApi_id = jsondata['api_id']
      _apiUser_id = jsondata['user_id']
      _apiCaption = jsondata['caption']
      _apiDescription = jsondata['description']
      _apiMapping_json = jsondata['mapping_json']
      query = "INSERT INTO myboard.widget (id,api_id,user_id,caption,description,mapping_json,created_time) VALUES (null, %s, %s, %s, %s, %s, now())"
      return(executeSQL(query, ( _apiApi_id, _apiUser_id, _apiCaption, _apiDescription, _apiMapping_json)))
    except Exception as e:
      return({'error':str(e)})
  def put(self): #update
    try:
     jsondata = request.get_json(force=True)
      _apiId = jsondata['id']
      _apiApi_id = jsondata['api_id']
      _apiUser_id = jsondata['user_id']
      _apiCaption = jsondata['caption']
      _apiDescription = jsondata['description']
      _apiMapping_json = jsondata['mapping_json']
      query = "UPDATE myboard.widget SET api_id = %s,user_id = %s,caption = %s,description = %s,mapping_json = %s, created_time = now()  WHERE user_id = %s and id = %s"
      return(executeSQL(query, (_apiApi_id,_apiUser_id,_apiCaption,_apiDescription,_apiMapping_json,_apiUser_id,_apiId )))
    except Exception as e:
      return({'error':str(e)})
  def delete(self): # 사용자가 dashboard에 등록한 위젯을 삭제하는과정. (widget_pos, favorite, widget에서 다 삭제되야함.)
    jsondata = request.get_json(force=True)
    _apiUser_id = jsondata['user_id']
    _apiId = jsondata['id']
    query = "DELETE FROM myboard.api WHERE user_id = %s and id = %s"
    return(executeSQL(query, (_apiUser_id,_apiId)))

class dashboardAPI(Resource):
  def get(self): #dashboard list
    jsondata = request.get_json(force=True)
    _apiUser_id = jsondata['user_id']
    # _apiId = jsondata['id']
    query = "SELECT id, name, order_index FROM myboard.dashboard WHERE user_id=%s"
    return(executeSQL(query, (_apiUser_id)))
  def post(self): #insert
    try:
      jsondata = request.get_json(force=True)
      _User_id = jsondata['user_id']
      _dashboardName = jsondata['name']
      _order_index = jsondata['index']
      query = "INSERT INTO myboard.dashboard (id, user_id, name, order_index) VALUES (null, %s, %s, %s)"
      return(insertSQL(query, (_User_id, _dashboardName, _order_index)))
    except Exception as e:
      return({'error':str(e)})
  def put(self):
    try:
      jsondata = request.get_json(force=True)
      _apiId = jsondata['id']
      _apiUser_id = jsondata['user_id']
      _apidashboardName = jsondata['name']
      _apiorder_index = jsondata['index']
      query = "UPDATE myboard.dashboard SET _apidashboardName = %s,_apiorder_index = %s WHERE user_id = %s and id = %s"
      return(executeSQL(query, (_apidashboardName,_apiorder_index,_apiUser_id,_apiId )))
    except Exception as e:
      return({'error':str(e)})
  def delete(self): #del
    jsondata = request.get_json(force=True)
    _apiId = jsondata['id']
    _apiUser_id = jsondata['user_id']
    query = "DELETE FROM myboard.dashboard WHERE user_id = %s and id = %s"
    return(executeSQL(query, (_apiUser_id, _apiId)))

api.add_resource(myboardAPI, '/apis')
api.add_resource(inspectorAPI, '/inspects/<user>/<api>')
api.add_resource(widgetAPI, '/widgets')
api.add_resource(dashboardAPI, '/dashboards')

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