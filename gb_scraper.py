from audioop import add
import requests, re, sys
from bs4 import BeautifulSoup


# verify zipcode
def verify_zipCode(input):
    pattern = re.compile(r"^[0-9]+$")
    zipCode = pattern.match(str(input))[0]
    zipCode_length = len(zipCode)

    if zipCode_length > 0 and zipCode_length < 6:
    	return zipCode

    return None


# get soup object
def get_soup(zip_code):
	verified_zip_code = verify_zipCode(zip_code)
	if verified_zip_code is None:
		print("Error: "+str(zip_code)+" is not a corrent Zip code.")
		sys.exit(1)
	URL = "https://www.gasbuddy.com/home?search="+ verified_zip_code +"&fuel=1&maxAge=0&method=credit"
	headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36'}
	page = requests.get(URL, headers=headers)
	return BeautifulSoup(page.content, "html.parser")


# extract data from gas buddy
def get_gb_data(soup):

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

	all_data.sort(key = sort_key)
	return all_data


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
