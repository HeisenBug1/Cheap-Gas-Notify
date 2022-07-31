import gb_scraper as gb
import pickle, sys, re

# soup = gb.get_soup("https://www.gasbuddy.com/home?search=14043&fuel=1&maxAge=0&method=credit")

def pickle_obj(obj):
	limit = 100

	while True:
		try:
			with open("soup", "wb") as file:
				pickle.dump(obj, file)
			print("Limit: "+str(limit)+" worked")
			break
		except RecursionError:
			print("Limit: "+str(limit)+" didn't work")
			limit += 100
			sys.setrecursionlimit(limit)


def load_soup():
	with open("soup", "rb") as file:
		return pickle.load(file)


# soup = gb.get_soup(14043)
# pickle_obj(soup)
# print(type(soup))
# print(type("streasd"))
print(gb.get_gb_data(14043))
# print(type(12))


# print(len(gb.get_gb_data(soup)))
# print(soup.prettify())
# for station, address, price in gb.get_gb_data(load_soup()):
	# print(format_price(price))
	# print(price)