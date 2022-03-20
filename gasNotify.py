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
sender = ''
password = ''
receiver = ''
token = ''
dataFile = ''


# get gas price by state (USA)
def getGasByState(stateCode):
	conn = http.client.HTTPSConnection("api.collectapi.com")

	headers = {
		'content-type': "application/json",
		'authorization': "apikey "+token
		}

	conn.request("GET", "/gasPrice/stateUsaPrice?state="+stateCode, headers=headers)

	res = conn.getresponse()
	data = res.read()

	return json.loads(data.decode("utf-8")) # returns a dict


# (NOT USED) check for new month to backup data to HDD instead of RamDisk
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
		global sender
		global password
		global receiver
		global token
		global dataFile
		with open(configFile, 'r') as file:
			lines = file.readlines()
		
		for line in lines:
			line = line.strip().split()
			option = line[0].lower()
			if len(line) == 1:
				print("error: "+str(line)+ " is missing argument(s)")
				continue
			elif len(line) == 2:
				if 'state' == option:
					state = line[1].upper()
				if 'city' == option:
					city = line[1]
				if 'receiver' == option:
					receiver = line[1]
				if 'token' == option:
					token = line[1]
				if 'data' == option:
					dataFile = line[1]
			elif len(line) == 3 and 'sender' == option:
				sender = line[1]
				password = line[2]
			else:
				print("error: "+str(line)+" has unusable arguments. Please fix")
		
		required = [state, city, sender, password, receiver, token]
		missingItems = ''
		for item in required:
			if item == '':
				missingItems += item+", "
		if missingItems != '':
			sys.exit("Error: "+configFile+" is missing items:\n"+missingItems)

	else:
		parser = argparse.ArgumentParser(description='Notifies user when GAS price is low through email')
		parser.add_argument('-s', '--state', help='Shortcode of an US state', required=True)
		parser.add_argument('-c', '--city', help='Name of a city within the chosen US state', required=True)
		parser.add_argument('-e', '--sender', help='the sender email address to send emails from', required=True)
		parser.add_argument('-r', '--receiver', help='the receiver email address', required=True)
		parser.add_argument('-t', '--token', help='api token to get data from (https://collectapi.com/api/gasPrice/gas-prices-api/usaStateCode)', required=True)
		parser.add_argument('-d', '--data', help='exact location of where the data will be stored', required=False)

		args = parser.parse_args()

		os.makedirs(os.path.dirname(configFile), exist_ok=True)

		output = ('state ' + args.state
				+ '\ncity ' + args.city
				+ '\nsender ' + args.sender
				+ '\nreceiver ' + args.receiver
				+ '\ntoken ' + args.token)
		if args.data is not None:
			output += '\ndata ' + args.data
		else:
			output += '\n data ' + str(Path.home())+'/GasNotify/gas_data_'+args.state+'.pkl'

		with open(configFile, 'w') as f:
			f.write(output)
		sys.exit("Open "+configFile+"\nand add SENDER's password beside. e.g: sender myEmail@gmail.com 12345678")


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
	dataNY = saveLoad('load', None, dataFile)
	today = datetime.date.today()
	gas = getGasByState(state)
	dataNY.append((today, gas))
	saveLoad('save', dataNY, dataFile)
	return dataNY



initialize()
dataNY = update()
# dataNY = saveLoad('load', None, dataFile)	# test
send_email(sender, receiver, compareGasPrice(city, 'reg', dataNY))
