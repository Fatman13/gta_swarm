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
			print('PPID: {} PID: {} GTA_key: {} checkin: {}'.format(os.getppid(), os.getpid(), str(s_request['GTA_key']), s_request['checkin_date']) )
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

	ent = {}
	ent['gta_key'] = s_request['GTA_key']
	ent['rooms'] = s_request['rooms']
	ent['checkin_date'] = s_request['checkin_date']
	ent['hotel_name'] = s_request['hotel_name']
	ent['text'] = r
	return ent

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

def add_empty_ent(response, res):
	for room in response['rooms']:
		ent = {}
		ent['GTA_key'] = response['gta_key']
		ent['Hotel_Name'] = response['hotel_name']	
		ent['Room_Name'] = room
		ent['Check_in'] = response['checkin_date']
		res.append(ent)

@click.command()
@click.option('--file_name', default='tuniu_hotel_list.csv')
# @click.option('--from_d', default='2017-11-19')
# @click.option('--to_d', default='2017-11-20')
@click.option('--client', default='tuniu')
def asp_pool_w(file_name, client):
	res = []
	search_requests = []
	DAYS = 30

	# try:
	# 	validate_d(from_d)
	# 	validate_d(to_d)
	# except ValueError:
	# 	print('Please input date in correct format..')
	# 	return
	from_date = datetime.datetime.now().date() # .strptime(from_d, '%Y-%m-%d').date()
	to_date = from_date + datetime.timedelta(DAYS)
	# print('Check in date ' + checkin_date.strftime('%Y-%m-%d'))

	hotel_ids = set()
	hotel_codes = []
	with open(file_name, encoding='utf-8-sig') as csvfile:
		ids = set()
		reader = csv.DictReader(csvfile)
		for row in reader:
			if row['gta_key'] not in ids:
				ent = {}
				ent['gta_key'] = row['gta_key']
				try:
					city_code, item_code = row['gta_key'].rstrip().split('_')
				except ValueError:
					print('Warning: skipping GTA key.. ' + line.rstrip())
					continue
				ent['city_code'] = city_code
				ent['item_code'] = item_code
				ent['hotel_name'] = row['hotel_name']
				ent['rooms'] = []
				ent['rooms'].append(row['room_type'])
				hotel_codes.append(ent)
			else:
				for ent in hotel_codes:
					if ent['gta_key'] == row['gta_key']:
						ent['rooms'].append(row['room_type'])
						break
			ids.add(row['gta_key'])

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
		# DateFormatResponse="true"
		search_tree.find('.//IncludeChargeConditions').set('DateFormatResponse', 'true')
		for single_date in daterange(from_date, to_date):
			search_tree.find('.//CheckInDate').text = single_date.strftime('%Y-%m-%d')
			ent = {}
			# ent['GTA_key'] = '_'.join([hotel_code['city_code'], hotel_code['item_code']])
			ent['GTA_key'] = hotel_code['gta_key']
			ent['checkin_date'] = single_date.strftime('%Y-%m-%d')
			ent['rooms'] = hotel_code['rooms']
			ent['hotel_name'] = hotel_code['hotel_name']
			ent['body'] = ET.tostring(search_tree.getroot(), encoding='UTF-8', method='xml')
			search_requests.append(ent)

	# multi thread
	responses = asp_p(search_requests)

	# process res
	for response in responses:
		if response['text'] == None:
			add_empty_ent(response, res)
			continue
		try:
			r_tree = ET.fromstring(response['text'].text)
		except ParseError:
			add_empty_ent(response, res)
			print('Warning: Parse error for..\n' + response.text)
			continue
		if r_tree.find('.//ItemPrice') == None:
			add_empty_ent(response, res)
			# print('Warning: No item price..')
			continue
		for hotel in r_tree.find('.//HotelDetails'):
			hotel_name = hotel.find('.//Item').text
			# gta_key = hotel.find('.//City').get('Code') + '_' + hotel.find('.//Item').get('Code')
			gta_key = response['gta_key']

			for room_cat in r_tree.find('.//RoomCategories'):
				# print('Id: ' + str(room_cat.get('Id')))
				# print('Des: ' + str(room_cat.find('.//Description').text))
				entry = dict()
				# entry['GTA_key'] = hotel_code['city_code'] + '_' + hotel_code['item_code']
				entry['GTA_key'] = gta_key
				
				entry['Hotel_Name'] = hotel_name
				entry['Room_Name'] = room_cat.find('.//Description').text
				if entry['Room_Name'] not in response['rooms']:
					continue
				entry['Category_id'] = room_cat.get('Id')
				# entry['Breakfast'] = room_cat.find('.//Basis').get('Code')
				# entry['Policy'] = ''
				# for charge_condition in room_cat.find('.//ChargeConditions'):
				# 	if charge_condition.get('Type') == 'cancellation':
				# 		for conditoin in charge_condition:
				# 			if conditoin.get('Charge') == 'true':
				# 				entry['Check_in'] = str(conditoin.get('FromDate'))
				# 				break
				# 		break

				# entry['Check_in'] = checkin_date.strftime('%Y-%m-%d')
				entry['Check_in'] = response['checkin_date']
				entry['Price'] = room_cat.find('.//ItemPrice').text
				entry['Currency'] = room_cat.find('.//ItemPrice').get('Currency')
				res.append(entry)

	# gta_keys = [ ent['GTA_key'] for ent in res ]
	# for hotel_id in hotel_ids:
	# 	if hotel_id not in get_keys:
	# 		ent = {}
	# 		ent['GTA_key'] = hotel_id
	# 		res.append(ent)

	keys = None
	max_len = 0
	for ent in res:
		if len(ent.keys()) > max_len:
			max_len = len(ent.keys())
			keys = ent.keys()

	output_file_name = '_'.join([ 'Output_search_price_w',
									datetime.datetime.now().strftime('%y%m%d'),
									datetime.datetime.now().strftime('%H%M')
								]) + '.csv'
	# keys = res[0].keys()
	with open(output_file_name, 'w', newline='', encoding='utf-8') as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		dict_writer.writeheader()
		dict_writer.writerows(res)

if __name__ == '__main__':
	multiprocessing.freeze_support()
	asp_pool_w()