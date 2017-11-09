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
import random
import json
# import logging
from requests.exceptions import ConnectionError
from requests.exceptions import ChunkedEncodingError
from requests.exceptions import ReadTimeout
# from multiprocessing.dummy import Pool as ThreadPool
import multiprocessing
from xml.etree.ElementTree import ParseError

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

def asp(s_request):
	url = 'https://rbs.gta-travel.com/rbscnapi/RequestListenerServlet'
	r = None
	for i in range(MAX_RETRIES):
		try:
			r = requests.post(url, data=s_request['body'], timeout=10)
			# retry if no price found?
			# if not has_item_price(r):
			# 	print('retry.. ' + str(i))
			# 	continue
			# print('request body: ' + str(request_body[301:322]))
			# print('Posting ' + str(s_request['GTA_key']))
			print('PPID: {} PID: {} GTA_key: {}'.format(os.getppid(), os.getpid(), str(s_request['GTA_key'])) )
		except OSError:
			print('Error: ignoring OSError...' + str(i))
			continue
		except ConnectionError:
			print('Error: ignoring ConnectionError...' + str(i))
			continue
		except ChunkedEncodingError:
			print('Error: ignoring ChunkedEncodingError...' + str(i))
			continue
		except ReadTimeout:
			print('Error: ignoring ReadTimeout...' + str(i))
			continue
		else:
			break
	if r == None:
		print('Warning: Reached MAX RETRIES.. r==None.. ')

	# ent = {}
	# ent['gta_key'] = s_request['GTA_key']
	# ent['text'] = r
	# return ent
	return r

def asp_p(search_requests):
	# pool = ThreadPool(threads)
	# results = pool.map(asp, search_requests)
	# pool.close()
	# pool.join()
	PROCESSES = 4
	with multiprocessing.Pool(PROCESSES) as pool:
		results = pool.map(asp, search_requests)
	return results

# def process(responese):
# 	if response == None:
# 		return None
# 	r_tree = ET.fromstring(response.text)
# 	if r_tree.find('.//ItemPrice') == None:
# 		return None
# 	for hotel in r_tree.find('.//HotelDetails'):
# 		hotel_name = hotel.find('.//Item').text
# 		for room_cat in r_tree.find('.//RoomCategories'):
# 			print('Id: ' + str(room_cat.get('Id')))
# 			print('Des: ' + str(room_cat.find('.//Description').text))
# 			entry = dict()
# 			entry['GTA_key'] = hotel_code['city_code'] + '_' + hotel_code['item_code']
# 			entry['Hotel_Name'] = hotel_name
# 			entry['Room_Name'] = room_cat.find('.//Description').text
# 			entry['Category_id'] = room_cat.get('Id')
# 			entry['Breakfast'] = room_cat.find('.//Basis').get('Code')
# 			entry['Policy'] = ''
# 			for charge_condition in room_cat.find('.//ChargeConditions'):
# 				if charge_condition.get('Type') == 'cancellation':
# 					for conditoin in charge_condition:
# 						if conditoin.get('Charge') == 'true':
# 							entry['Policy'] += 'Charge(FromDay: ' + str(conditoin.get('FromDay')) + ' ToDay: ' + str(conditoin.get('ToDay')) + ') '
# 						else:
# 							entry['Policy'] += 'Free(FromDay: ' + str(conditoin.get('FromDay')) + ') '

# 			entry['Check_in'] = checkin_date.strftime('%Y-%m-%d')
# 			entry['Price'] = room_cat.find('.//ItemPrice').text
# 			entry['Currency'] = room_cat.find('.//ItemPrice').get('Currency')
# 			return entry
# 			# res.append(entry)

# def process_p(search_responses, threads=2):
# 	pool = ThreadPool(threads)
# 	results = pool.map(process, search_responses)
# 	pool.close()
# 	pool.join()
# 	return results

def add_empty_ent(response, checkin_date, res):
	ent = {}
	ent['GTA_key'] = response['gta_key']
	ent['Check_in'] = checkin_date.strftime('%Y-%m-%d')
	res.append(ent)

