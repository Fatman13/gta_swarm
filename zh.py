#!/usr/bin/env python
# coding=utf-8

import pprint
import csv
import click 
import requests
import datetime as datetime
from datetime import date
from xml.etree import ElementTree as ET
import os
# from random import sample
import random
# import logging

def validate_d(date_text):
	try:
		datetime.datetime.strptime(date_text, '%Y-%m-%d')
	except ValueError:
		raise ValueError("Incorrect data format, should be YYYY-MM-DD")

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)

@click.command()
@click.option('--file_name', default='hotel_codes_zh')
@click.option('--check_d', default='2017-05-15')
def zh(file_name, check_d):

	url = 'https://rbs.gta-travel.com/rbscnapi/RequestListenerServlet'
	pp = pprint
	res = []

	validate_d(check_d)

	check_d = datetime.datetime.strptime(check_d, '%Y-%m-%d').date()
	hotel_codes = []
	with open(file_name, 'r') as file:
		for line in file:
			# pp.pprint(line)
			city_code, item_code = line.rstrip().split('_')
			hotel_codes.append(dict([('city_code', city_code), ('item_code', item_code), ('has_zh', 'N')]))

	search_tree = ET.parse(os.path.join(os.getcwd(), 'SearchHotelPricePaxRequest.xml'))

	pp.pprint('Searching Language: ' + str(search_tree.find('.//RequestorPreferences').get('Language')))

	for hotel_code in hotel_codes:
		pp.pprint('Searching Price for ' + hotel_code['city_code'] + ' ' + hotel_code['item_code'])
		search_tree.find('.//ItemDestination').set('DestinationCode', hotel_code['city_code'])
		search_tree.find('.//ItemCode').text = hotel_code['item_code']
		# search_tree.find('.//PaxRoom').set('Adults', str(2))

		entry = dict()
		entry['Hotel_Code'] = hotel_code['city_code'] + '_' + hotel_code['item_code']

		search_tree.find('.//CheckInDate').text = check_d.strftime('%Y-%m-%d')
		pp.pprint('Check in date: ' + check_d.strftime('%Y-%m-%d'))
		search_tree.find('.//PaxRoom').set('Adults', str(2))

		# pp.pprint(ET.tostring(search_tree.getroot(), encoding='UTF-8', method='xml'))

		try:
			r = requests.post(url, data=ET.tostring(search_tree.getroot(), encoding='UTF-8', method='xml'), timeout=360)
		except OSError:
			pp.pprint('Error: ignoring OSError...')
			continue

		r_tree = ET.fromstring(r.text)
		# pp.pprint(r.text)
		if r_tree.find('.//Item') != None:
			pp.pprint('Hotel Name: ' + str(r_tree.find('.//Item').text))

			entry['has_hotel_name_zh'] = 'N'
			try:
				str(r_tree.find('.//Item').text).encode('latin1')
			except UnicodeEncodeError:
				entry['has_hotel_name_zh'] = 'Y'
			entry['hotel_name'] = str(r_tree.find('.//Item').text)

		entry['has_zh'] = 'N'
		try:
			r.text.encode('latin1')
		except UnicodeEncodeError:
			entry['has_zh'] = 'Y'

		res.append(entry)

	pp.pprint(res)
	keys = res[0].keys()
	# with open('output_SearchPrice_' + date.today().strftime('%Y_%m_%d') + '.csv', 'w', encoding='utf-8') as output_file:
	with open('output_has_zh_' + datetime.datetime.now().strftime('%Y_%m_%d_%H_%M') + '.csv', 'w', encoding='utf-8') as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		dict_writer.writeheader()
		dict_writer.writerows(res)
	

if __name__ == '__main__':
	zh()