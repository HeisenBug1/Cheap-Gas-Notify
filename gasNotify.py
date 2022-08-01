import http.client, pickle, json, datetime, argparse, os, sys
# from collections import deque
from pathlib import Path
import gb_scraper as gb


# global variables
configFile = ''
args = ''
sender = ''
password = ''
receiver = ''
dataFile = ''
zipCode = None


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

	try:
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
		plt.title(str(len(data))+' Day Gas Price in '+city)

		# rotate x tick labels to fit properly
		plt.xticks(rotation=30)

		if fileName is None:
			# function to show the plot
			plt.show()
		else:
			path = dataFile+fileName
			plt.savefig(path)
			return(path)

	except ModuleNotFoundError:
		print("MatPlotLib is not installed")
		return None


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


# compare gas price
def compareGasPrice(data, days=30):

	try:
		days = -abs(days)
	except:
		print("Error: days parameter is not an integer")
		print("\tDefaulting to last 30 days")
		days = -30

	# make sure queue is not empty
	if len(data) == 0:
		print("Not data in dataset")
		return False

	lowestPrice = 9999999
	highestPrice = 0
	today = data[-1][0]	# datetime object
	todaysPrice = float(data[-1][1])
	lowestDay = None
	highestDay = None

	# find lowest day of gas price in dataset
	for date, price in data[days:]:

		curPrice = float(price)
		curDate = date

		# find lowest
		if lowestPrice >= curPrice:
			lowestDay = curDate
			lowestPrice = curPrice

		# find highest
		if highestPrice <= curPrice:
			highestPrice = curPrice
			highestDay = curDate

	# compare lowerest price with todays price
	if lowestPrice >= todaysPrice:
		return ("Today is a great time to buy.\n$"+str(round(todaysPrice, 2))+" in "+zipCode)
	else:
		lowestDay = today - lowestDay
		highestDay = today - highestDay

		output = "Today is $"+str(round(todaysPrice, 2))
		output += "\n\nLowest was "+str(lowestDay.days)+" days ago in "+zipCode+" at $"+str(round(lowestPrice, 2))
		output += " a difference of $"+str(round((todaysPrice - lowestPrice), 2))
		output += " ("+str(diff(todaysPrice, lowestPrice))+"%)"

		if highestDay.days > 0:
			output += "\n\nHighest was "+str(highestDay.days)+" days ago at $"+str(round(highestPrice, 2))
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
		print("Found config file: "+configFile)
		global sender
		global password
		global receiver
		global dataFile
		global zipCode
		with open(configFile, 'r') as file:
			lines = file.readlines()
		
		for line in lines:
			line = line.strip().split()
			option = line[0].lower()
			if len(line) == 1:
				print("error: "+str(line)+ " is missing argument(s)")
				continue
			elif len(line) == 2:
				if 'zip' == option:
					zipCode = line[1]
				if 'receiver' == option:
					receiver = line[1]
				if 'data' == option:
					dataFile = line[1]
					dataFilePath = Path(dataFile)
					# create data file if it does not exist
					if not dataFilePath.exists():
						# d = deque(maxlen=30)  # only holds 30 items
						d = []
						saveLoad('save', d, dataFile)
			elif len(line) == 3 and 'sender' == option:
				sender = line[1]
				password = line[2]
			else:
				print("error: "+str(line)+" has unusable arguments. Please fix")
		
		# required items to run app
		required = [ sender, password, receiver, dataFile, zipCode]
		req_text = ['sender', 'password', 'receiver', 'data', 'zip']
		missingItems = ''

		# if any item in reqired is missing, then print error and exit
		for i in range(len(required)):
			if required[i] == '':
				missingItems += req_text[i]+", "
		if missingItems != '':
			sys.exit("Error: "+configFile+" is missing arguments in:\n"+missingItems)

	else:
		parser = argparse.ArgumentParser(description='Notifies user when GAS price is low through email')
		parser.add_argument('-s', '--state', help='Shortcode of an US state', required=False)
		parser.add_argument('-c', '--city', help='Name of a city within the chosen US state', required=False)
		parser.add_argument('-e', '--sender', help='the sender email address to send emails from', required=True)
		parser.add_argument('-r', '--receiver', help='the receiver email address', required=True)
		parser.add_argument('-t', '--token', help='api token to get data from (https://collectapi.com/api/gasPrice/gas-prices-api/usaStateCode)', required=False)
		parser.add_argument('-d', '--data', help='exact location of where the data will be stored', required=False)
		parser.add_argument('-z', '--zip', help='Zip Code of desired location for its Gas price', required=True)

		args = parser.parse_args()

		os.makedirs(os.path.dirname(configFile), exist_ok=True)

		output = ('sender ' + args.sender
				+ '\nreceiver ' + args.receiver
				+ '\nzip' + args.zip)
		if args.data is not None:
			output += '\ndata ' + args.data
		else:
			output += '\n data ' + str(Path.home())+'/GasNotify/gas_data_'+args.zip+'.pkl'

		with open(configFile, 'w') as f:
			f.write(output)
		print("Open "+configFile+"\nand add SENDER's password beside. e.g: sender myEmail@gmail.com 12345678")
		sys.exit(1)

	print("Initialization complete ...")


# email a user
def send_email_OLD(mail_from, mail_to, msg):
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
def update():
	data = saveLoad('load', None, dataFile)
	today = datetime.date.today()

	# prevent new data addition if it already exists
	if today == data[-1][0]:
		return data

	gas = gb.get_gb_data(zipCode)

	# if new gas data was succesfully retrieved, then add to database
	if gas is not None:
		data.append((today, str(gas[0][2])))
		saveLoad('save', data, dataFile)
		print("New gas data added to database ..")

	# else notify about error
	else:
		msg = "Subject: Gas App ALERT\n\nCould not scrape data from Gas Buddy\n\n"
		send_email_OLD(sender, receiver, msg)
		print(msg)
		sys.exit(9)

	return data


# make sure this script is run directly and not as a module
if __name__ == "__main__":
	initialize()
	data = update()
	# data = saveLoad('load', None, dataFile)	# test
	msg = compareGasPrice(data)
	if sys.stdout.isatty() is True:
		print(msg)
	else:
		plot = get_plot(data, "plot.png")
		send_email(msg, plot)	# new email function
		# send_email(sender, receiver, msg)	# old email function

