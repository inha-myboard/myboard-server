#2017.10.05
#merge main.py, googleLogin.py

import flask
from flask import Flask, render_template,jsonify, request
from flaskext.mysql import MySQL
from flask_cors import CORS

#google oauth2
import json
import uuid
import httplib2
from googleapiclient import discovery
from oauth2client import client
# import API

#
import requests
from selenium import webdriver
import selenium.webdriver.support.ui as ui
import time, re
from flask_restful import Resource, Api
from flask_restful import reqparse

app = flask.Flask(__name__, static_folder='assets')
mysql = MySQL()
api = Api(app)
CORS(app)

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
      scope='email',
      # scope = 'https://www.googleapis.com/auth/userinfo.profile',
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
    print(googleInfo)
    print(type(googleInfo))
    print(googleInfo['access_token'])
    print(googleInfo['id_token']['email'])
    
    reqURL = 'https://www.googleapis.com/plus/v1/people/me'
    headers = {'Authorization': 'Bearer '+googleInfo['access_token']}
    clientInfo = json.loads(requests.get(reqURL, headers = headers).text)
    print(clientInfo)
    print(clientInfo['displayName'])
    print(clientInfo['image']['url'])
    try:
      query = "INSERT INTO myboard.user (id,email,nickname,access_token,img) VALUES (null, %s,%s,%s,%s) ON DUPLICATE KEY UPDATE access_token=%s and nickname=%s and img=%s"
      executeSQL(query, (googleInfo['id_token']['email'], clientInfo['displayName'], googleInfo['access_token'],clientInfo['image']['url'], googleInfo['access_token'],clientInfo['displayName'],clientInfo['image']['url']))
      # cursor.execute(query, (googleInfo['id_token']['email'], clientInfo['displayName'], googleInfo['access_token'],clientInfo['image']['url'], googleInfo['access_token'],clientInfo['displayName'],clientInfo['image']['url']))
      return(flask.redirect(flask.url_for('index')))
    except Exception as e:
      return({'error':str(e)})

@app.route('/dashboard')
def dashboard():
  return(render_template('dashboard.html'))

# @app.route('/<name>')
# def test(name = None):
#   return(render_template(name+'.html'))

#################UTIL#########################
def inspector(inputjson):
  data = json.loads(inputjson.replace('\'','"'))#json or str to dict
  driver.get(data["url"])
  ui.WebDriverWait(driver, 10).until(lambda browser: driver.find_element_by_tag_name('body'))

  rst = list()
  bodyPath = data['body_selector']
  bodys = driver.find_elements_by_css_selector(bodyPath)
  
  for body in bodys:
    obj = dict()
    for j in range(len(data["segments"])):
      temp = dict()
      if data["segments"][j]['selector'].split(' ')[-1][0:3] == 'img':
        temp['type'] = 'img'
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
        obj[data["segments"][j]['name']] = temp
      elif data["segments"][j]['selector'].split(' ')[-1][0] == 'a':
        temp['type'] = 'text'
        temp['href'] = body.find_element_by_css_selector(data["segments"][j]['selector']).get_attribute('href')
        temp['text'] = body.find_element_by_css_selector(data["segments"][j]['selector']).get_attribute('innerText')
        obj[data["segments"][j]['name']] = temp
      else:
        temp['type'] = 'text'
        temp['text'] = body.find_element_by_css_selector(data["segments"][j]['selector']).get_attribute('innerText')
        try: #seg에서 맨 마지막 parent가 a라면
          if data["segments"][j]['selector'].split(' ')[-3][0] == 'a':
            href = body.find_element_by_css_selector(data["segments"][j]['selector'][0:(data["segments"][j]['selector'].rfind('>')-1)]).get_attribute('href')
            temp['href'] = href
        except: # seg에서 parent tag가 없다면
          if data['body_selector'].split(' ')[-1][0] == 'a':
            href = body.get_attribute('href')
            temp['href'] = href
      obj[data["segments"][j]['name']] = temp
      # print(temp)
    rst.append(obj)
  return(rst)

def selectSQL(query): #return
  conn = mysql.connect()
  cursor = conn.cursor()
  try:
    cursor.execute(query)
    columns = cursor.description 
    result = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
    return(result)
  except Exception as e:
    return({'error':str(e)})
  finally:
    cursor.close()
    conn.close()


def executeSQL(query, parameter):
  conn = mysql.connect()
  cursor = conn.cursor()
  try:
    cursor.execute(query, parameter)
    conn.commit()
    return({'StatusCode': '200', 'query': query%parameter})
  except Exception as e:
    return({'error':str(e)})
  finally:
    cursor.close()
    conn.close()

