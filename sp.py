#!/usr/bin/env python

import pprint
import os
import uuid
from xml.etree import ElementTree as ET
import requests
import datetime as datetime

# url of rbs API
url = 'https://rbs.gta-travel.com/rbscnapi/RequestListenerServlet'
from_date = datetime.date(2017, 4, 3)
to_date = datetime.date(2017, 4, 5)
counter = (to_date - from_date).days

pp = pprint.PrettyPrinter(indent=4)

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)

pp.pprint(str('/// /// /// Get Daily Price of Searching_Hotel_Price_Pax  /// /// ///'))
pp.pprint('how many days: ' + str(counter))

hotel_codes = []
with open('hotel_codes', 'r') as file:
	for line in file:
		city_code, item_code = line.rstrip().split('_')
		hotel_codes.append(dict([('city_code', city_code), ('item_code', item_code), ('missing_price', [])]))

pp.pprint(hotel_codes)

search_tree = ET.parse(os.path.join(os.getcwd(), 'SearchHotelPricePaxRequest.xml'))

for hotel_code in hotel_codes:
	pp.pprint('Searching Price for ' + hotel_code['city_code'] + ' ' + hotel_code['item_code'])

	for single_date in daterange(from_date, to_date):
		pp.pprint('Searching date: ' + single_date.strftime("%Y-%m-%d"))

		search_tree.find('.//ItemDestination').set('DestinationCode', hotel_code['city_code'])
		search_tree.find('.//ItemCode').text = hotel_code['item_code']

		for i in range(3):
			pp.pprint('Pax #: ' + str(i + 1))
			search_tree.find('.//PaxRoom').set('Adults', str(i + 1))
		
			r = requests.post(url, data=ET.tostring(search_tree.getroot(), encoding='UTF-8', method='xml'))

			pp.pprint('Search price status code: ' + str(r.status_code))
			# pp.pprint(r.headers)
			# pp.pprint('Search price Response body: ' + r.text)

			r_tree = ET.fromstring(r.text)
			if (r_tree.find('.//RoomPrice') == None):
				hotel_code['missing_price'].append('Pax ' + str(i + 1) + ': ' + single_date.strftime("%Y-%m-%d"))
				pp.pprint('Alert: Price not returned... ')
			else:
				# pp.pprint('Gross: ' + str(r_tree.find('.//RoomPrice').get('Gross')))
				for room_cat in r_tree.find('.//RoomCategories'):
					pp.pprint('Id: ' + str(room_cat.get('Id')))
					pp.pprint('Id: ' + str(room_cat.find('.//Description').text))

pp.pprint('/// /// /// Test Result /// /// ///')
pp.pprint(hotel_codes)