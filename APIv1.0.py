from selenium import webdriver
import time
import json
inputjson = """{"type":"static","body_selector":"html > body > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(1) > div > ul > li","segments":[{"selector":"a > span:nth-child(1)","name":"rank"},{"selector":"a > span:nth-child(2)","name":"name"}]}"""
data = json.loads(inputjson)
url = 'https://www.naver.com/'

driver = webdriver.PhantomJS('./PhantomJS.exe')
driver.get(url)
body = driver.find_element_by_css_selector(data['body_selector'])

rst = list()
for i in range(len(data["segments"])):
	rst.append(body.find_element_by_css_selector(data["segments"][i]['selector']).text)
print(rst)
#DB, flask