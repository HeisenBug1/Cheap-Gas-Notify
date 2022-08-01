import gb_scraper as gb
import pickle, sys, re, datetime
from bs4 import BeautifulSoup

# soup = gb.get_soup("https://www.gasbuddy.com/home?search=14043&fuel=1&maxAge=0&method=credit")

def pickle_obj(obj, fName=None):
	limit = 100
	if fName is None:
		fName = "soup"

	while True:
		try:
			with open(fName, "wb") as file:
				pickle.dump(obj, file)
			print("Limit: "+str(limit)+" worked")
			break
		except RecursionError:
			print("Limit: "+str(limit)+" didn't work")
			limit += 100
			sys.setrecursionlimit(limit)


def load_soup(location=None):
	if location is None:
		with open("soup", "rb") as file:
			return pickle.load(file)
	else:
		with open(location, "rb") as file:
			return pickle.load(file)


# soup = gb.get_soup(14043)
# pickle_obj(soup)
# print(type("streasd"))
# print(gb.get_gb_data(14043))
# print(type(12))
# soup = load_soup("/home/rez/ramdisk/gas_data_NY_persistent.pkl")



data = load_soup("/home/rez/ramdisk/14043.pkl")
# print(type(data[0][1]))
print(data[0][1])






# print(data[-1][0])
# date = datetime.date(2022, 7, 21)
# if date == data[-1][0]:
# 	print('True')
# else:
# 	print('False')


# data = gb.get_gb_data(14043)
# pickle_obj(data, '/home/rez/ramdisk/gasData.pkl')
# data = load_soup('/home/rez/ramdisk/gasData.pkl')
# print(data[0][2])





# print(soup[1][0])\
# print(len(soup))
# for i in range(len(soup[0][1]['result']['cities'])):
# newData = []
# for i in range(len(soup)):
	# print(soup[i][1]['result']['cities'][3])
	# newData.append((soup[i][0], soup[i][1]['result']['cities'][3]['gasoline']))
# pickle_obj(newData, "14043.pkl")
# for d, p in newData:
# 	print(d, end="\t")
# 	print(p)
# print(soup[0][1]['result']['cities'])
# print(soup[0][1]['result']['cities'][0])
# newData = [(d, p["buffalo-niagara falls"]) for (d, p) in soup]
# if type(soup) is BeautifulSoup:
# 	print("yes")
# else:
# 	print("no")
# print(gb.get_gb_data(soup)[0])


# print(len(gb.get_gb_data(soup)))
# print(soup.prettify())
# for station, address, price in gb.get_gb_data(load_soup()):
	# print(format_price(price))
	# print(price)