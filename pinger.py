import requests
import time
import datetime


while True:
	res = requests.get("https://stock-chk.herokuapp.com/")
	print(datetime.datetime.now())
	print(res.status_code, end=" ")
	time.sleep(1200)