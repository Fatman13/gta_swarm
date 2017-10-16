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
@click.option('--filename', default='output_ctrip_update_res_no_171013_1353.csv')
@click.option('--days', default=-30, type=int)
@click.option('--output', default='output_ctrip_booking_store.csv')
# @click.option('--client', default='ctrip')
# @click.option('--days', default=1, type=int)
def ctrip_store_booking(filename, days, output):

	# if is_bad_date('output_ctrip_update_res_no_(\d+)', filename):
	# if is_bad_date_re('output_ctrip_update_res_no_(\d+)', filename):
	# 	print('Fatal: bad date .. no store booking .. ')
	# 	return

	bookings = []
	res = []
	try:
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
					entry['hotel_confirmation_#'] = []
					entry['hotel_confirmation_status'] = ''
					entry['hotel_email'] = ''
					if 'hotel_email' in row:
						entry['hotel_email'] = row['hotel_email']
					if 'hotel_confirmation_#' in row:
						# entry['hotel_confirmation_#'].append(row['hotel_confirmation_#'])
						entry['hotel_confirmation_#'] = row['hotel_confirmation_#']
					if 'hotel_confirmation_status' in row:
						entry['hotel_confirmation_status'] = row['hotel_confirmation_status']
					bookings.append(entry)
				ids.add(row['gta_api_booking_id'])

		output_file_name = output
		with open(output_file_name, encoding='utf-8-sig') as csvfile:
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
					entry['hotel_confirmation_#'] = []
					entry['hotel_confirmation_status'] = ''
					entry['hotel_email'] = ''
					if 'hotel_email' in row:
						entry['hotel_email'] = row['hotel_email']
					if 'hotel_confirmation_#' in row:
						# entry['hotel_confirmation_#'].append(row['hotel_confirmation_#'])
						entry['hotel_confirmation_#'] = row['hotel_confirmation_#']
					if 'hotel_confirmation_status' in row:
						entry['hotel_confirmation_status'] = row['hotel_confirmation_status']
					bookings.append(entry)
				ids.add(row['gta_api_booking_id'])
	except FileNotFoundError:
		print('Error: file not found.. bye.. ')

	if not bookings:
		print('Warning: bookings empty..')
		return

	cut_off_date = datetime.datetime.today().date() + datetime.timedelta(days=days)

	ids = set()
	for counter, booking in enumerate(bookings):
		print('Booking store Ctrip: ' + str(counter) + ': ' + booking['gta_api_booking_id'])

		if datetime.datetime.strptime(booking['booking_departure_date'] , '%Y-%m-%d').date() < cut_off_date:
			continue
		if booking['gta_api_booking_id'] in ids:
			continue
		ids.add(booking['gta_api_booking_id'])
		res.append(booking)

	if not res:
		print('Warning: List empty..')
		return

	# keys = res[0].keys()
	keys = res[0].keys()
	# with open('output_SearchPrice_' + date.today().strftime('%Y_%m_%d') + '.csv', 'w', encoding='utf-8') as output_file:
	# output_file_name = '_'.join([ 'output_ctrip_booking_store',
	# 								datetime.datetime.today().date().strftime('%y%m%d'),
	# 								datetime.datetime.now().strftime('%H%M')
	# 							]) + '.csv'
	output_file_name = output
	with open(output_file_name, 'w', newline='', encoding='utf-8') as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		dict_writer.writeheader()
		dict_writer.writerows(res)

if __name__ == '__main__':
	ctrip_store_booking()