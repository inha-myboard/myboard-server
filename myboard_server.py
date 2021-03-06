# -*- coding: utf-8 -*-
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

passAuth = False
app = flask.Flask(__name__, static_folder='assets')
mysql = MySQL()
api = Api(app)
CORS(app)

@app.before_request
def before_request():
  granted_request = ['oauth2callback' , 'login', 'logout']
  if 'credentials' not in flask.session and request.path.strip("/") not in granted_request and passAuth is False:
  # if 'credentials' not in flask.session and request.endpoint != 'oauth2callback' and passAuth is False:
    return ('Access denied', 403)

@app.route('/')
@app.route('/index')
def index():
  return("dummy")

@app.route('/login')
def login():
  # if 'credentials' not in flask.session:
  #   return(flask.redirect(flask.url_for('oauth2callback')))
  if 'credentials' not in flask.session:
    return(flask.redirect(flask.url_for('oauth2callback')))
  credentials = client.OAuth2Credentials.from_json(flask.session['credentials'])
  if credentials.access_token_expired:
    return(flask.redirect(flask.url_for('oauth2callback')))
  else:
    http_auth = credentials.authorize(httplib2.Http())
    return(flask.redirect("/"))

@app.route('/print')
def printSession():
  return(str(flask.session['credentials']))

@app.route('/logout')
def sessionOut():
  flask.session.clear()
  return(flask.redirect("/"))


