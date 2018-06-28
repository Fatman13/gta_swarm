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
import json
import copy
# import os
# import json
# import logging
from xml.etree.ElementTree import ParseError

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

CONFIRMED = 'Confirmed or Completed'

bad_hotels = [{"city_code": "SHEN", "item_code": "ASC"}, 
				{"city_code": "CHEG", "item_code": "HOW"},
				{"city_code": "WUH", "item_code": "CIT"},
				{"city_code": "CKG", "item_code": "94"}
				]

def is_bad_hotel(city_code, item_code):
	for bad_hotel in bad_hotels:
		if bad_hotel['city_code'] == city_code and bad_hotel['item_code'] == item_code:
			return True
	return False

def find_chain(hotel_chain, supplier_id, res):
	for ent in res:
		if ent['hotel_chain_name'] == hotel_chain and ent['supplier_id'] == supplier_id:
			return ent
	return None

# "Start Hour";
# "Start Timestamp";
# "Start Day";
# "Server Name";
# "Request: Client";
# "Request: Client Account ID";
# "Request: Client Account Name";
# "Request: Client Main Account ID";
# "Request: Client Main Account Name";
# "Request: Contract Supplier ID";
# "Request: Contract Supplier Name";
# "Request: Contract Supplier Rate";
# "Request: Contract Name";
# "Response: Hotel Supplier Brand";
# "Request: Check In Date";
# "Request: Check Out Date";
# "Request: Hotel Code";
# "Request: Hotel Name";
# "Request: Hotel Chain Name";
# "Request: Hotel Region";
# "Request: Occupancy";
# "Request: Room Type Code";
# "Request: Board Type Code";
# "Request: Lead Time Days";
# "Response: Error Message";
# "Response: Error Detailed Message";
# "Component Downloads (hits)";
# "Price Difference (Increase > 2%) (hits)";
# "Price Difference (Decrease < -2%) (hits)";
# "No Price Difference (hits)";
# "Errors (hits)";
# "SI Error: Hotel Not Available (hits)";
# "SI Error: External Error (hits)";
# "SI Error: Request Restricted (hits)";
# "Error: Allotment (hits)";
# "Error: Client Originated (hits)";
# "Error: OTHER / SYSTEM (hits)";
# "Error: Duplicated Error (APITUDE Only) (hits)"

