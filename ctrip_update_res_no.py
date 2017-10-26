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
import re

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

def isEnglish(s):
	try:
		s.encode(encoding='utf-8').decode('ascii')
	except UnicodeDecodeError:
		return False
	else:
		return True

def isGarbage(s):
	if s.lower() in ['ok', 'nono', 'ng', 'll', 'stp', 'wichuta', 'okay', 'view', 'vas', 'rt', 'kb', 'chalee', 'im', 'not available'  ]:
		return True
	return False

def hasNumbers(s):
	return any(char.isdigit() for char in s)

def hasDates(s):
	if any( month in s.lower() for month in ['jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec']):
		return True
	return False

def isValid(hc):
	for s in hc:
		# if isEnglish(s) and not isGarbage(s):
		if not isEnglish(s) or not hasNumbers(s) or hasDates(s):
			return False
	return True

REF_API = 'api'
REF_CLIENT = 'client'
REF_AGENT = 'agent'

CONFIRMED = 'Confirmed or Completed'
CANCELLED = 'Cancelled (to register)'

def is_bad_date(filename_regex, newest):
	today_date = datetime.datetime.now().strftime('%y%m%d')
	try:
		newest_date = re.search(filename_regex, newest).group(1)
	except AttributeError:
		newest_date = ''
	if newest_date != today_date:
		print('Error: newest date != today date.. mannual intervention needed..')
		return True
	print('newest date: ' + newest_date)
	return False

def is_bad_date_re(filename_regex, newest):
	today_date = datetime.datetime.now().date()
	try:
		newest_date = re.search(filename_regex, newest).group(1)
	except AttributeError:
		newest_date = ''
	try:
		newest_date = datetime.datetime.strptime(newest_date , '%y%m%d').date()
	except ValueError:
		print('Error: Unable to convert date')
		return True
	if newest_date < today_date:
		print('Error: newest date < today date.. mannual intervention needed..')
		return True
	print('newest date: ' + str(newest_date))
	return False

