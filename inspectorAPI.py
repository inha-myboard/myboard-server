# -*- coding: utf-8 -*-
import myboard_server
import json
import time
myboard_server.prepare()

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
	
	select = "SELECT id, url, api_json FROM myboard.api;"
	#select = "SELECT api.id, api_json FROM api LEFT JOIN api_data ON api.id = api_data.api_id WHERE api_data.api_id is NULL"
	error_count = 0
	while True:
		try:
			dataList = myboard_server.selectSQL(select, ())
			insert = "INSERT INTO myboard.api_data (api_id, data, updated_time) VALUES (%s, %s, now()) ON DUPLICATE KEY UPDATE data=%s, updated_time=now()"
			for i in range(len(dataList)):
				sql_data = json.dumps(myboard_server.inspect(dataList[i]['url'], str(dataList[i]['api_json'])))
				sql_id = dataList[i]['id']
				print(myboard_server.executeSQL(insert, (sql_id, sql_data, sql_data)))
				# print(sql_id)
				# print(sql_data)
		except Exception as e:
			print(str(e))
			error_count += 1
			if error_count >= 3:
				print("Error count is over three time. Exit")
				break
		finally:
			time.sleep(270)

	driver.close()
