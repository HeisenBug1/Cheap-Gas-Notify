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
def get_gas_data(**call_api_using):

	x = ''
	y = ''
	stateCode = ''

	# iterate over all arguments passed
	for k, v in call_api_using.items():
		k = k.lower()
		if k == 'x':
			x = v
		if k == 'y':
			y = v
		if k == 'state':
			stateCode = v.upper()

	# if both X,Y and state are give, prioritize the coordinates
	if x and y != '' and stateCode != '':
		use_coordinates = True
		print("Prioritizing X, Y coordinates insted of state short code: "+stateCode
			+"\nIf you only want to use state short code, then plase remove X,Y coordinates from "+configFile)
	
	# if only state short code is given
	elif x and y == '' and stateCode != '':
		if len(stateCode) > 2:
			sys.exit(str(stateCode)+" is an invalid US state short code.\nPlease fix in "+configFile)
		print("using only state code")
		use_coordinates = False

	# if only state is give OR X,Y is missing one
	elif x or y == '' and stateCode != '':
		print("Only one coordinate is given, using state short code: "+stateCode+" instead")
		use_coordinates = False

	# if none is give then exit
	else:
		sys.exit('No form of API call given. Should be either X,Y coordinates or State Short Code'
			+'\nPlease fix it in '+configFile)

	print((x, y, stateCode, use_coordinates))
	return

	conn = http.client.HTTPSConnection("api.collectapi.com")

	headers = {
		'content-type': "application/json",
		'authorization': "apikey "+token
		}

	if use_coordinates is True:
		conn.request("GET", "/gasPrice/fromCoordinates?lng="+x+"&lat="+y, headers=headers)
	else:
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
		if city.lower() in str(cities).lower():
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
		return ("Lowest was "+str(len(data)-(lowestIndex+1))+" days ago in "+city
			+" at $"+str(lowestVal)
			+"\nToday is $"+str(todaysVal)
			+" a difference of "+str(diff(todaysVal, lowestVal))+"%")

# % diff between 2 values
def diff(val1, val2):
	return round(((abs(val1-val2)/((val1+val2)/2))*100), 2)


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
			elif len(line) >= 3 and 'city' == option:
				for name in line[1:]:
					city += name+" "
				city = city.strip()
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
	if 'Subject:' in msg:
		message = msg
	else:
		message = "Subject: Gas Price Notification\n\n"+msg

	context = ssl.create_default_context()
	with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
		server.login(sender_email, password)
		server.sendmail(sender_email, receiver_email, message)


# update date using API call
def update(api_call_type):
	dataNY = saveLoad('load', None, dataFile)
	today = datetime.date.today()

	# prevent new data addition if it already exists
	for elm in dataNY:
		if today in elm:
			return dataNY

	# else get new data
	if type(api_call_type) == tuple:
		gas = get_gas_data(x=str(api_call_type[0]), y=str(api_call_type[1]))
	elif type(api_call_type) == str:
		gas = get_gas_data(state=api_call_type)
	else:
		sys.exit("Invalid API call type")

	# if API call is successful add to database
	if gas['success'] is True and len(gas['result']) > 0:
		dataNY.append((today, gas))
		# saveLoad('save', dataNY, dataFile)

	# else notify about error
	else:
		msg = "Subject: Gas App ALERT\n\nAPI call failed\n\n"+str(gas)
		send_email(sender, receiver, msg)
		sys.exit(msg)

	return dataNY



initialize()
# dataNY = update(state)	# API serves invalid data when using X,Y coords. Defaulting to state again
# msg = compareGasPrice(city, 'reg', dataNY)
# send_email(sender, receiver, msg)

# dataNY = saveLoad('load', None, dataFile)	# test

print("Only XY")
get_gas_data(x=1, y=2)
print("-----------\n\nOnly state")
get_gas_data(state='NYC')
print("-----------\n\nX and state")
get_gas_data(y=2, state="NYC")