@app.route('/oauth2callback/')
def oauth2callback():
  flow = client.flow_from_clientsecrets(
      filename='./client_secrets.json',
      scope='email',
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
    # print(googleInfo)
    # print(type(googleInfo))
    # print(googleInfo['access_token'])
    # print(googleInfo['id_token']['email'])
    
    reqURL = 'https://www.googleapis.com/plus/v1/people/me'
    headers = {'Authorization': 'Bearer '+googleInfo['access_token']}
    clientInfo = json.loads(requests.get(reqURL, headers = headers).text)
    # print(clientInfo)
    # print(clientInfo['displayName'])
    # print(clientInfo['image']['url'])
    try:
      query = "INSERT INTO myboard.user (id,email,nickname,access_token,img) VALUES (null, %s,%s,%s,%s) ON DUPLICATE KEY UPDATE access_token=%s, nickname=%s, img=%s"
      executeSQL(query, (googleInfo['id_token']['email'], clientInfo['displayName'], googleInfo['access_token'],clientInfo['image']['url'], googleInfo['access_token'],clientInfo['displayName'],clientInfo['image']['url']))
      
      query = "SELECT id FROM myboard.user WHERE email = %s"
      flask.session['userId'] = selectSQL(query, (googleInfo['id_token']['email']))
      # return(flask.redirect(flask.url_for('index')))
      return(flask.redirect("/"))
    except Exception as e:
      return({'error':str(e)}, 500)

# @app.route('/<name>')
# def check(name = None):
#   if 'credentials' not in flask.session:
#     return(flask.redirect(flask.url_for('oauth2callback')))
#   else:
#     return(flask.redirect(flask.url_for(name)))

###################### INSPECTOR ######################
def inspect(url, inputjson):
  data = json.loads(inputjson.replace('\'','"'))#json or str to dict
  driver.get(url)
  ui.WebDriverWait(driver, 10).until(lambda browser: driver.find_element_by_tag_name('body'))
  # driver.refresh()
  # ui.WebDriverWait(driver, 10).until(lambda browser: driver.find_element_by_tag_name('body'))
  rst = list()
  bodyPath = data['body_selector']
  bodys = driver.find_elements_by_css_selector(bodyPath)
  
  for body in bodys:
    obj = dict()
    for j in range(len(data["segments"])):
      temp = dict()
      if data["segments"][j]['selector'].split(' ')[-1][0:3] == 'img':
        try:
          temp['src'] = body.find_element_by_css_selector(data["segments"][j]['selector']).get_attribute('src')
          temp['type'] = 'img'
        except: #segment가 없으면. key제거
          pass
          #temp.pop('src')
        try: #seg에서 맨 마지막 parent가 a라면
          if data["segments"][j]['selector'].split(' ')[-3][0] == 'a':
            href = body.find_element_by_css_selector(data["segments"][j]['selector'][0:(data["segments"][j]['selector'].rfind('>')-1)]).href
            temp['href'] = href
        except: # seg에서 parent tag가 없다면
          pass
        # obj[data["segments"][j]['name']] = temp
      elif data["segments"][j]['selector'].split(' ')[-1][0] == 'a':
        try:
          temp['href'] = body.find_element_by_css_selector(data["segments"][j]['selector']).get_attribute('href')
          temp['text'] = body.find_element_by_css_selector(data["segments"][j]['selector']).get_attribute('innerText')
          temp['type'] = 'text'
        except:
          pass
        # obj[data["segments"][j]['name']] = temp
      else:
        try:
          temp['text'] = body.find_element_by_css_selector(data["segments"][j]['selector']).get_attribute('innerText')
          temp['type'] = 'text'
        except:
          pass
        try: #seg에서 맨 마지막 parent가 a라면
          if data["segments"][j]['selector'].split(' ')[-3][0] == 'a':
            href = body.find_element_by_css_selector(data["segments"][j]['selector'][0:(data["segments"][j]['selector'].rfind('>')-1)]).get_attribute('href')
            temp['href'] = href
        except: # seg에서 parent tag가 없다면
          if data['body_selector'].split(' ')[-1][0] == 'a':
            href = body.get_attribute('href')
            temp['href'] = href
      if(len(temp.keys()) == 0):
        continue
      obj[data["segments"][j]['name']] = temp
      # print(temp)
    if(len(obj.keys()) == 0):
      continue
    rst.append(obj)
  return(rst)


def selectSQL(query, parameter=()):
  conn = mysql.connect()
  cursor = conn.cursor()
  try:
    cursor.execute(query, parameter)
    columns = cursor.description 
    result = [{columns[index][0]:column for index, column in enumerate(value)} for value in cursor.fetchall()]
    return(result)
  except Exception as e:
    return({'error':str(e)}, 500)
  finally:
    cursor.close()
    conn.close()


def insertSQL(query, parameter=()):
  conn = mysql.connect()
  cursor = conn.cursor()
  try:
    cursor.execute(query, parameter)
    cursor.execute("SELECT LAST_INSERT_ID() AS id;")
    result = cursor.fetchall()
    conn.commit()
    return({'inserted_id': result[0][0], 'query': query%parameter}, 200)
  except Exception as e:
    return({'error':str(e)}, 500)
  finally:
    cursor.close()
    conn.close()


def executeSQL(query, parameter=()):
  conn = mysql.connect()
  cursor = conn.cursor()
  try:
    cursor.execute(query, parameter)
    conn.commit()
    return(query % parameter, 200)
  except Exception as e:
    return({'error':str(e)}, 500)
  finally:
    cursor.close()
    conn.close()


###################### MYBOARD API ######################
class myboardApi(Resource):
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
      _apiUser_id =  0 if passAuth is True else flask.session['userId'][0]['id']
      # _apiName = jsondata['name']
      query = "UPDATE myboard.api SET name = %s, caption = %s, description = %s, type = %s, url = %s, api_json = %s, created_time = now()  WHERE id = %s"
      return(flask.jsonify(executeSQL(query, (_apiChange_name,_apiCaption,_apiDescription,_apiType,_apiUrl,_apiApi_json,_apiId ))))
    except Exception as e:
      return({'error':str(e)}, 500)
  def delete(self, apiId):
    _apiId = apiId
    query = "DELETE FROM myboard.api WHERE id = %s"
    return(flask.jsonify(executeSQL(query, (_apiId))))
class myboardApiList(Resource):
  def get(self):
    query = "SELECT id,user_id,name,caption,description,type,url,api_json from myboard.api"
    return(flask.jsonify(selectSQL(query, ())))
  def post(self):
    try:
      jsondata = request.get_json(force=True)
      _apiUser_id = 0 if passAuth is True else flask.session['userId'][0]['id']
      _apiName = jsondata['name']
      _apiCaption = jsondata['caption']
      _apiDescription = jsondata['description']
      _apiType = jsondata['type']
      _apiApi_json = jsondata['api_json']
      _apiUrl = jsondata['url']
      query = "INSERT INTO myboard.api (id, user_id, name, caption, description, type, url, api_json, created_time) VALUES (null, %s, %s, %s, %s, %s, %s, %s, now())"
      # return(flask.jsonify(executeSQL(query, (_apiUser_id, _apiName, _apiCaption, _apiDescription, _apiType, _apiUrl, _apiApi_json))))
      result = insertSQL(query, (_apiUser_id, _apiName, _apiCaption, _apiDescription, _apiType, _apiUrl, _apiApi_json))
      print(result)
      last_insert_id = result[0]['inserted_id']
      
      # insert data
      select = "SELECT api.id, api_json FROM api LEFT JOIN api_data ON api.id = api_data.api_id WHERE api_data.api_id is NULL;"
      temp = selectSQL(select, ())
      insert = "INSERT INTO myboard.api_data (api_id, data, updated_time) VALUES (%s, %s, now()) ON DUPLICATE KEY UPDATE data=%s, updated_time = now()"
      for i in range(len(temp)):
        api_json = json.dumps(inspect(_apiUrl, str(temp[i]['api_json'])))
        api_id = temp[i]['id']
        executeSQL(insert, (api_id, api_json, api_json))
      return({'id': last_insert_id})
    except Exception as e:
      return({'error':str(e)}, 500)

###################### INSPECTOR API ######################
class inspectApi(Resource):
    # def get(self):
    #   query = "SELECT api_id, data FROM myboard.api_data;"
    #   getjson = selectSQL(query)
    #   return(flask.jsonify(getjson))
    def post(self):
      try:
        jsondata = request.get_json(force=True)
        url = jsondata['url']
        api_json = jsondata['api_json']
        # _apiUrl = jsondata['url']
        preview = inspect(url, api_json)
        return(preview)
      except Exception as e:
        return({'error':str(e)}, 500)


###################### WIDGET API ######################
class widget(Resource):
  def get(self, widgetId): #update
    try:
        query = "SELECT * FROM widget w WHERE w.id = %s"
        rst = selectSQL(query, (widgetId))
        if len(rst) > 0:
          return(flask.jsonify(rst[0]))
        return ('', 204)
    except Exception as e:
        return({'error':str(e)}, 500)
  def put(self, widgetId): #update
    try:
        jsondata = request.get_json(force=True)
        # _apiId = jsondata['id']
        _apiId = widgetId
        _apiApi_id = jsondata['api_id']
        _apiUser_id = 0 if passAuth is True else flask.session['userId'][0]['id']
        _apiCaption = jsondata['caption']
        _apiDescription = jsondata['description']
        _apiMapping_json = jsondata['mapping_json']
        query = "UPDATE myboard.widget SET api_id = %s,user_id = %s,caption = %s,description = %s,mapping_json = %s, created_time = now()  WHERE id = %s"
        return(flask.jsonify(executeSQL(query, (_apiApi_id,_apiUser_id,_apiCaption,_apiDescription,_apiMapping_json,_apiId ))))
    except Exception as e:
        return({'error':str(e)}, 500)
  def delete(self, widgetId):
      _apiId = widgetId
      query = "DELETE FROM myboard.widget WHERE id = %s"
      return(flask.jsonify(executeSQL(query, (_apiId))))


class widgetData(Resource):
  def get(self, widgetId): #update
    try:
        query = "SELECT w.id, ad.data, ad.updated_time FROM api_data ad INNER JOIN widget w on w.api_id = ad.api_id WHERE w.id = %s"
        rst = selectSQL(query, (widgetId))
        if len(rst) > 0:
          query = "UPDATE api_data ad INNER JOIN widget w on w.api_id = ad.api_id SET last_access_time = now() WHERE w.id = %s"
          executeSQL(query, (widgetId))
          return(flask.jsonify(rst[0]))
        return ('', 204)
    except Exception as e:
        return({'error':str(e)}, 500)


class widgetList(Resource):
  def get(self): #list, search  #뒤에 변수값 있으면 search, null이면 list
    user_id = request.args.get('user_id', default = None)
    query = "SELECT w.id,w.caption, user.nickname,w.description,api.url, w.created_time from myboard.widget w inner join api on w.api_id = api.id inner join user on w.user_id = user.id"
    if user_id  is  not  None:
        query = query + " WHERE user_id = %s" % user_id
    return(flask.jsonify(selectSQL(query, ())))
  def post(self): # 사용자가 위젯을 등록. 현재 구조로 API 먼저 등록하고 위젯 등록.
    try:
        jsondata = request.get_json(force=True)
        _apiApi_id = jsondata['api_id']
        _apiType = jsondata['type']
        _apiCaption = jsondata['caption']
        _apiDescription = jsondata['description']
        _apiMapping_json = jsondata['mapping_json']
        _apiUser_id = 0 if passAuth is True else flask.session['userId'][0]['id']
        query = "INSERT INTO myboard.widget (id,api_id,type, user_id,caption,description,mapping_json,created_time) VALUES (null, %s, %s, %s, %s, %s, %s, now())"
        return(flask.jsonify(executeSQL(query, ( _apiApi_id, _apiType, _apiUser_id, _apiCaption, _apiDescription, _apiMapping_json))))
    except Exception as e:
        return({'error':str(e)}, 500)

###################### DASHBOARD API ######################
class userDashboardList(Resource):
    def get(self, userId): #dashboard list
        if passAuth is False and userId is not flask.session['userId'][0]['id']:
            return('access denied', 403)
        query = "SELECT id, name, icon, order_index FROM myboard.dashboard WHERE user_id=%s"
        return(selectSQL(query, (userId)))
    def post(self, userId): #insert
        if passAuth is False and  userId is not flask.session['userId'][0]['id']:
            return('access denied', 403)
        try:
            jsondata = request.get_json(force=True)
            query = "INSERT INTO myboard.dashboard (user_id, name, icon, order_index) VALUES (%s, %s, %s, %s)"
            for dashboard in jsondata:
                _name = dashboard['name']
                _icon = dashboard['icon']
                _user_id = 0 if passAuth is True else flask.session['userId'][0]['id']
                _order_index = dashboard['order_index']
                executeSQL(query, (_user_id, _name, _icon, _order_index))
            return('', 204)
        except Exception as e:
            return({'error':str(e)}, 500)
    def put(self, userId): # dashboard update
        if passAuth is False and  userId is not flask.session['userId'][0]['id']:
            return('access denied', 403)
        try:
            jsondata = request.get_json(force=True)
            query = "UPDATE myboard.dashboard SET name = %s, icon = %s, order_index = %s WHERE id = %s"
            for dashboard in jsondata:
                _id = dashboard['id']
                _name = dashboard['name']
                _icon = dashboard['icon']
                _order_index = dashboard['order_index']
                executeSQL(query, (_name, _icon, _order_index, _id))
            return('', 204)
        except Exception as e:
            return({'error': str(e)}, 500)
    def delete(self, userId): # dashboard update
        if passAuth is False and  userId is not flask.session['userId'][0]['id']:
            return('access denied', 403)
        try:
            jsondata = request.get_json(force=True)
            query = "DELETE FROM myboard.dashboard WHERE id = %s"
            for dashboard in jsondata:
                _id = dashboard['id']
                executeSQL(query, (_id))
            return('', 204)
        except Exception as e:
            return({'error': str(e)}, 500)


class dashboard(Resource):
    # def get(self, dashboardId):
    #     _dashboardId = dashboardId
    #     query = "SELECT id, name, order_index FROM myboard.dashboard WHERE id=%s" % dashboardId
    #     return(selectSQL(query))
    # def post(self, dashboardId): #dashboard insert
    #     try:
    #         jsondata = request.get_json(force=True)
    #         _dashboardId = dashboardId
    #         _User_id = jsondata['user_id']
    #         _dashboardName = jsondata['name']
    #         _order_index = jsondata['index']
    #         query = "INSERT INTO myboard.dashboard (id, user_id, name, order_index) VALUES (null, %s, %s, %s)"
    #         return(executeSQL(query, (_User_id, _dashboardName, _order_index)))
    #     except Exception as e:
    #         return({'error':str(e)})

    def put(self, userId):
        try:
            jsondata = request.get_json(force=True)
            _id = jsondata['id']
            _name = jsondata['name']
            _icon = jsondata['icon']
            _order_index = jsondata['index']
            query = "UPDATE myboard.dashboard SET name = %s, order_index = %s WHERE id = %s"
            return(flask.jsonify(executeSQL(query, (_name, _icon, _order_index, _id))))
        except Exception as e:
            return({'error':str(e)}, 500)


    def delete(self, dashboardId): #del
        _dashboardId = dashboardId
        query = "DELETE FROM myboard.dashboard WHERE id = %s"
        return(flask.jsonify(executeSQL(query, (_dashboardId))))


class dashboardWidgetList(Resource):
    def get(self, dashboardId):
        _dashboardId = dashboardId
        
        query = 'SELECT w.*, api.url, wp.props_json FROM widget_pos wp INNER JOIN widget w ON wp.widget_id = w.id INNER JOIN api ON w.api_id = api.id WHERE dashboard_id = %s'
        rst = selectSQL(query, (_dashboardId))
        return(flask.jsonify(rst))
    def post(self, dashboardId):
        conn = mysql.connect()
        conn.begin()
        cursor = conn.cursor()
        try:
            jsondata = request.get_json(force=True)
            cursor.execute("DELETE FROM myboard.widget_pos WHERE dashboard_id = %s;", (dashboardId))

            for obj in jsondata:
                widget_id = obj['id']
                props_json = obj['props_json']
                cursor.execute("INSERT INTO myboard.widget_pos (widget_id, dashboard_id, props_json) VALUES (%s, %s, %s);", (widget_id, dashboardId, props_json))
            conn.commit()
        except Exception as e:
            conn.rollback()
            return({'error':str(e)}, 500)
        finally:
            cursor.close()
            conn.close()


class dashboardWidgetData(Resource):
    def get(self, dashboardId):
        _dashboardId = dashboardId
        query = 'SELECT widget.id, api_data.data FROM myboard.widget_pos inner join myboard.widget on myboard.widget_pos.widget_id = myboard.widget.id inner join api_data on widget.api_id = api_data.api_id where dashboard_id = %s'
        rst = selectSQL(query, (_dashboardId))
        if len(rst) > 0:
            query = "UPDATE api_data ad INNER JOIN widget w ON w.api_id = ad.api_id INNER JOIN widget_pos wp ON wp.widget_id = w.id INNER JOIN api a ON a.id = ad.api_id SET a.last_access_time = NOW() WHERE wp.dashboard_id = %s"
            executeSQL(query, (_dashboardId))
        return(flask.jsonify(rst))


###################### PROFILE API ######################
class profile(Resource):
    def get(self):
      try:
        _user_id = 0 if passAuth is True else flask.session['userId'][0]['id']
        query = "SELECT id, email, nickname, img FROM user WHERE id = %s"
        rst = selectSQL(query, (_user_id))
        return(flask.jsonify(rst[0]))
      except Exception as e:
        return(str(e), '500')


api.add_resource(myboardApi, '/apis/<apiId>')
api.add_resource(myboardApiList, '/apis')

api.add_resource(inspectApi, '/inspects') # apijson로 inspect 실행

api.add_resource(widget, '/widgets/<widgetId>') # widget 템플릿 조회
api.add_resource(widgetData, '/widgets/<widgetId>/data') # widget 데이터 조회
api.add_resource(widgetList, '/widgets')

api.add_resource(profile, '/me')

api.add_resource(dashboard, '/dashboards/<dashboardId>') # //dash id 입력하면 그 대쉬보드를 // get,post,del, put
api.add_resource(userDashboardList, '/users/<userId>/dashboards') # user의 dash list가져오기 //get
api.add_resource(dashboardWidgetList, '/dashboards/<dashboardId>/widgets') # 대시보드 위젯리스트 조회, 저장 //get, post
api.add_resource(dashboardWidgetData, '/dashboards/<dashboardId>/widgets/data') # 대시보드 위젯데이터 조회 //get

def prepare():
  #MySQL configurations
  app.config.from_object(__name__)
  try:
    app.config.from_envvar('MYBOARD_SETTINGS', silent=False)
  except:
    app.config.from_pyfile('local.cfg')
  global driver
  driver = webdriver.PhantomJS('./phantomjs')
  mysql.init_app(app)
  app.secret_key = str(uuid.uuid4())
  app.debug = False

if __name__ == '__main__':
  prepare()
  app.run(host='0.0.0.0')
