from audioop import add
import requests, re
from bs4 import BeautifulSoup


# get soup object
def get_soup(URL):
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

        station_name = elm.find("h3", attrs={'class': re.compile('^header.*')})
        station_address = elm.find("div", attrs={'class': re.compile('^StationDisplay-module__address.*')})
        price = elm.find("div", attrs={'class': re.compile('^StationDisplayPrice-module__priceContainer.*')}).find('span')

        station_data = (station_name.text, format_address(station_address.text), price.text)
        # call function here to verify data before appending to all_data
        
        # add data to list as a tuple for each iteration
        all_data.append(station_data)

    return all_data


# format gas price (remove $ sign)
def format_price(price):
    if "$" in price:
        return price.split("$")[1]
    return None


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
