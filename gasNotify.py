import http.client, pickle, json, datetime, argparse, os, sys
from collections import deque
from pathlib import Path


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


# get X, Y value for plotting
def get_XY(data):
	x = []
	y = []
	# elm = tuple --> (datetime, dict)
	for elm in data:
		x.append(elm[0].strftime("%b %d"))
		cities = elm[1]['result']['cities']
		for a_city in cities:
			if city.lower() in a_city['lowerName']:
				y.append(float(a_city['gasoline']))

	return (x, y)


# create a plot of the date
def get_plot(data, fileName=None):

	import matplotlib.pyplot as plt

	x, y = get_XY(data)

	# set figure size
	plt.figure(figsize=(12,6), dpi=200)
	  
	# # plotting the points 
	plt.plot(x, y)
	  
	# # naming the x axis
	plt.xlabel('Date')
	# # naming the y axis
	plt.ylabel('Price')
	  
	# # giving a title to my graph
	plt.title('30 Day Gas Price in '+city)

	# rotate x tick labels to fit properly
	plt.xticks(rotation=30)

	if fileName is None:
		# function to show the plot
		plt.show()
	else:
		path = dataFile+fileName
		plt.savefig(path)
		return(path)



# get gas price by state (USA)
def get_gas_data(**call_api_using):
	x = ''
	y = ''
	stateCode = ''
	use_coordinates = False

	# iterate over all arguments passed
	for k, v in call_api_using.items():
		k = k.lower()
		if k == 'x':
			x = v.strip()
		if k == 'y':
			y = v.strip()
		if k == 'state':
			stateCode = v.strip().upper()

	# verify X,Y cords if they exist
	if x != '' or y != '':
		try:
			float(x)
			float(y)
		except:
			print("X,Y coordinates: "+str((x, y))+" is invalid.\nPleae fix in "+configFile)
		else:
			use_coordinates = True

	# if both X,Y and state are give, prioritize the coordinates
	if use_coordinates is True and stateCode != '':
		print("Prioritizing X,Y coordinates insted of state short code: "+stateCode
			+"\nIf you only want to use state short code, then plase remove X,Y coordinates from "+configFile)

	# verify state code is correct
	if use_coordinates is False and len(stateCode) != 2:
		sys.exit(str(stateCode)+" is an invalid US state short code.\nPlease fix in "+configFile)
	
	# if nothing is given
	if use_coordinates is False and stateCode == '':
		sys.exit("No valid form of API call given. Received: "+str((x, y, stateCode))
			+"\nPlease fix in "+configFile)

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

	# make sure a value exists for the city in data
	todaysVal = float(findCity(city, compareType, data[-1][1]))
	if todaysVal == False:
		print("No comparison made")
		return False

	lowestIndex = 99999
	lowestVal = 9999999
	highestIndex = 99999
	highestVal = 0
	today = data[-1][0]	# datetime object

	# find lowest day of gas price in dataset
	for i in range(len(data)):
		curVal = float(findCity(city, compareType, data[i][1]))
		curDate = data[i][0]

		# find lowest
		if lowestVal >= curVal:
			lowestIndex = i
			lowestVal = curVal

		# find highest
		if highestVal <= curVal:
			highestVal = curVal
			highestIndex = i

	# compare lowerest price with todays price
	if lowestVal >= todaysVal:
		return ("Today is a great time to buy.\n$"+str(round(todaysVal, 2))+" in "+city)
	else:
		lowestDay = today - data[lowestIndex][0]
		highestDay = today - data[highestIndex][0]

		output = "Today is $"+str(round(todaysVal, 2))
		output += "\n\nLowest was "+str(lowestDay.days)+" days ago in "+city+" at $"+str(round(lowestVal, 2))
		output += " a difference of $"+str(round((todaysVal - lowestVal), 2))
		output += " ("+str(diff(todaysVal, lowestVal))+"%)"

		if highestDay.days > 0:
			output += "\n\nHighest was "+str(highestDay.days)+" days ago at $"+str(round(highestVal, 2))
		else:
			output += "\n\nHighest is today."
			
		return output

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
		
		# required items to run app
		required = [state, city, sender, password, receiver, token]
		missingItems = ''

		# if any item in reqired is missing, then print error and exit
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


# convert text with newlines to HTML format
def to_html(msg):
	# print(msg)
	new_msg = ""
	for line in msg.splitlines():
		new_msg += line + "<br>"
	return new_msg


# test email
def send_email(body, plot=None):
	import smtplib, ssl
	from email.mime.multipart import MIMEMultipart
	from email.mime.text import MIMEText
	from email.mime.image import MIMEImage

	msg = MIMEMultipart()
	msg['Subject'] = 'Gas Price Notification'
	msg['From'] = sender
	msg['To'] = receiver

	body = to_html(body)

	msgText = MIMEText('<p>%s</p>' % (body), 'html')
	msg.attach(msgText)

	if plot is not None:
		with open(plot, 'rb') as fp:
			img = MIMEImage(fp.read())
			img.add_header('Content-Disposition', 'attachment', filename=plot)
			msg.attach(img)

	port = 465  # For SSL
	smtp_server = "smtp.gmail.com"
	context = ssl.create_default_context()
	with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
		server.login(sender, password)
		server.sendmail(sender, receiver, msg.as_string())


# update date using API call
def update(api_call_type):
	dataNY = saveLoad('load', None, dataFile)
	today = datetime.date.today()

	# prevent new data addition if it already exists
	for elm in dataNY:
		if today in elm:
			return dataNY

	# else get new data
	if type(api_call_type) == tuple:	# X,Y coordinates
		gas = get_gas_data(x=str(api_call_type[0]), y=str(api_call_type[1]))
	elif type(api_call_type) == str:	# US State (eg: NY)
		gas = get_gas_data(state=api_call_type)
	else:
		sys.exit("Invalid API call type")

	# if API call is successful add to database
	if gas['success'] is True and len(gas['result']) > 0:
		dataNY.append((today, gas))
		saveLoad('save', dataNY, dataFile)

	# else notify about error
	else:
		msg = "Subject: Gas App ALERT\n\nAPI call failed\n\n"+str(gas)
		send_email(sender, receiver, msg)
		sys.exit(msg)

	return dataNY



initialize()
dataNY = update(state)	# API serves invalid data when using X,Y coords. Defaulting to state again
# dataNY = saveLoad('load', None, dataFile)	# test
msg = compareGasPrice(city, 'reg', dataNY)
if sys.stdout.isatty() is True:
	print(msg)
else:
	plot = get_plot(dataNY, "plot.png")
	send_email(msg, plot)	# new email function
	# send_email(sender, receiver, msg)	# old email function

