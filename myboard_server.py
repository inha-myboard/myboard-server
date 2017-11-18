#2017.10.05
#merge main.py, googleLogin.py

#flask
import flask
from flask import Flask, render_template,jsonify, request
from flaskext.mysql import MySQL

#google oauth2
import json
import uuid
import httplib2
from apiclient import discovery
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
    # print(googleInfo['access_token'])
    # print(googleInfo['id_token']['email'])
    
    reqURL = 'https://www.googleapis.com/plus/v1/people/me'
    headers = {'Authorization': 'Bearer '+googleInfo['access_token']}
    clientInfo = json.loads(requests.get(reqURL, headers = headers).text)
    print(clientInfo)
    print(clientInfo['displayName'])
    print(clientInfo['image']['url'])
    try:
      query = "INSERT INTO myboard.user (id,email,nickname,access_token,img) VALUES (null, %s,%s,%s,%s) ON DUPLICATE KEY UPDATE access_token=%s and nickname=%s and img=%s"
      cursor.execute(query, (googleInfo['id_token']['email'], clientInfo['displayName'], googleInfo['access_token'],clientInfo['image']['url'], googleInfo['access_token'],clientInfo['displayName'],clientInfo['image']['url']))
      conn.commit()
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
# def inspector(inputjson):
#     driver = webdriver.PhantomJS('./PhantomJS')
#     data = json.loads(inputjson.replace('\'','"'))#json or str to dict

#     driver.get(data["url"])
#     ui.WebDriverWait(driver, 10).until(lambda browser: driver.find_element_by_tag_name('body'))
#     driver.refresh()
#     ui.WebDriverWait(driver, 10).until(lambda browser: driver.find_element_by_tag_name('body'))
#     rst = list()

#     bodyPath = data['body_selector']
#     while 1:
#         obj = dict()
#         try:
#             body = driver.find_element_by_css_selector(bodyPath)
#         except:
#             break
#         for j in range(len(data["segments"])):
#             temp = dict()
#             if data["segments"][j]['selector'].split(' ')[-1][0:3] == 'img':
#                 try:
#                     temp['src'] = body.find_element_by_css_selector(data["segments"][j]['selector']).get_attribute('src')
#                 except:
#                     pass
#                 try: #seg에서 맨 마지막 parent가 a라면
#                     if data["segments"][j]['selector'].split(' ')[-3][0] == 'a':
#                         href = body.find_element_by_css_selector(data["segments"][j]['selector'][0:(data["segments"][j]['selector'].rfind('>')-1)]).href
#                         temp['href'] = href
#                 except: # seg에서 parent tag가 없다면
#                     pass
#                     # if data['body_selector'][i].split(' ')[-1][0] == 'a':
#                     #   href = body.get_attribute('href')
#                 obj[data["segments"][j]['name']] = temp
#             elif data["segments"][j]['selector'].split(' ')[-1][0] == 'a':
#                 temp['href'] = body.find_element_by_css_selector(data["segments"][j]['selector']).get_attribute('href')
#                 temp['text'] = body.find_element_by_css_selector(data["segments"][j]['selector']).text
#                 obj[data["segments"][j]['name']] = temp
#             else:
#                 # text = body.find_element_by_css_selector(data["segments"][j]['selector']).text
#                 temp['text'] = body.find_element_by_css_selector(data["segments"][j]['selector']).text
#                 try: #seg에서 맨 마지막 parent가 a라면
#                     if data["segments"][j]['selector'].split(' ')[-3][0] == 'a':
#                         href = body.find_element_by_css_selector(data["segments"][j]['selector'][0:(data["segments"][j]['selector'].rfind('>')-1)]).get_attribute('href')
#                         temp['href'] = href
#                 except: # seg에서 parent tag가 없다면
#                     if data['body_selector'].split(' ')[-1][0] == 'a':
#                         href = body.get_attribute('href')
#                         temp['href'] = href
#                 obj[data["segments"][j]['name']] = temp
#         rst.append(obj)
#         bodyPath = bodyPath + ' + ' + body.tag_name
#     driver.close()
#     return(rst)

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
      return(executeSQL(query, (_apiChange_name,_apiCaption,_apiDescription,_apiType,_apiUrl,_apiApi_json,_apiId )))
    except Exception as e:
      return({'error':str(e)})
  def delete(self, apiId):
    _apiId = apiId
    query = "DELETE FROM myboard.api WHERE id = %s"
    return(executeSQL(query, (_apiId)))
class myboardAPIList(Resource):
  def get(self):
    query = "SELECT id,user_id,name,caption,description,type,url,api_json from myboard.api"
    return(selectSQL(query))
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
      return(executeSQL(query, (_apiUser_id, _apiName, _apiCaption, _apiDescription, _apiType, _apiUrl, _apiApi_json)))
    except Exception as e:
      return({'error':str(e)})

###################### INSPECTOR API ######################
class inspectorAPI(Resource):
    def get(self):
      query = "SELECT api_id, data FROM myboard.api_data;"
      getjson = selectSQL(query)
      return(getjson)

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
        return(executeSQL(query, (_apiApi_id,_apiUser_id,_apiCaption,_apiDescription,_apiMapping_json,_apiId )))
    except Exception as e:
        return({'error':str(e)})
  def delete(self, widgetID):
      _apiId = widgetID
      query = "DELETE FROM myboard.widget WHERE id = %s"
      return(executeSQL(query, (_apiId)))

class widgetAPIList(Resource):
  def get(self): #list, search  #뒤에 변수값 있으면 search, null이면 list
    query = "SELECT id,api_id,user_id,caption,description,mapping_json from myboard.widget"
    return(selectSQL(query))
  def post(self): #insert 사용자가 위젯을 등록. 현재 DB구조로는 컴포넌트 먼저 등록하고 위젯 등록.
    try:
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
          return(executeSQL(query, (_User_id, _dashboardName, _order_index)))
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
            return(executeSQL(query, (_apidashName, _apiorder_index, _dashId )))
        except Exception as e:
            return({'error':str(e)})
    def delete(self, dashId): #del
        _dashId = dashId
        query = "DELETE FROM myboard.dashboard WHERE id = %s"
        return(executeSQL(query, (_dashId)))

class dashboardANDWidget(Resource):
    def get(self, dashId):
        _dashId = dashId
        query = 'SELECT w.*, wp.props_json FROM widget_pos wp inner join widget w on wp.widget_id = w.id where dashboard_id = %s' % _dashId
        return(selectSQL(query))
    def post(self, dashId):
        try:
            jsondata = request.get_json(force=True)
            # _User_id = jsondata['user_id']
            # _dashboardName = jsondata['name']
            # _order_index = jsondata['index']
            # query = "INSERT INTO myboard.dashboard (id, user_id, name, order_index) VALUES (null, %s, %s, %s)"
            # return(executeSQL(query, (_User_id, _dashboardName, _order_index)))
        except Exception as e:
            return({'error':str(e)})

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

if __name__ == '__main__':
    #MySQL configurations
    app.config.from_object(__name__)
    app.config.from_envvar('MYBOARD_SETTINGS', silent=False)
    mysql.init_app(app)
    conn = mysql.connect()
    cursor = conn.cursor()

    app.secret_key = str(uuid.uuid4())
    app.debug = False
    app.run(host='0.0.0.0')