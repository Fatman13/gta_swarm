#!/usr/bin/env python
# coding=utf-8

import pprint
import csv
import click 
import requests
import datetime as datetime
from xml.etree import ElementTree as ET
import os
# import logging

url = 'https://rbs.gta-travel.com/rbscnapi/RequestListenerServlet'

pp = pprint

def validate_d(date_text):
	try:
		datetime.datetime.strptime(date_text, '%Y-%m-%d')
	except ValueError:
		raise ValueError("Incorrect data format, should be YYYY-MM-DD")

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)

res = []

@click.command()
@click.option('--hotel_code', default='MEL_912')
@click.option('--from_d', default='2017-04-01')
@click.option('--to_d', default='2017-04-03')
def spp(hotel_code, from_d, to_d):

	validate_d(from_d)
	validate_d(to_d)

	from_date = datetime.datetime.strptime(from_d, '%Y-%m-%d').date()
	to_date = datetime.datetime.strptime(to_d, '%Y-%m-%d').date()

	city_code, item_code = hotel_code.rstrip().split('_')

	search_tree = ET.parse(os.path.join(os.getcwd(), 'SearchHotelPricePaxRequest.xml'))
	search_tree.find('.//ItemDestination').set('DestinationCode', city_code)
	search_tree.find('.//ItemCode').text = item_code
	search_tree.find('.//PaxRoom').set('Adults', str(2))

	for single_date in daterange(from_date, to_date):
		search_tree.find('.//CheckInDate').text = single_date.strftime('%Y-%m-%d')
		
		r = requests.post(url, data=ET.tostring(search_tree.getroot(), encoding='UTF-8', method='xml'))

		r_tree = ET.fromstring(r.text)
		entry = dict()
		entry['GTA_key'] = hotel_code
		if (r_tree.find('.//RoomPrice') == None):
			# hotel_code['missing_price'].append('Pax ' + str(i + 1) + ': ' + single_date.strftime("%Y-%m-%d"))
			# pp.pprint('Alert: Price not returned... ')
			entry['Price'] = 'NULL'
		else:
			# pp.pprint('Gross: ' + str(r_tree.find('.//RoomPrice').get('Gross')))
			for hotel in r_tree.find('.//HotelDetails'):
				hotel_name = hotel.find('.//Item').text
				for room_cat in r_tree.find('.//RoomCategories'):
					pp.pprint('Id: ' + str(room_cat.get('Id')))
					pp.pprint('Id: ' + str(room_cat.find('.//Description').text))
					entry['Hotel_Name'] = hotel_name
					entry['Category_id'] = room_cat.get('Id')
					entry['Bed'] = room_cat.find('.//Description').text
					entry['Check_in'] = single_date.strftime('%Y-%m-%d')
					entry['Price'] = room_cat.find('.//ItemPrice').text
					entry['Currency'] = room_cat.find('.//ItemPrice').get('Currency')
					res.append(entry)

		# pp.pprint(res)

		

	keys = res[0].keys()
	with open('output.csv', 'w') as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		dict_writer.writeheader()
		dict_writer.writerows(res)
	

if __name__ == '__main__':
	spp()