@click.command()
@click.option('--file_name', default='gta_hotel_keys')
@click.option('--checkin_d', default='2017-11-22')
# @click.option('--to_d', default='2017-11-20')
@click.option('--client', default='ctrip')
def asp_pool(file_name, checkin_d, client):
	res = []
	search_requests = []

	try:
		validate_d(checkin_d)
	except ValueError:
		print('Please input date in correct format..')
		return
	checkin_date = datetime.datetime.strptime(checkin_d, '%Y-%m-%d').date()
	print('Check in date ' + checkin_date.strftime('%Y-%m-%d'))

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
			hotel_codes.append(dict([('city_code', city_code), ('item_code', item_code)]))
			hotel_ids.add(line)

	agent_secret = None
	with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secrets.json')) as data_file:    
		agent_secret = (json.load(data_file))[client]
	search_tree = ET.parse(os.path.join(os.getcwd(), 'SearchHotelPricePaxRequest.xml'))
	search_tree.find('.//RequestorID').set('Client', agent_secret['id'])
	search_tree.find('.//RequestorID').set('EMailAddress', agent_secret['email'])
	search_tree.find('.//RequestorID').set('Password', agent_secret['password'])

	# prep search_requests
	for counter, hotel_code in enumerate(hotel_codes):
		msg = ' '.join([ 'Searching Price for',
							hotel_code['city_code'],
							hotel_code['item_code'],
							'..',
							'id:',
							str(counter)
						])
		# print(msg)

		search_tree.find('.//ItemDestination').set('DestinationCode', hotel_code['city_code'])
		search_tree.find('.//ItemCode').text = hotel_code['item_code']
		search_tree.find('.//PaxRoom').set('Adults', str(2))
		search_tree.find('.//CheckInDate').text = checkin_date.strftime('%Y-%m-%d')
		ent = {}
		ent['GTA_key'] = '_'.join([hotel_code['city_code'], hotel_code['item_code']])
		ent['body'] = ET.tostring(search_tree.getroot(), encoding='UTF-8', method='xml')
		search_requests.append(ent)

	# multi thread
	responses = asp_p(search_requests)

	# process res
	for response in responses:
		if response == None:
			continue
		try:
			r_tree = ET.fromstring(response.text)
		except ParseError:
			print('Warning: Parse error for..\n' + response.text)
			continue
		if r_tree.find('.//ItemPrice') == None:
			# add_empty_ent(response, checkin_date, res)
			continue
		for hotel in r_tree.find('.//HotelDetails'):
			hotel_name = hotel.find('.//Item').text
			gta_key = hotel.find('.//City').get('Code') + '_' + hotel.find('.//Item').get('Code')

			for room_cat in r_tree.find('.//RoomCategories'):
				# print('Id: ' + str(room_cat.get('Id')))
				# print('Des: ' + str(room_cat.find('.//Description').text))
				entry = dict()
				# entry['GTA_key'] = hotel_code['city_code'] + '_' + hotel_code['item_code']
				entry['GTA_key'] = gta_key
				
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

				entry['Check_in'] = checkin_date.strftime('%Y-%m-%d')
				entry['Price'] = room_cat.find('.//ItemPrice').text
				entry['Currency'] = room_cat.find('.//ItemPrice').get('Currency')
				res.append(entry)

	gta_keys = [ ent['GTA_key'] for ent in res ]
	# print(str(gta_keys))
	for hotel_id in hotel_ids:
		if hotel_id != '' and hotel_id not in gta_keys:
			# print(hotel_id)
			ent = {}
			ent['GTA_key'] = hotel_id.strip()
			ent['Check_in'] = checkin_date.strftime('%Y-%m-%d')
			res.append(ent)

	keys = None
	max_len = 0
	for ent in res:
		if len(ent.keys()) > max_len:
			max_len = len(ent.keys())
			keys = ent.keys()

	output_file_name = '_'.join([ 'Output_search_price',
									file_name,
									checkin_date.strftime('%y%m%d'),
									datetime.datetime.now().strftime('%H%M')
								]) + '.csv'
	# keys = res[0].keys()
	with open(output_file_name, 'w', newline='', encoding='utf-8') as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		dict_writer.writeheader()
		dict_writer.writerows(res)

if __name__ == '__main__':
	multiprocessing.freeze_support()
	asp_pool()