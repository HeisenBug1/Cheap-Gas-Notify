import requests, re, sys
from bs4 import BeautifulSoup


# verify zipcode
def verify_zipCode(zipCode):

	if type(zipCode) is not str:
		zipCode = str(zipCode)
	zipCode.strip()

	zipCode_length = len(zipCode)

	pattern = re.compile(r"^[0-9]+$")
	zipCode = pattern.match(zipCode)

	if zipCode_length != 5 or zipCode is None:
		return None

	return zipCode[0]


# get median
def get_median(dataList):
	n = len(dataList)
	if n % 2 == 0:
		median1 = dataList[n//2]
		median2 = dataList[n//2 - 1]
		median = (median1 + median2)/2
	else:
		median = dataList[n//2]
	return median


# get soup object
def get_soup(zip_code):
	verified_zip_code = verify_zipCode(zip_code)
	if verified_zip_code is None:
		print("Error: "+str(zip_code)+" is not a correct zip code")
		sys.exit(1)
	URL = "https://www.gasbuddy.com/home?search="+ verified_zip_code +"&fuel=1&maxAge=0&method=credit"
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36'}
	page = requests.get(URL, headers=headers)
	return BeautifulSoup(page.content, "html.parser")


# extract data from gas buddy
def get_gb_data(input_var):

	if type(input_var) is str or type(input_var) is int:
		soup = get_soup(input_var)

	elif type(input_var) is BeautifulSoup:
		soup = input_var

	else:
		print("Error: "+type(input_var)+" received.\nRequired either zip code or bs4 object")
		sys.exit(2)

	# get all relative HTML elements containing gas price data
	elements = soup.find_all("div", attrs={'class': re.compile('^GenericStationListItem-module__stationListItem.*')})

	"""
		data list (tuples)  # all strings
		[   
			(Station Name, Station Address, Gas Price),
			(..., ..., ...),
			(..., ..., ...)
		]
		example: [ ( Exxon, (123 Jump St, Manhattan, NY), $13.99 ) ]
	"""
	all_data = []

	# loop through each HTML element to extract specific information
	for elm in elements:

		price = elm.find("div", attrs={'class': re.compile('^StationDisplayPrice-module__priceContainer.*')})
		price = price.find('span')
		price = format_price(price.text)

		# skip to next if price DNE
		if price is None:
			continue

		station_name = elm.find("h3", attrs={'class': re.compile('^header.*')})
		station_address = elm.find("div", attrs={'class': re.compile('^StationDisplay-module__address.*')})

		station_data = (station_name.text, format_address(station_address.text), price)
		# call function here to verify data before appending to all_data
		
		# add data to list as a tuple for each iteration
		all_data.append(station_data)

	if len(all_data) > 0:
		all_data.sort(key = sort_key)
		return (get_median(all_data), all_data)
	return None


# format gas price (remove $ sign)
def format_price(price):
	if "$" in price:
		return float(price.split("$")[1])
	return None


# sort function key
def sort_key(element):
	return element[2]


# format gas station address
def format_address(address):
	was_space = False
	index = 0

	for char in address:
		if was_space == False and char.isupper():
			# found index in string that separates street with city
			break
			# return index
		if char == ' ':
			was_space = True
		else:
			was_space = False
		index += 1

	street = address[:index]
	city, state = address[index:].split(",")
	city = city.strip()
	state = state.strip()

	# return tuple (street, city, state)
	return (street, city, state)