@click.command()
@click.option('--filename', default='CTRIP---API-Errors---API-valuation-step-issues--h-_v205111_s2608_2018-06-23-00-00.csv')
# @click.option('--client', default='ctrip')
# @click.option('--days', default=1, type=int)
def hb_er(filename):

	# url = 'https://rbs.gta-travel.com/rbscnapi/RequestListenerServlet'
	# pp = pprint

	# # agent_secret = None
	# # with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secrets.json')) as data_file:    
	# # 	agent_secret = (json.load(data_file))[client]

	# agent_secret = None
	# with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secrets.json')) as data_file:    
	# 	agent_secret = json.load(data_file)

	# print('Search client.. ' + client)

	err_records = []
	with open(filename, encoding='utf-8-sig') as csvfile:
		ids = set()
		reader = csv.DictReader(csvfile, delimiter=';')
		for row in reader:
			# if row['gta_api_booking_id'] not in ids:
			# 	bookings_c.append(row['gta_api_booking_id'])
			# ids.add(row['gta_api_booking_id'])
			err_records.append(row)

	res = []
	for record in err_records:
		ent = find_chain(record['Request: Hotel Chain Name'], record['Request: Contract Supplier ID'], res)
		if ent == None:
			ent = {}
			ent['timestamp'] = record['Start Timestamp']
			ent['hotel_chain_name'] = record['Request: Hotel Chain Name']
			ent['supplier_id'] = record['Request: Contract Supplier ID']
			ent['supplier_name'] = record['Request: Contract Supplier Name']
			# Request: Contract Supplier Name
			ent['client_id'] = record['Request: Client Account ID']
			ent['client_name'] = record['Request: Client Account Name']
			ent['server_name'] = record['Server Name']

			try:
				ent['hits'] = int(record['Component Downloads (hits)'])
			except ValueError:
				ent['hits'] = 0
			try:
				ent['price_diff_>2%'] = int(record['Price Difference (Increase > 2%) (hits)'])
			except ValueError:
				ent['price_diff_>2%'] = 0
			try:
				ent['price_diff_<2%'] = int(record['Price Difference (Decrease < -2%) (hits)'])
			except ValueError:
				ent['price_diff_<2%'] = 0
			try:	
				ent['no_price_diff'] = int(record['No Price Difference (hits)'])
			except ValueError:
				ent['no_price_diff'] = 0
			try:
				ent['error_hits'] = int(record['Errors (hits)'])
			except ValueError:
				ent['error_hits'] = 0
			# except ValueError:
			# 	print('Value error : ' + \
			# 		str(record['Component Downloads (hits)']) + \
			# 		str(record['Price Difference (Increase > 2%) (hits)']) + \
			# 		str(record['Price Difference (Decrease < -2%) (hits)']) + \
			# 		str(record['No Price Difference (hits)']) + \
			# 		str(record['Errors (hits)'])
			# 		)	
			
			# float('{0:.3f}'.format(float( (l2b - last_l2b) / last_l2b )))

			res.append(ent)
			continue
		try: 
			ent['hits'] = ent['hits'] + int(record['Component Downloads (hits)'])
		except ValueError:
			pass
		try:
			ent['price_diff_>2%'] = ent['price_diff_>2%'] + int(record['Price Difference (Increase > 2%) (hits)'])
		except ValueError:
			pass

		try:
			ent['price_diff_<2%'] = ent['price_diff_<2%'] + int(record['Price Difference (Decrease < -2%) (hits)'])
		except ValueError:
			pass
		try:
			ent['no_price_diff'] = ent['no_price_diff'] + int(record['No Price Difference (hits)'])
		except ValueError:
			pass
		try:
			ent['error_hits'] = ent['error_hits'] + int(record['Errors (hits)'])
		except ValueError:
			pass


	for ent in res:
		ent['success_ratio'] = float('{0:.3f}'.format(float( ent['no_price_diff'] / ent['hits'] )))
		ent['recommend_offline'] = 'no'
		if ent['success_ratio'] < 0.5:
			ent['recommend_offline'] = 'yes'


	output_file_name = '_'.join(['output_hb_pa_stats',
									datetime.datetime.today().date().strftime('%y%m%d'),
									datetime.datetime.now().strftime('%H%M'),
									'.csv'])

	keys = res[0].keys()
	# with open('output_SearchPrice_' + date.today().strftime('%Y_%m_%d') + '.csv', 'w', encoding='utf-8') as output_file:
	# with open('output_Search_item_hr_' + datetime.datetime.today().date().strftime('%y%m%d') + '_' + datetime.datetime.now().strftime('%H%M') + '.csv', 'w', newline='', encoding='utf-8') as output_file:
	with open(output_file_name, 'w', newline='', encoding='utf-8') as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		dict_writer.writeheader()
		dict_writer.writerows(res)

	# print(str(err_records[100]))
	# print(str(err_records[100]['Component Downloads (hits)']))

	# bookings = []
	# res = []
	# # filename = 'gtaConfirmRefs_5867_2017-06-30_2017-07-07.csv'
	# with open(filename, encoding='utf-8-sig') as csvfile:
	# 	ids = set()
	# 	reader = csv.DictReader(csvfile)
	# 	for row in reader:
	# 		# pp.pprint(row['hotel_id'])
	# 		if row['gta_api_booking_id'] not in ids:
	# 			entry = dict()
	# 			entry['client_booking_id'] = row['client_booking_id']
	# 			entry['agent_booking_id'] = row['agent_booking_id']
	# 			entry['gta_api_booking_id'] = row['gta_api_booking_id']
	# 			entry['booking_status'] = row['booking_status']
	# 			entry['booking_creation_date'] = row['booking_creation_date']
	# 			entry['booking_departure_date'] = row['booking_departure_date']
	# 			entry['booking_name'] = row['booking_name']
	# 			entry['booking_net_price'] = row['booking_net_price']
	# 			entry['booking_currency'] = row['booking_currency']
	# 			entry['hotel_confirmation_#'] = ''
	# 			entry['hotel_confirmation_status'] = ''
	# 			entry['client_name'] = ''
	# 			if 'hotel_confirmation_#' in row:
	# 				entry['hotel_confirmation_#'] = row['hotel_confirmation_#']
	# 			if 'hotel_confirmation_status' in row:
	# 				entry['hotel_confirmation_status'] = row['hotel_confirmation_status']
	# 			if 'client_name' in row:
	# 				entry['client_name'] = row['client_name']
	# 			bookings.append(entry)
	# 		ids.add(row['gta_api_booking_id'])

	# search_tree = ET.parse(os.path.join(os.getcwd(), 'SearchBookingItemRequest.xml'))

	# for counter, booking in enumerate(bookings):
	# 	pp.pprint('Searching booking id: ' + str(counter) + ': ' + booking['gta_api_booking_id'])

	# 	if booking['gta_api_booking_id'] in bookings_c:
	# 		print('Warning: already pushed to Ctrip.. skip..')
	# 		continue

	# 	if 'client_name' not in booking.keys():
	# 		print('Error: No client name...')
	# 		continue

	# 	search_tree.find('.//RequestorID').set('Client', agent_secret[booking['client_name']]['id'])
	# 	search_tree.find('.//RequestorID').set('EMailAddress', agent_secret[booking['client_name']]['email'])
	# 	search_tree.find('.//RequestorID').set('Password', agent_secret[booking['client_name']]['password'])

	# 	if not booking['hotel_confirmation_#'] and booking['hotel_confirmation_#'] != '':
	# 		print('have hotel confirmation # already.. skipping')
	# 		entry = copy.deepcopy(booking)
	# 		res.append(entry)
	# 		continue
	# 	if not booking['hotel_confirmation_status'] and booking['hotel_confirmation_status'] != '':
	# 		print('status updated already.. skipping')
	# 		entry = copy.deepcopy(booking)
	# 		res.append(entry)
	# 		continue	

	# 	if CONFIRMED not in booking['booking_status']:
	# 		print('Booking not confirmed.. skipping..')
	# 		continue
	# 	# search_tree.find('.//ItemDestination').set('DestinationCode', hotel_code['city_code'])
	# 	# search_tree.find('.//ItemCode').text = hotel_code['item_code']
	# 	booking_id = booking['gta_api_booking_id'].replace('041/', '')
	# 	for search_request in search_tree.find('.//RequestDetails'):
	# 		search_request.find('.//BookingReference').text = booking_id

	# 	try:
	# 		r = requests.post(url, data=ET.tostring(search_tree.getroot(), encoding='UTF-8', method='xml'), timeout=10)
	# 	except OSError:
	# 		pp.pprint('Error: OSError.. Searching has stopped..')
	# 		continue

	# 	try:
	# 		r_tree = ET.fromstring(r.text)
	# 	except ParseError:
	# 		print('Error: parsing error.. skip.. 1')
	# 		continue

	# 	items_ele = r_tree.find('.//BookingItems')
	# 	if items_ele == None:
	# 		print('Error: No BookingItems found..')
	# 		continue

	# 	# for booking_item in r_tree.find('.//BookingItems'):
	# 	for response in r_tree.find('.//ResponseDetails'):
	# 		# print(booking_item.text)

	# 		hotel_ref_ele = response.find('.//ItemConfirmationReference')
	# 		if hotel_ref_ele != None:
	# 			booking['hotel_confirmation_#'] = hotel_ref_ele.text
	# 		else:
	# 			continue

	# 		# logic to exclude bad hotels
	# 		city_ele = response.find('.//ItemCity')
	# 		item_ele = response.find('.//Item')
	# 		if city_ele != None and items_ele != None:
	# 			city_code = city_ele.get('Code')
	# 			item_code = item_ele.get('Code')
				
	# 			if is_bad_hotel(city_code, item_code):
	# 				print('Warning: bad hotel.. skipping.. ')
	# 				continue

	# 		entry = copy.deepcopy(booking)
	# 		res.append(entry)

	# # keys = res[0].keys()
	# keys = res[0].keys()
	# # with open('output_SearchPrice_' + date.today().strftime('%Y_%m_%d') + '.csv', 'w', encoding='utf-8') as output_file:
	# with open('output_Search_item_hr_' + datetime.datetime.today().date().strftime('%y%m%d') + '_' + datetime.datetime.now().strftime('%H%M') + '.csv', 'w', newline='', encoding='utf-8') as output_file:
	# 	dict_writer = csv.DictWriter(output_file, keys)
	# 	dict_writer.writeheader()
	# 	dict_writer.writerows(res)
	

if __name__ == '__main__':
	hb_er()