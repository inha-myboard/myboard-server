import requests
from bs4 import BeautifulSoup
import re


source = requests.get("http://www.naver.com")
html = source.text
soup = BeautifulSoup(html, "html.parser")
# bodyselector = "html > body > div > div > div > div > div > ul > li"
bodyselector = "html > body > div:nth-child(2) > div:nth-child(1) > div:nth-child(2) > div:nth-child(2) > div:nth-child(3) > ul:nth-child(4) > li"

# cont = soup.select(bodyselector)
cont = soup.select(bodyselector)
# print(cont)

cont = re.sub("<.*?>","",str(cont))
print(cont)




# {"type":"static","body_selector":"","segments":[{"selector":"a:nth-child(1) > span:nth-child(1)","name":"rank"},{"selector":"a:nth-child(1) > span:nth-child(2)","name":"cont"}]}