###################### MYBOARD API ######################
class myboardAPI(Resource):
  def put(self, apiId):
    try:
      jsondata = request.get_json(force=True)
      _apiId = apiId
      _apiChange_name = jsondata['change_name']
      _apiCaption = jsondata['caption']
      _apiDescription = jsondata['description']
      _apiType = jsondata['type']
      _apiUrl = jsondata['url']
      _apiApi_json = jsondata['api_json']
      _apiUser_id = jsondata['user_id']
      # _apiName = jsondata['name']
      query = "UPDATE myboard.api SET name = %s, caption = %s, description = %s, type = %s, url = %s, api_json = %s, created_time = now()  WHERE id = %s"
      return(flask.jsonify(executeSQL(query, (_apiChange_name,_apiCaption,_apiDescription,_apiType,_apiUrl,_apiApi_json,_apiId ))))
    except Exception as e:
      return({'error':str(e)})
  def delete(self, apiId):
    _apiId = apiId
    query = "DELETE FROM myboard.api WHERE id = %s"
    return(flask.jsonify(executeSQL(query, (_apiId))))
class myboardAPIList(Resource):
  def get(self):
    query = "SELECT id,user_id,name,caption,description,type,url,api_json from myboard.api"
    return(flask.jsonify(selectSQL(query)))
  def post(self):
    try:
      jsondata = request.get_json(force=True)
      _apiUser_id = jsondata['user_id']
      _apiName = jsondata['name']
      _apiCaption = jsondata['caption']
      _apiDescription = jsondata['description']
      _apiType = jsondata['type']
      _apiApi_json = jsondata['api_json']
      _apiUrl = jsondata['url']
      query = "INSERT INTO myboard.api (id, user_id, name, caption, description, type, url, api_json, created_time) VALUES (null, %s, %s, %s, %s, %s, %s, %s, now())"
      # return(flask.jsonify(executeSQL(query, (_apiUser_id, _apiName, _apiCaption, _apiDescription, _apiType, _apiUrl, _apiApi_json))))
      executeSQL(query, (_apiUser_id, _apiName, _apiCaption, _apiDescription, _apiType, _apiUrl, _apiApi_json))
      
      # insert data
      select = "SELECT id, url, api_json FROM myboard.api;"
      temp = selectSQL(select)
      insert = "INSERT INTO myboard.api_data (api_id, data) VALUES (%s, %s) ON DUPLICATE KEY UPDATE data=%s"
      for i in range(len(temp)):
        sql_data = json.dumps(inspector(str(temp[i]['api_json'])))
        sql_id = temp[i]['id']
        executeSQL(insert, (sql_id, sql_data, sql_data))
  
    except Exception as e:
      return({'error':str(e)})

###################### INSPECTOR API ######################
class inspectorAPI(Resource):
    # def get(self):
    #   query = "SELECT api_id, data FROM myboard.api_data;"
    #   getjson = selectSQL(query)
    #   return(flask.jsonify(getjson))
    def post(self):
      try:
        jsondata = request.get_json(force=True)
        _apiApi_json = jsondata['api_json']
        # _apiUrl = jsondata['url']
        preview = inspector(json.dumps(_apiApi_json))
        return(preview)
      except Exception as e:
        return({'error':str(e)})


###################### WIDGET API ######################
class widgetAPI(Resource):
  def put(self, widgetID): #update
    try:
        jsondata = request.get_json(force=True)
        # _apiId = jsondata['id']
        _apiId = widgetID
        _apiApi_id = jsondata['api_id']
        _apiUser_id = jsondata['user_id']
        _apiCaption = jsondata['caption']
        _apiDescription = jsondata['description']
        _apiMapping_json = jsondata['mapping_json']
        query = "UPDATE myboard.widget SET api_id = %s,user_id = %s,caption = %s,description = %s,mapping_json = %s, created_time = now()  WHERE id = %s"
        return(flask.jsonify(executeSQL(query, (_apiApi_id,_apiUser_id,_apiCaption,_apiDescription,_apiMapping_json,_apiId ))))
    except Exception as e:
        return({'error':str(e)})
  def delete(self, widgetID):
      _apiId = widgetID
      query = "DELETE FROM myboard.widget WHERE id = %s"
      return(flask.jsonify(executeSQL(query, (_apiId))))

class widgetAPIList(Resource):
  def get(self): #list, search  #뒤에 변수값 있으면 search, null이면 list
    query = "SELECT w.id,w.caption, user.nickname,w.description,api.url, w.created_time from myboard.widget w inner join api on w.api_id = api.id inner join user on w.user_id = user.id"
    return(flask.jsonify(selectSQL(query)))
  def post(self): #insert 사용자가 위젯을 등록. 현재 DB구조로는 컴포넌트 먼저 등록하고 위젯 등록.
    try:
      jsondata = request.get_json(force=True)
      _apiApi_id = jsondata['api_id']
      _apiUser_id = jsondata['user_id']
      _apiCaption = jsondata['caption']
      _apiDescription = jsondata['description']
      _apiMapping_json = jsondata['mapping_json']
      query = "INSERT INTO myboard.widget (id,api_id,user_id,caption,description,mapping_json,created_time) VALUES (null, %s, %s, %s, %s, %s, now())"
      return(flask.jsonify(executeSQL(query, ( _apiApi_id, _apiUser_id, _apiCaption, _apiDescription, _apiMapping_json))))
    except Exception as e:
      return({'error':str(e)})

