from selenium import webdriver
import time
import json
from flask import Flask
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

def inspectorAPI():
	inputjson = """{"type":"static","body_selector":"html > body > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div > ul > li","segments":[{"selector":"a > span:nth-child(1)","name":"rank"},{"selector":"a > span:nth-child(2)","name":"name"}]}"""
	data = json.loads(inputjson)
	url = 'https://www.naver.com/'
	
	driver.get(url)
	body = driver.find_element_by_css_selector(data['body_selector'])

	rst = list()
	for i in range(len(data["segments"])):
		rst.append(body.find_element_by_css_selector(data["segments"][i]['selector']).text)
	return(rst)

class CreateApi(Resource):
	def get(self):
		try:
			query = "SELECT * from myboard.api"
			cursor.execute(query)
			rows = cursor.fetchall()
			return(rows)
		except Exception as e:
			return({'error':str(e)})
	def post(self):
		try:
			parser = reqparse.RequestParser()
			parser.add_argument('url', type=str)
			parser.add_argument('body', type=str)
			parser.add_argument('segments', type=str)
			args = parser.parse_args()

			_apiUrl = args['url']
			_apiBody = args['body']
			_apiSegments = args['segments']
			
			query = "INSERT INTO myboard.api (id, type, selector_json) VALUES (null, %s,%s)"
			cursor.execute(query, (_apiBody, _apiSegments))
			conn.commit()
			return({'StatusCode': '200', 'query': query%(_apiBody, _apiSegments)})
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

api.add_resource(CreateApi, '/api')

if __name__ == '__main__':
	#MySQL configurations
	app.config['MYSQL_DATABASE_USER'] = 'root'
	app.config['MYSQL_DATABASE_PASSWORD'] = '1234'
	app.config['MYSQL_DATABASE_DB'] = 'myboard'
	app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
	mysql.init_app(app)
	conn = mysql.connect()
	cursor = conn.cursor()

	app.run(port = 8003, debug=False)

#DB, flask