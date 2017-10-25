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
	driver = webdriver.PhantomJS('./PhantomJS.exe')
	data = json.loads(inputjson)
	driver.get(data["url"])
	body = driver.find_element_by_css_selector(data['body_selector'])
	rst = list()
	for i in range(len(data["segments"])):
		rst.append(body.find_element_by_css_selector(data["segments"][i]['selector']).text)
	driver.close()
	print(rst)
	return(rst)

def selectSQL(query, parameter): #return
	try:
		cursor.execute(query,parameter)
		rows = cursor.fetchall()
		return(rows)
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
		query = "SELECT * from myboard.api"
		return(selectSQL(query))
	def post(self):
		try:
			#parsing
			jsondata = request.get_json(force=True)
			_apiUrl = jsondata['url']
			_apiBody = jsondata['body_selector']
			_apiSegments = jsondata['segments']
			_apiType = jsondata['type']
			#SQL
			#INSERT INTO myboard.api (id, user_id, name, caption, description, type, url, api_json, created_time) VALUES	(null, 1, "qwe", "cap", "qq", "qwe", "zz", "{\"selector\":\"a > span:nth-child(1)\",\"name\":\"rank\"}", now())
			query = "INSERT INTO myboard.api (id, user_id, name, caption, description, type, url, api_json, created_time) VALUES (null, %s, %s, %s, %s, %s, %s, %s, now())"

			# query = """INSERT INTO myboard.api (id, user_id, name, caption, description, type, url, api_json, created_time) VALUES	(null, 1, "qwe", "cap", "qq", "qwe", "zz", "{\"selector\":\"a > span:nth-child(1)\",\"name\":\"rank\"}", now())"""
			return(executeSQL(query, (1, "name", "caption", "??", _apiType, _apiUrl, json.dumps(jsondata))))
		except Exception as e:
			return({'error':str(e)})
	def put(self):
		query = "UPDATE myboard.api SET type = \"ok\" WHERE id = 1"
		return(executeSQL(query))
	def delete(self):
		query = "DELETE FROM myboard.api WHERE id = 1"
		return(executeSQL(query))

class inspectorAPI(Resource):
	def get(self):
		user_id = request.args.get("user_id")
		name = request.args.get("api_name")
		print(user_id)
		print(name)
		query = "SELECT api_json FROM myboard.api WHERE name=%s and user_id=%s"
		getjson = selectSQL(query,(name,user_id))
		print(json.loads(str(getjson[0][0])))
		# jsondata = request.get_json(force=True)
		# jsondata = """{"url":"http://www.naver.com",type":"static","body_selector":"html > body > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div > ul > li","segments":[{"selector":"a > span:nth-child(1)","name":"rank"},{"selector":"a > span:nth-child(2)","name":"name"}]}"""
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
api.add_resource(inspectorAPI, '/inspectorapi')
api.add_resource(widgetAPI, '/widgetapi')
api.add_resource(dashboardAPI, '/dashboardapi')

if __name__ == '__main__':
	#MySQL configurations
	# app.config['MYSQL_DATABASE_USER'] = 'root'
	# app.config['MYSQL_DATABASE_PASSWORD'] = '1234'
	# app.config['MYSQL_DATABASE_DB'] = 'myboard'
	# app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
	app.config.from_object(__name__)
	app.config.from_envvar('MYBOARD_SETTINGS', silent=True)
	mysql.init_app(app)
	conn = mysql.connect()
	cursor = conn.cursor()

	app.run(debug=False)