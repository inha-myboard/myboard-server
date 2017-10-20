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
			
			query = "INSERT into api (id, type, url, selector_json) values (0,%s,%s,%s)"
			cursor.execute(query, (_apiBody, _apiUrl, _apiSegments))
			conn.commit()
			data = cursor.fetchone()

			if len(data) is 0:
				conn.commit()
				return({'StatusCode': '200', 'Message': 'User creation success'})
			else:
				return({'StatusCode': '1000', 'Message': str(data[0])})
			# return( {'status':'success'})
		except Exception as e:
			return({'error':str(e)})

api.add_resource(CreateApi, '/api')

if __name__ == '__main__':
	#MySQL configurations
	app.config['MYSQL_DATABASE_USER'] = 'root'
	app.config['MYSQL_DATABASE_PASSWORD'] = '1234'
	app.config['MYSQL_DATABASE_DB'] = 'mydb'
	app.config['MYSQL_DATABASE_HOST'] = '127.0.0.1'
	mysql.init_app(app)
	conn = mysql.connect()
	cursor = conn.cursor()

	app.run(debug=False)

#DB, flask