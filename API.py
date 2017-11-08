from selenium import webdriver
import time, re
import json
from flask import Flask, jsonify, request
from flaskext.mysql import MySQL
from flask_restful import Resource, Api
from flask_restful import reqparse

#flask
app = Flask(__name__)
api = Api(app)
#mySQL
mysql = MySQL()

def inspector(inputjson):
	driver = webdriver.PhantomJS('./PhantomJS')
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
	app.config.from_object(__name__)
	app.config.from_envvar('MYBOARD_SETTINGS', silent=True)
	mysql.init_app(app)
	conn = mysql.connect()
	cursor = conn.cursor()

	app.run(debug=False)