###################### DASHBOARD API ######################
class dashboardAPIList(Resource):
    def get(self, userId): #dashboard list
        _apiUser_id = userId
        query = "SELECT id, name, order_index FROM myboard.dashboard WHERE user_id=%s" % _apiUser_id
        return(selectSQL(query))
    def post(self, userId): #insert
        try:
          jsondata = request.get_json(force=True)
          _User_id = userId
          _dashboardName = jsondata['name']
          _order_index = jsondata['index']
          query = "INSERT INTO myboard.dashboard (id, user_id, name, order_index) VALUES (null, %s, %s, %s)"
          return(flask.jsonify(executeSQL(query, (_User_id, _dashboardName, _order_index))))
        except Exception as e:
            return({'error':str(e)})

class dashboardAPI(Resource):
    # def get(self, dashId):
    #     _dashId = dashId
    #     query = "SELECT id, name, order_index FROM myboard.dashboard WHERE id=%s" % dashId
    #     return(selectSQL(query))
    # def post(self, dashId): #dashboard insert
    #     try:
    #         jsondata = request.get_json(force=True)
    #         _dashId = dashId
    #         _User_id = jsondata['user_id']
    #         _dashboardName = jsondata['name']
    #         _order_index = jsondata['index']
    #         query = "INSERT INTO myboard.dashboard (id, user_id, name, order_index) VALUES (null, %s, %s, %s)"
    #         return(executeSQL(query, (_User_id, _dashboardName, _order_index)))
    #     except Exception as e:
    #         return({'error':str(e)})
    def put(self, dashId): # dashboard update
        try:
            jsondata = request.get_json(force=True)
            _dashId = dashId
            _apidashName = jsondata['name']
            _apiorder_index = jsondata['index']
            query = "UPDATE myboard.dashboard SET name = %s,order_index = %s WHERE id = %s"
            return(flask.jsonify(executeSQL(query, (_apidashName, _apiorder_index, _dashId ))))
        except Exception as e:
            return({'error':str(e)})
    def delete(self, dashId): #del
        _dashId = dashId
        query = "DELETE FROM myboard.dashboard WHERE id = %s"
        return(flask.jsonify(executeSQL(query, (_dashId))))

class dashboardANDWidget(Resource):
    def get(self, dashId):
        _dashId = dashId
        
        # SELECT w.*, wp.props_json,api_data.data FROM widget_pos wp inner join widget w on wp.widget_id = w.id inner join api_data on w.api_id = api_data.api_ID; #data까지 한번에 긁어오는거
        rst = dict()
        query = 'SELECT w.*, wp.props_json FROM widget_pos wp inner join widget w on wp.widget_id = w.id where dashboard_id = %s' % _dashId
        rst['widget'] = selectSQL(query)
        print(rst['widget'])
        query = 'SELECT api_data.api_id, data FROM myboard.widget_pos inner join myboard.widget on myboard.widget_pos.widget_id = myboard.widget.id inner join api_data on widget.api_id = api_data.api_ID where dashboard_id = %s' % _dashId
        rst['data'] = selectSQL(query)
        print(rst['data'])
        return(flask.jsonify(rst))
    def post(self, dashId):
        conn = mysql.connect()
        conn.begin()
        cursor = conn.cursor()
        try:
            jsondata = request.get_json(force=True)
            cursor.execute("DELETE FROM myboard.widget_pos WHERE dashboard_id = %s;", (dashId))

            for obj in jsondata:
                widget_id = obj['widget_id']
                props_json = obj['props_json']
                cursor.execute("INSERT INTO myboard.widget_pos (widget_id, dashboard_id, props_json) value (%s, , %s, %s);", (widget_id, dashId, json.dumps(props_json)))
            conn.commit()
        except Exception as e:
            conn.rollback()
            return({'error':str(e)})
        finally:
            cursor.close()
            conn.close()


api.add_resource(myboardAPI, '/apis/<apiId>')
api.add_resource(myboardAPIList, '/apis')

api.add_resource(inspectorAPI, '/inspects')
# api.add_resource(inspectorAPI, '/inspects/<apiId>')
# api.add_resource(inspectorAPI, '/dashboards/<id>/inspects')

api.add_resource(widgetAPI, '/widgets/<widgetID>')
api.add_resource(widgetAPIList, '/widgets')

api.add_resource(dashboardAPI, '/dashboards/<dashId>') # //dash id 입력하면 그 대쉬보드를 // get,post,del, put
api.add_resource(dashboardAPIList, '/users/<userId>/dashboards') # user의 dash list가져오기 //get
api.add_resource(dashboardANDWidget, '/dashboards/<dashId>/widgets/') # 대시보드 위젯리스트 조회, 저장 //get, post
# SELECT w.*, wp.props_json FROM widget_pos wp inner join widget w on wp.widget_id = w.id where dashboard_id = ?

def prepare():
  #MySQL configurations
  app.config.from_object(__name__)
  try:
    app.config.from_envvar('MYBOARD_SETTINGS', silent=False)
  except:
    app.config.from_pyfile('local.cfg')
  mysql.init_app(app)
  app.secret_key = str(uuid.uuid4())
  app.debug = False

if __name__ == '__main__':
  prepare()
  driver = webdriver.PhantomJS('./PhantomJS')
  app.run(host='0.0.0.0')