@click.command()
@click.option('--filename', default='output_hotel_ref_171013_1237.csv')
# @click.option('--client', default='ctrip')
# @click.option('--days', default=1, type=int)
def ctrip_update_res_no(filename):

	url = 'http://vendor.ctrip.com/Hotel/OTAReceive/HotelResNumUpdate.asmx'
	pp = pprint

	soap_wrapper_head = '<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body>'
	soap_wrapper_foot = '</soap:Body></soap:Envelope>'

	# if is_bad_date('output_hotel_ref_(\d+)', filename):
	if is_bad_date_re('output_hotel_ref_(\d+)', filename):
		print('Fatal: bad date .. no push to ctrip .. ')
		return

	bookings = []
	res = []
	# filename = 'gtaConfirmRefs_5867_2017-06-30_2017-07-07.csv'
	with open(filename, encoding='utf-8-sig') as csvfile:
		ids = set()
		reader = csv.DictReader(csvfile)
		for row in reader:
			# pp.pprint(row['hotel_id'])
			if row['gta_api_booking_id'] not in ids:
				entry = dict()
				entry['client_booking_id'] = row['client_booking_id']
				entry['agent_booking_id'] = row['agent_booking_id']
				entry['gta_api_booking_id'] = row['gta_api_booking_id']
				entry['booking_status'] = row['booking_status']
				entry['booking_creation_date'] = row['booking_creation_date']
				entry['booking_departure_date'] = row['booking_departure_date']
				entry['booking_name'] = row['booking_name']
				entry['booking_net_price'] = row['booking_net_price']
				entry['booking_currency'] = row['booking_currency']
				# confirmation_# list
				# ad-hoc bug fix
				# entry['hotel_confirmation_#'] = []
				entry['hotel_confirmation_#'] = set()
				entry['hotel_confirmation_status'] = ''
				entry['hotel_email'] = ''
				if 'hotel_email' in row:
					entry['hotel_email'] = row['hotel_email']
				if 'hotel_confirmation_#' in row:
					# entry['hotel_confirmation_#'].append(row['hotel_confirmation_#'])
					entry['hotel_confirmation_#'].add(row['hotel_confirmation_#'])
				if 'hotel_confirmation_status' in row:
					entry['hotel_confirmation_status'] = row['hotel_confirmation_status']
				# new 
				entry['Ctrip_update_API'] = ''
				# last_entry = entry
				bookings.append(entry)
			else:
				booking_entry = None
				for booking in bookings:
					if booking['gta_api_booking_id'] == row['gta_api_booking_id']:
						booking_entry = booking
				# booking_entry['hotel_confirmation_#'].append(row['hotel_confirmation_#'])
				booking_entry['hotel_confirmation_#'].add(row['hotel_confirmation_#'])

			ids.add(row['gta_api_booking_id'])

	# exclude bookings already pushed to ctrip 
	gta_api_ids_exclu = []
	try:
		output_file_name = 'output_ctrip_booking_store.csv'
		with open(output_file_name, encoding='utf-8-sig') as csvfile:
			ids = set()
			reader = csv.DictReader(csvfile)
			for row in reader:
				# pp.pprint(row['hotel_id'])
				if row['gta_api_booking_id'] not in ids:
					gta_api_ids_exclu.append(row['gta_api_booking_id'])
				ids.add(row['gta_api_booking_id'])
	except FileNotFoundError:
		print('Error: file not found.. bye.. ')
		return

	search_tree = ET.parse(os.path.join(os.getcwd(), 'CtripHotelResNumUpdateRQ.xml'))

	headers = { 'Content-Type': 'text/xml',
				'SOAPAction': '"http://www.opentravel.org/OTA/2003/05/Request"' }

	for counter, booking in enumerate(bookings):
		pp.pprint('Updating booking id to Ctrip: ' + str(counter) + ': ' + booking['gta_api_booking_id'])

		if booking['gta_api_booking_id'] in gta_api_ids_exclu:
			print('Booking has already being pushed to Ctrip API once.. ')
			continue

		if len(booking['hotel_confirmation_#']) == 0:
			print('booking confirmation # len == 0 .. skipping..')
			continue

		if any( hc == None for hc in booking['hotel_confirmation_#']) or any( hc == '' for hc in booking['hotel_confirmation_#']):
			print('No booking confirmation #.. skipping..')
			continue

		if booking['hotel_confirmation_status'] != None and booking['hotel_confirmation_status'] == CANCELLED:
			print('Booking canceled .. skipping..')
			continue

		if not isValid(list(booking['hotel_confirmation_#'])):
			print('Warning: Confirmation # not valid.. ' + str(booking['hotel_confirmation_#']))
			booking['Ctrip_update_API'] = 'not sent to ctrip'
			res.append(booking)
			continue

		for res_id in search_tree.find('.//{http://www.opentravel.org/OTA/2003/05}HotelReservationIDs'):
			if res_id.get('ResID_Type') == '501':
				# print(res_id.get('ResID_Value'))
				res_id.set('ResID_Value', booking['agent_booking_id'])
			if res_id.get('ResID_Type') == '502':
				# print(res_id.get('ResID_Value'))
				res_id.set('ResID_Value', booking['gta_api_booking_id'].replace('041/', ''))
			if res_id.get('ResID_Type') == '504':
				res_id.set('ResID_Value', ','.join(booking['hotel_confirmation_#']))
				print(res_id.get('ResID_Value'))				

		try:
			r = requests.post(url, data=ET.tostring(search_tree.getroot(), encoding='UTF-8'), headers=headers, timeout=60)
		except OSError:
			pp.pprint('Error: OSError.. Searching has stopped..')
			booking['Ctrip_update_API'] = 'Connection Error: OSError'
			res.append(booking)
			continue
		except ConnectionError as e:
			print('fatal Connection error...r')
			booking['Ctrip_update_API'] = 'Connection Error: ConnectionError'
			res.append(booking)
			continue
		except ReadTimeout as e:
			print('fatal Read timeout error...r')
			booking['Ctrip_update_API'] = 'Connection Error: ReadTimeout'
			res.append(booking)
			continue
		except ChunkedEncodingError as e:
			print('fatal Chunked encoding error...s')
			booking['Ctrip_update_API'] = 'Connection Error: ChunkedEncodingError'
			res.append(booking)
			continue

		r_tree = ET.fromstring(r.text)

		# pp.pprint('r_text: ' + r.text)
		# pp.pprint('r: ' + r)

		if r_tree == None:
			booking['Ctrip_update_API'] = 'No result from Ctrip API'
			print('Warning: No response...')
			res.append(booking)
			continue

		if r_tree.find('.//{http://www.opentravel.org/OTA/2003/05}Success') != None:
			booking['Ctrip_update_API'] = 'Success'
			print('Update success...')
		if r_tree.find('.//{http://www.opentravel.org/OTA/2003/05}Errors') != None:
			booking['Ctrip_update_API'] = r.text
			print('Update errors...')

		res.append(booking)
	# .set('Client', agent_secret['id'])
	# search_tree.find('.//RequestorID').set('EMailAddress', agent_secret['email'])
	# search_tree.find('.//RequestorID').set('Password', agent_secret['password'])

	# for counter, booking in enumerate(bookings):
	# 	pp.pprint('Searching booking id: ' + str(counter) + ': ' + booking['gta_api_booking_id'])

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
	# 		r = requests.post(url, data=ET.tostring(search_tree.getroot(), encoding='UTF-8', method='xml'), timeout=600)
	# 	except OSError:
	# 		pp.pprint('Error: OSError.. Searching has stopped..')
	# 		continue

	# 	r_tree = ET.fromstring(r.text)

	# 	items_ele = r_tree.find('.//BookingItems')
	# 	if items_ele == None:
	# 		print('Error: No BookingItems found..')
	# 		continue

	# 	for booking_item in r_tree.find('.//BookingItems'):
	# 		hotel_ref_ele = booking_item.find('.//ItemConfirmationReference')
	# 		if hotel_ref_ele != None:
	# 			booking['hotel_confirmation_#'] = hotel_ref_ele.text
	# 		entry = copy.deepcopy(booking)
	# 		res.append(entry)

	if not res:
		print('Warning: List empty..')
		return

	# keys = res[0].keys()
	keys = res[0].keys()
	# with open('output_SearchPrice_' + date.today().strftime('%Y_%m_%d') + '.csv', 'w', encoding='utf-8') as output_file:
	with open('output_ctrip_update_res_no_' + datetime.datetime.today().date().strftime('%y%m%d') + '_' + datetime.datetime.now().strftime('%H%M') + '.csv', 'w', newline='', encoding='utf-8') as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		dict_writer.writeheader()
		dict_writer.writerows(res)
	

if __name__ == '__main__':
	ctrip_update_res_no()