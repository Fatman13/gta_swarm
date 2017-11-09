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
import json

def validate_d(date_text):
	try:
		datetime.datetime.strptime(date_text, '%Y-%m-%d')
	except ValueError:
		raise ValueError("Incorrect data format, should be YYYY-MM-DD")

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)

# booking_id_secret = None
# with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secrets.json')) as data_file:    
# 	booking_id_secret = (json.load(data_file))['booking_id']

REF_API = 'api'
REF_CLIENT = 'client'
REF_AGENT = 'agent'

TYPE_DEPARTURE = 'departure'
TYPE_CREATION = 'creation'

@click.command()
@click.option('--days', default=0, type=int)
@click.option('--duration', default=0, type=int)
# @click.option('--client', default='ctrip_di')
@click.option('--d_type', default=TYPE_DEPARTURE)
def booking_id_ctrip(days, duration, d_type):

	url = 'https://rbs.gta-travel.com/rbscnapi/RequestListenerServlet'
	pp = pprint
	res = []
	clients = ['ctrip', 'ctrip_di', 'ctrip_dd']

	# validate_d(from_d)
	# validate_d(to_d)

	from_date = datetime.datetime.today().date() + datetime.timedelta(days=days)
	to_date = from_date + datetime.timedelta(days=duration)

	print('Search booking.. ' + from_date.strftime('%Y-%m-%d'))
	# print('Duration.. ' + )

	# from_date = datetime.datetime.strptime(from_d, '%Y-%m-%d').date()
	# to_date = datetime.datetime.strptime(to_d, '%Y-%m-%d').date()

	# pp.pprint('? ' + str(skip))

	# hotel_codes = []
	# with open(file_name, 'r') as file:
	# 	for line in file:
	# 		# pp.pprint(line)
	# 		city_code, item_code = line.rstrip().split('_')
	# 		hotel_codes.append(dict([('city_code', city_code), ('item_code', item_code), ('missing_price', [])]))

	agent_secret = None
	with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secrets.json')) as data_file:
		agent_secret = json.load(data_file)

	search_tree = ET.parse(os.path.join(os.getcwd(), 'SearchBookingRequest.xml'))

	for client in clients:

		search_tree.find('.//RequestorID').set('Client', agent_secret[client]['id'])
		search_tree.find('.//RequestorID').set('EMailAddress', agent_secret[client]['email'])
		search_tree.find('.//RequestorID').set('Password', agent_secret[client]['password'])

		search_tree.find('.//FromDate').text = from_date.strftime('%Y-%m-%d')
		search_tree.find('.//ToDate').text = to_date.strftime('%Y-%m-%d')
		search_tree.find('.//BookingDateRange').set('DateType', d_type)

		try:
			r = requests.post(url, data=ET.tostring(search_tree.getroot(), encoding='UTF-8', method='xml'), timeout=600)
		except OSError:
			pp.pprint('Error: OSError.. Searching has stopped..')
			return

		r_tree = ET.fromstring(r.text)

		for booking in r_tree.find('.//Bookings'):
			entry = {}
			entry['client_booking_id'] = entry['agent_booking_id'] = entry['gta_api_booking_id'] = ''
			entry['booking_status'] = entry['booking_creation_date'] = entry['booking_departure_date'] = ''
			entry['booking_name'] = entry['booking_net_price'] = entry['booking_currency'] = ''

			for booking_ref in booking.find('.//BookingReferences'):
				ref_type = booking_ref.get('ReferenceSource')

				if ref_type == REF_CLIENT:
					entry['client_booking_id'] = booking_ref.text
				if ref_type == REF_AGENT:
					entry['agent_booking_id'] = booking_ref.text
				if ref_type == REF_API:
					entry['gta_api_booking_id'] = '041/' + booking_ref.text

			entry['booking_status'] = booking.find('.//BookingStatus').text
			entry['booking_creation_date'] = booking.find('.//BookingCreationDate').text
			entry['booking_departure_date'] = booking.find('.//BookingDepartureDate').text
			entry['booking_name'] = booking.find('.//BookingName').text
			entry['booking_net_price'] = booking.find('.//BookingPrice').get('Nett')
			entry['booking_currency'] = booking.find('.//BookingPrice').get('Currency')

			# fix client with multi ids
			entry['client_name'] = client
			res.append(entry)

	# keys = res[0].keys()
	keys = res[0].keys()
	# with open('output_SearchPrice_' + date.today().strftime('%Y_%m_%d') + '.csv', 'w', encoding='utf-8') as output_file:
	with open('output_Search_booking_id_' + from_date.strftime('%y%m%d') + '_' + datetime.datetime.now().strftime('%H%M') + '_' + str(duration) + 'd.csv', 'w', newline='', encoding='utf-8') as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		dict_writer.writeheader()
		dict_writer.writerows(res)
	

if __name__ == '__main__':
	booking_id_ctrip()