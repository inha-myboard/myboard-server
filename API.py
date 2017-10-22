from selenium import webdriver
import time
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
#selenium
# driver = webdriver.PhantomJS('./PhantomJS.exe')

def inspector():
	inputjson = """{"type":"static","body_selector":"html > body > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div > ul > li","segments":[{"selector":"a > span:nth-child(1)","name":"rank"},{"selector":"a > span:nth-child(2)","name":"name"}]}"""
	data = json.loads(inputjson)
	url = 'https://www.naver.com/'
	
	driver.get(url)
	body = driver.find_element_by_css_selector(data['body_selector'])

	rst = list()
	for i in range(len(data["segments"])):
		rst.append(body.find_element_by_css_selector(data["segments"][i]['selector']).text)
	return(rst)

class myboardAPI(Resource):
	def get(self):
		try:
			query = "SELECT type, selector_json from myboard.api"
			cursor.execute(query)
			rows = cursor.fetchall()
			return(rows)
		except Exception as e:
			return({'error':str(e)})
	def post(self):
		try:
			#parsing
			# parser = reqparse.RequestParser()
			# parser.add_argument('url', type=str, required=True)
			# parser.add_argument('body_selector', type=str, required=True)
			# parser.add_argument('segments', type=str ,action='append', required=True)
			# parser.add_argument('type', type=str, required=True)
			# args = parser.parse_args()

			# _apiUrl = args['url']
			# _apiBody = args['body_selector']
			# _apiSegments = args['segments']
			# _apiType = args['type']
			jsondata = request.get_json(force=True)
			_apiUrl = jsondata['url']
			_apiBody = jsondata['body_selector']
			_apiSegments = jsondata['segments']
			_apiType = jsondata['type']

			#SQL
			query = "INSERT INTO myboard.api (id, type, selector_json) VALUES (null, %s,%s)"
			cursor.execute(query, (_apiType, jsondata))
			conn.commit()
			return({'StatusCode': '200', 'query': query%(_apiType, jsondata)})
		except Exception as e:
			return({'error':str(e)})
	def put(self):
		try:
			query = "UPDATE myboard.api SET type = \"ok\" WHERE id = 1"
			cursor.execute(query)
			conn.commit()
			return("test")
		except Exception as e:
			return({'error':str(e)})
	def delete(self):
		try:
			query = "DELETE FROM myboard.api WHERE id = 1"
			cursor.execute(query)
			conn.commit()
			return("delete")
		except Exception as e:
			return({'error':str(e)})

class inspectorAPI(Resource):
	def post(self):
		return(inspector())

class componentAPI(Resource):
	def post(self):
		try:
			query = "SELECT * from myboard.compoenet"
			cursor.execute(query)
			rows = cursor.fetchall()
			return(rows)
		except Exception as e:
			return({'error':str(e)})

class widgetAPI(Resource):
	def get(self): #list, search  #뒤에 변수값 있으면 search, null이면 list
		return()
	def post(self): #insert
		return()
	def put(self): #update
		return()
	def delete(self):
		return()

class dashboardAPI(Resource):
	def get(self): #dashboard list
		return()
	def post(self): #insert
		return()
	def delete(self): #del
		return()
api.add_resource(myboardAPI, '/myboardapi')
api.add_resource(inspectorAPI, '/inspectorapi')
api.add_resource(componentAPI, '/componentapi')
api.add_resource(widgetAPI, '/widgetapi')
api.add_resource(dashboardAPI, '/dashboardapi')

if __name__ == '__main__':
	#MySQL configurations
	app.config['MYSQL_DATABASE_USER'] = 'root'
	app.config['MYSQL_DATABASE_PASSWORD'] = '1234'
	app.config['MYSQL_DATABASE_DB'] = 'myboard'
	app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
	mysql.init_app(app)
	conn = mysql.connect()
	cursor = conn.cursor()

	app.run(debug=False)

#DB, flask