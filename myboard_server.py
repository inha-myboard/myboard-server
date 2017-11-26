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

app = flask.Flask(__name__, static_folder='assets')
mysql = MySQL()
api = Api(app)
CORS(app)


@app.route('/login')
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
    return(flask.redirect(flask.url_for('/')))

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
      useridval = selectSQL(query, (googleInfo['id_token']['email']))
       # flask.session['userId']
      
      # cursor.execute(query, (googleInfo['id_token']['email'], clientInfo['displayName'], googleInfo['access_token'],clientInfo['image']['url'], googleInfo['access_token'],clientInfo['displayName'],clientInfo['image']['url']))
      return(flask.redirect(flask.url_for('index')))
    except Exception as e:
      return({'error':str(e)})

# @app.route('/<name>')
# def check(name = None):
#   if 'credentials' not in flask.session:
#     return(flask.redirect(flask.url_for('oauth2callback')))
#   else:
#     return(flask.redirect(flask.url_for(name)))


def inspect(inputjson):
  data = json.loads(inputjson.replace('\'','"')) #json or str to dict
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

def selectSQL(query, parameter):
  conn = mysql.connect()
  cursor = conn.cursor()
  try:
    cursor.execute(query, parameter)
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
class myboardApiList(Resource):
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
      
      select = "SELECT LAST_INSERT_ID();"
      temp = selectSQL(select, ())
      last_insert_id = temp[0]

      # insert data
      select = "SELECT api.id, api_json FROM api LEFT JOIN api_data ON api.id = api_data.api_id WHERE api_data.api_id is NULL;"
      temp = selectSQL(select)
      insert = "INSERT INTO myboard.api_data (api_id, data) VALUES (%s, %s) ON DUPLICATE KEY UPDATE data=%s"
      for i in range(len(temp)):
        sql_data = json.dumps(inspector(str(temp[i]['api_json'])))
        sql_id = temp[i]['id']
        executeSQL(insert, (sql_id, sql_data, sql_data))
      return(last_insert_id)
    except Exception as e:
      return({'error':str(e)})

###################### INSPECTOR API ######################
class inspectApi(Resource):
    # def get(self):
    #   query = "SELECT api_id, data FROM myboard.api_data;"
    #   getjson = selectSQL(query)
    #   return(flask.jsonify(getjson))
    def post(self):
      try:
        jsondata = request.get_json(force=True)
        _apiApi_json = jsondata['api_json']
        # _apiUrl = jsondata['url']
        preview = inspect(json.dumps(_apiApi_json))
        return(preview)
      except Exception as e:
        return({'error':str(e)})


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
        return({'error':str(e)})
  def put(self, widgetId): #update
    try:
        jsondata = request.get_json(force=True)
        # _apiId = jsondata['id']
        _apiId = widgetId
        _apiApi_id = jsondata['api_id']
        _apiUser_id = jsondata['user_id']
        _apiCaption = jsondata['caption']
        _apiDescription = jsondata['description']
        _apiMapping_json = jsondata['mapping_json']
        query = "UPDATE myboard.widget SET api_id = %s,user_id = %s,caption = %s,description = %s,mapping_json = %s, created_time = now()  WHERE id = %s"
        return(flask.jsonify(executeSQL(query, (_apiApi_id,_apiUser_id,_apiCaption,_apiDescription,_apiMapping_json,_apiId ))))
    except Exception as e:
        return({'error':str(e)})
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
          return(flask.jsonify(rst[0]))
        return ('', 204)
    except Exception as e:
        return({'error':str(e)})


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
        _apiCaption = jsondata['caption']
        _apiDescription = jsondata['description']
        _apiMapping_json = jsondata['mapping_json']
        query = "INSERT INTO myboard.widget (id,api_id,user_id,caption,description,mapping_json,created_time) VALUES (null, %s, %s, %s, %s, %s, now())"
        return(flask.jsonify(executeSQL(query, ( _apiApi_id, _apiUser_id, _apiCaption, _apiDescription, _apiMapping_json))))
    except Exception as e:
        return({'error':str(e)})

###################### DASHBOARD API ######################
class userDashboardList(Resource):
    def get(self, userId): #dashboard list
        _apiUser_id = userId
        query = "SELECT id, name, icon, order_index FROM myboard.dashboard WHERE user_id=%s"
        return(selectSQL(query, (_apiUser_id)))
    def post(self, userId): #insert
        try:
            jsondata = request.get_json(force=True)
            _user_id = userId
            _name = jsondata['name']
            _icon = jsondata['icon']
            _order_index = jsondata['index']
            query = "INSERT INTO myboard.dashboard (id, user_id, name, icon, order_index) VALUES (null, %s, %s, %s, %s)"
            return(flask.jsonify(executeSQL(query, (_user_id, _name, _icon,_order_index))))
        except Exception as e:
            return({'error':str(e)})
    def put(self, userId): # dashboard update
        try:
            jsondata = request.get_json(force=True)
            query = "UPDATE myboard.dashboard SET name = %s, icon = %s, order_index = %s WHERE id = %s"
            for dashboard in jsondata:
                _id = dashboard['id']
                _name = dashboard['name']
                _icon = dashboard['icon']
                _order_index = dashboard['order_index']
                executeSQL(query, (_name, _icon, _order_index, _id ))
            return('', 204)
        except Exception as e:
            return({'error':str(e)})



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
            return({'error':str(e)})


    def delete(self, dashboardId): #del
        _dashboardId = dashboardId
        query = "DELETE FROM myboard.dashboard WHERE id = %s"
        return(flask.jsonify(executeSQL(query, (_dashboardId))))


class dashboardWidgetList(Resource):
    def get(self, dashboardId):
        _dashboardId = dashboardId
        
        query = 'SELECT w.*, wp.props_json FROM widget_pos wp inner join widget w on wp.widget_id = w.id where dashboard_id = %s'
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
                widget_id = obj['widget_id']
                props_json = obj['props_json']
                cursor.execute("INSERT INTO myboard.widget_pos (widget_id, dashboard_id, props_json) value (%s, , %s, %s);", (widget_id, dashboardId, json.dumps(props_json)))
            conn.commit()
        except Exception as e:
            conn.rollback()
            return({'error':str(e)})
        finally:
            cursor.close()
            conn.close()


class dashboardWidgetData(Resource):
    def get(self, dashboardId):
        _dashboardId = dashboardId
        query = 'SELECT widget.id, api_data.data FROM myboard.widget_pos inner join myboard.widget on myboard.widget_pos.widget_id = myboard.widget.id inner join api_data on widget.api_id = api_data.api_id where dashboard_id = %s'
        rst = selectSQL(query, (_dashboardId))
        return(flask.jsonify(rst))


###################### PROFILE API ######################
class profile(Resource):
    def get(self):
      if 'credentials' not in flask.session: return(flask.redirect(flask.url_for('oauth2callback')))
      # print(flask.session)
      return(flask.session['userId'])
      # cred = json.loads(flask.session['credentials'])
      # cred['access_token']


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
