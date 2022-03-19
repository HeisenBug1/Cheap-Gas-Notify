import http.client
import pickle
import json
from collections import deque
import datetime
from pathlib import Path
import argparse
import os
import sys


# global variables
configFile = ''
args = ''
state = ''
city = ''
email = ''
password = ''


# get gas price by state (USA)
def getGasByState(stateCode):
	conn = http.client.HTTPSConnection("api.collectapi.com")

	headers = {
		'content-type': "application/json",
		'authorization': "apikey 5xe4yYRAZ7VT8fGHs9uMom:2UUt710Y8KVEHPptJNWmaG"
		}

	conn.request("GET", "/gasPrice/stateUsaPrice?state="+stateCode, headers=headers)

	res = conn.getresponse()
	data = res.read()

	return json.loads(data.decode("utf-8")) # returns a dict


# check for new month to backup data to HDD instead of RamDisk
def end_of_month(dt):
	todays_month = dt.month
	tomorrows_month = (dt + datetime.timedelta(days=1)).month
	return True if tomorrows_month != todays_month else False


# safe/load data to/from file
def saveLoad(type, data, fileName):

	if type == "save":
		# write data to file
		with open(fileName, 'wb') as file:
			pickle.dump(data, file)
		return True

	elif type == "load":
		# read data from file
		with open(fileName, 'rb') as file:
			return pickle.load(file)

	else:
		print("Type: wrong")
		return False


# find a city's gas price in data
def findCity(city, returnType, data):
	for cities in data['result']['cities']:
		if city in str(cities).lower():
			regular = float(cities['gasoline'])
			midGrade = float(cities['midGrade'])
			premium = float(cities['premium'])
			diesel = float(cities['diesel'])

			if returnType == 'all':
				return (city +"\n---------------\nRegular: "+str(regular)+"\nMidGrade: "+str(midGrade)+"\nPremium: "+str(premium)+"\nDiesel: "+str(diesel)+"\n")
			elif returnType == 'reg':
				return regular
			elif returnType == 'mid':
				return regular
			elif returnType == 'pre':
				return premium
			elif returnType == 'die':
				return diesel
			else:
				print("DataType: "+returnType+" does not exist")
				return False
	print(city + " does not exist in dataset")
	return False


# compare gas price
def compareGasPrice(city, compareType, data):

	# make sure queue is not empty
	if len(data) == 0:
		print("Not data in dataset")
		return False

	# dataList = list(data.queue)	# make a copy of queue

	# make sure city exists in data
	todaysVal = float(findCity(city, compareType, data[-1][1]))
	if todaysVal == False:
		print("No comparison made")
		return False

	lowestIndex = 99999
	lowestVal = 9999999

	# find lowest day of gas price in dataset
	for i in range(len(data)):
		curVal = float(findCity(city, compareType, data[i][1]))
		if lowestVal > curVal:
			lowestIndex = i
			lowestVal = curVal

	# compare lowerest price with todays price
	if lowestVal >= todaysVal:
		return ("Today is a great time to buy.\n$"+str(todaysVal)+" in "+city)
	else:
		return ("Lowest was "+str(len(dataList)-lowestIndex)+" days ago")


# check if all required files exist, else create them
def initialize():
	global configFile
	global args

	configFile = str(Path.home())+'/GasNotify/config.txt'
	path = Path(configFile)
	if path.exists():
		global state
		global city
		global email
		global password
		with open(configFile, 'r') as file:
			lines = file.readlines()
		if len(lines) == 4:
			state = lines[0].strip()
			city = lines[1].strip()
			email = lines[2].strip()
			password = lines[3].strip()
		else:
			sys.exit("Error: Open "+configFile+" and add your gmail password at the end")

	else:
		parser = argparse.ArgumentParser(description='Notifies user when GAS price is low through email')
		parser.add_argument('-s', '--state', help='Shortcode of an US state', required=True)
		parser.add_argument('-c', '--city', help='Name of a city within the chosen US state', required=True)
		parser.add_argument('-e', '--email', help='the email address to send notification to', required=True)

		args = parser.parse_args()

		os.makedirs(os.path.dirname(configFile), exist_ok=True)

		with open(configFile, 'w') as f:
			f.write(args.state+'\n'+args.city+'\n'+args.email+'\n')
		print("Open "+configFile+"\nand add your gmail password at the end")


# email a user
def send_email(mail_from, mail_to, msg):
	import smtplib, ssl

	port = 465  # For SSL
	smtp_server = "smtp.gmail.com"
	sender_email = mail_from  # Enter your address
	receiver_email = mail_to  # Enter receiver address
	global password
	message = "Subject: Gas Price Notification\n\n"+msg

	context = ssl.create_default_context()
	with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
		server.login(sender_email, password)
		server.sendmail(sender_email, receiver_email, message)


# update date using API call
def update():
	dataNY = saveLoad('load', None, 'gas_last_30day_NY.pkl')
	today = datetime.date.today()
	gas = getGasByState(state)
	dataNY.append((today, gas))
	saveLoad('save', dataNY, 'gas_last_30day_NY.pkl')
	return dataNY



initialize()
# dataNY = update()
dataNY = saveLoad('load', None, 'gas_last_30day_NY.pkl')
send_email('rez.net.r6700@gmail.com', email, compareGasPrice(city, 'reg', dataNY))