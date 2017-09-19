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
# import logging
from requests.exceptions import ConnectionError
from requests.exceptions import ChunkedEncodingError
from requests.exceptions import ReadTimeout

def validate_d(date_text):
	try:
		datetime.datetime.strptime(date_text, '%Y-%m-%d')
	except ValueError:
		raise ValueError("Incorrect data format, should be YYYY-MM-DD")

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)

MAX_RETRIES = 2

def has_item_price(r):
	r_tree = ET.fromstring(r.text)
	if r_tree.find('.//ItemPrice') == None:
		return False
	return True

@click.command()
@click.option('--file_name', default='gta_hotel_keys')
@click.option('--from_d', default='2017-09-28')
@click.option('--to_d', default='2017-09-29')
@click.option('--client', default='ctrip')
def asp(file_name, from_d, to_d, client):

	url = 'https://rbs.gta-travel.com/rbscnapi/RequestListenerServlet'
	pp = pprint
	res = []

	validate_d(from_d)
	validate_d(to_d)

	from_date = datetime.datetime.strptime(from_d, '%Y-%m-%d').date()
	to_date = datetime.datetime.strptime(to_d, '%Y-%m-%d').date()

	# pp.pprint('? ' + str(skip))

	hotel_ids = set()
	hotel_codes = []
	with open(file_name, 'r') as file:
		for line in file:
			# pp.pprint(line)
			if line in hotel_ids:
				continue			
			try:
				city_code, item_code = line.rstrip().split('_')
			except ValueError:
				print('Warning: skipping GTA key.. ' + line.rstrip())
				continue
			hotel_codes.append(dict([('city_code', city_code), ('item_code', item_code), ('missing_price', [])]))
			hotel_ids.add(line)

	agent_secret = None
	with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secrets.json')) as data_file:    
		agent_secret = (json.load(data_file))[client]

	search_tree = ET.parse(os.path.join(os.getcwd(), 'SearchHotelPricePaxRequest.xml'))
	search_tree.find('.//RequestorID').set('Client', agent_secret['id'])
	search_tree.find('.//RequestorID').set('EMailAddress', agent_secret['email'])
	search_tree.find('.//RequestorID').set('Password', agent_secret['password'])

	for hotel_code in hotel_codes:
		pp.pprint('Searching Price for ' + hotel_code['city_code'] + ' ' + hotel_code['item_code'])
		search_tree.find('.//ItemDestination').set('DestinationCode', hotel_code['city_code'])
		search_tree.find('.//ItemCode').text = hotel_code['item_code']
		search_tree.find('.//PaxRoom').set('Adults', str(2))

		# entry = dict()
		# entry['Hotel_Code'] = hotel_code['city_code'] + '_' + hotel_code['item_code']

		for single_date in daterange(from_date, to_date):
			search_tree.find('.//CheckInDate').text = single_date.strftime('%Y-%m-%d')
			pp.pprint('Check in date: ' + single_date.strftime('%Y-%m-%d'))
			# pp.pprint('num of days: ' + str(num_days))

			# pprint.pprint(ET.tostring(search_tree.getroot(), encoding='UTF-8', method='xml'))

			r = None
			# r_tree = None
			for i in range(MAX_RETRIES):
				try:
					r = requests.post(url, data=ET.tostring(search_tree.getroot(), encoding='UTF-8', method='xml'), timeout=10)
					# retry if no price found?
					if not has_item_price(r):
						print('retry.. ' + str(i))
						continue
				except OSError:
					pp.pprint('Error: ignoring OSError...' + str(i))
					continue
				except ConnectionError:
					pp.pprint('Error: ignoring ConnectionError...' + str(i))
					continue
				except ChunkedEncodingError:
					pp.pprint('Error: ignoring ChunkedEncodingError...' + str(i))
					continue
				except ReadTimeout:
					pp.pprint('Error: ignoring ReadTimeout...' + str(i))
					continue
				else:
					break

			if r == None:
				print('Warning: Reached MAX RETRIES.. still no good.. ')
				continue
			# pprint.pprint(r.text)

			# pprint.pprint(r_tree.getroot())
		
			if not has_item_price(r):
				# hotel_code['missing_price'].append('Pax ' + str(i + 1) + ': ' + single_date.strftime("%Y-%m-%d"))
				pp.pprint('Warning: Price not returned... ')
				# entry['Price'] = 'NULL'
				entry = dict()
				entry['GTA_key'] = hotel_code['city_code'] + '_' + hotel_code['item_code']
				res.append(entry)
			else:
				# pp.pprint('Gross: ' + str(r_tree.find('.//RoomPrice').get('Gross')))
				r_tree = ET.fromstring(r.text)

				for hotel in r_tree.find('.//HotelDetails'):
					hotel_name = hotel.find('.//Item').text
					for room_cat in r_tree.find('.//RoomCategories'):
						pp.pprint('Id: ' + str(room_cat.get('Id')))
						pp.pprint('Des: ' + str(room_cat.find('.//Description').text))
						entry = dict()
						entry['GTA_key'] = hotel_code['city_code'] + '_' + hotel_code['item_code']
						entry['Hotel_Name'] = hotel_name
						entry['Room_Name'] = room_cat.find('.//Description').text
						entry['Category_id'] = room_cat.get('Id')
						entry['Breakfast'] = room_cat.find('.//Basis').get('Code')
						entry['Policy'] = ''
						for charge_condition in room_cat.find('.//ChargeConditions'):
							if charge_condition.get('Type') == 'cancellation':
								for conditoin in charge_condition:
									if conditoin.get('Charge') == 'true':
										entry['Policy'] += 'Charge(FromDay: ' + str(conditoin.get('FromDay')) + ' ToDay: ' + str(conditoin.get('ToDay')) + ') '
									else:
										entry['Policy'] += 'Free(FromDay: ' + str(conditoin.get('FromDay')) + ') '


						entry['Check_in'] = single_date.strftime('%Y-%m-%d')
						entry['Price'] = room_cat.find('.//ItemPrice').text
						entry['Currency'] = room_cat.find('.//ItemPrice').get('Currency')
						res.append(entry)	
		# res.append(entry)

	keys = None
	max_len = 0
	for ent in res:
		if len(ent.keys()) > max_len:
			max_len = len(ent.keys())
			keys = ent.keys()

	output_file_name = '_'.join([ 'Output_search_price',
									file_name,
									from_date.strftime('%y%m%d'),
									datetime.datetime.now().strftime('%H%M')
								]) + '.csv'

	# keys = res[0].keys()
	# with open('output_SearchPrice_' + date.today().strftime('%Y_%m_%d') + '.csv', 'w', encoding='utf-8') as output_file:
	with open(output_file_name, 'w', newline='', encoding='utf-8') as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		dict_writer.writeheader()
		dict_writer.writerows(res)

if __name__ == '__main__':
	asp()