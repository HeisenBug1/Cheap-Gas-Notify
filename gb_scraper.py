import requests, re, sys
from bs4 import BeautifulSoup
from typing import Union


# verify zipcode
def verify_zipcode(zipcode):

	if type(zipcode) is not str:
		zipcode = str(zipcode)
	zipcode.strip()

	zipcode_length = len(zipcode)

	pattern = re.compile(r"^[\d]+$")
	zipcode = pattern.match(zipcode)

	if zipcode_length != 5 or zipcode is None:
		return None

	return zipcode[0]


# get median
def get_median(datalist):
	n = len(datalist)
	return datalist[n//2]


# get soup object
def get_soup(search: Union[str, int, tuple]):

	search_type = type(search)

	if search_type == str or search_type == int:
		query = verify_zipcode(search)
		if query is None:
			print("Error: "+str(search)+" is not a correct zip code")
			sys.exit(1)
		URL = "https://www.gasbuddy.com/home?search="+ query +"&fuel=1&maxAge=0&method=credit"

	elif search_type == tuple:
		lat, lng = search
		if type(lat) == str and type(lng) == str:
			lat = float(lat)
			lng = float(lng)
		if type(lat) == float and type(lng) == float:
			query = 'lat='+str(lat)+'&lng='+str(lng)
			print(query)
			URL = "https://www.gasbuddy.com/home?search=fuel=1&maxAge=0&method=credit&"+query
		else:
			print(f'Invalid Lat & Lng received: {lat}, {lng}')
			sys.exit(2)
	else:
		print(f'Invalid argument in get_soup(). Required: Lat,Lng OR ZipCode. Received: {str(search)}')
		sys.exit(3)

	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36'}
	page = requests.get(URL, headers=headers)
	return BeautifulSoup(page.content, "html.parser")


# extract data from gas buddy
def get_gb_data(input_var):

	# type check for str or int or tuple not working
	if isinstance(input_var, (str, int, tuple)):
		soup = get_soup(input_var)

	elif isinstance(input_var, BeautifulSoup):
		soup = input_var

	else:
		print("Error: "+str(type(input_var))+" received.\nRequired either GPS cordinates OR zip code OR bs4 object")
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

		station_name = elm.find("h3", attrs={'class': re.compile('^header.*')}).find('a')
		station_address = elm.find("div", attrs={'class': re.compile('^StationDisplay-module__address.*')})

		station_data = (station_name.decode_contents(), format_address(station_address.decode_contents()), price)
		
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
# "123 Jump St, Manhattan, NY"  -->  ("123 Jump St", "Manhattan", "NY")
def format_address(address):

	address = address.split('<br/>')

	street = address[0].strip()

	address = address[1].split(',')

	city = address[0].strip()
	state = address[1].strip()

	return (street, city, state)
