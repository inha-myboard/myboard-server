# test
from selenium import webdriver
import selenium.webdriver.support.ui as ui
import json
import time
import flask
from flaskext.mysql import MySQL
mysql = MySQL()
app = flask.Flask(__name__)

def inspector(inputjson):
	data = json.loads(inputjson.replace('\'','"'))#json or str to dict
	driver.get(data["url"])
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

if __name__ == '__main__':
	#naver
	# data = {'url': 'http://www.naver.com', 'type': 'static', 'segments': [{'name': 'rank', 'selector': 'a > span:nth-child(1)'}, {'name': 'name', 'selector': 'a > span:nth-child(2)'}], 'body_selector': 'html > body > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div > ul > li'}
	#inha cse board
	# data = {'url':'http://cse.inha.ac.kr/','type':'static','body_selector':'html > body > form > div:nth-child(3) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > ul > li','segments':[{'selector':'a','name':'segment0'},{'selector':'span','name':'segment1'}]}
	#naver sport img -> ajax
	# data = {'url':'http://sports.news.naver.com/index.nhn','type':'static','body_selector':'html > body > div:nth-child(4) > div:nth-child(3) > div > div > div:nth-child(6) > div:nth-child(1) > a > div','segments':[{'selector':'img','name':'news'}]}
	#inha cse img
	# data = {'url':'http://cse.inha.ac.kr/','type':'static','body_selector':'html > body > form > div:nth-child(3) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > div > a','segments':[{'selector':'img','name':'segment0'}]}
	# print(inspector(str(data)))
	
	driver = webdriver.PhantomJS('./PhantomJS')
	
	app.config.from_object(__name__)
	app.config.from_envvar('MYBOARD_SETTINGS', silent=False)
	mysql.init_app(app)
	conn = mysql.connect()
	cursor = conn.cursor()

	# rst = dict()
	select = "SELECT id, url, api_json FROM myboard.api;"
	insert = "INSERT INTO myboard.api_data (id, api_ID, data) VALUES (null, %s, %s) ON DUPLICATE KEY UPDATE data=%s"
	temp = selectSQL(select)
	for i in range(len(temp)):
		sql_data = json.dumps(inspector(str(temp[i]['api_json'])))
		sql_id = temp[i]['id']
		print(executeSQL(insert, (sql_id, sql_data, sql_data)))
		# print(sql_id)
		# print(sql_data)
			
	driver.close()