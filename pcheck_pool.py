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
			print('asp PPID: {} PID: {} GTA_key: {}'.format(os.getppid(), os.getpid(), str(s_request['gta_code'])) )
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
	ent['gta_code'] = s_request['gta_code']
	ent['city_code'] = s_request['city_code']
	ent['item_code'] = s_request['item_code']
	ent['body'] = s_request['body']
	if r != None:
		ent['text'] = r.text
	return ent

def aspp(s_request):
	url = 'https://rbs.gta-travel.com/rbscnapi/RequestListenerServlet'
	r = None
	for i in range(MAX_RETRIES):
		try:
			r = requests.post(url, data=s_request['body'], timeout=10)
			print('aspp PPID: {} PID: {} GTA_key: {}'.format(os.getppid(), os.getpid(), str(s_request['gta_code'])) )
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
	ent['gta_code'] = s_request['gta_code']
	ent['city_code'] = s_request['city_code']
	ent['item_code'] = s_request['item_code']
	ent['room_id'] = s_request['room_id']
	ent['price'] = s_request['price']
	ent['f_body'] = s_request['body']
	ent['xml_req'] = s_request['xml_req']
	ent['xml_res'] = s_request['xml_res']
	ent['timestamp'] = datetime.datetime.utcnow()
	ent['text'] = None
	if r != None:
		ent['text'] = r.text
		# print('Warning: Reached MAX RETRIES.. r==None.. ')
	return ent

def asp_p(func, search_requests):
	# pool = ThreadPool(threads)
	# results = pool.map(asp, search_requests)
	# pool.close()
	# pool.join()
	PROCESSES = 4
	with multiprocessing.Pool(PROCESSES) as pool:
		results = pool.map(func, search_requests)
	return results

def add_empty_ent(response, checkin_date, res):
	ent = {}
	ent['GTA_key'] = response['gta_key']
	ent['Check_in'] = checkin_date.strftime('%Y-%m-%d')
	res.append(ent)

@click.command()
@click.option('--file_name', default='f_p_a_c_cmd')
@click.option('--client', default='lefei')
@click.option('--days', default=20, type=int)
def pcheck_pool(file_name, client, days):
	res = []
	f_res = []
	search_requests = []
	f_search_requests = []

	excel_cell_char_limit = 32000

	checkin_date = datetime.datetime.now().date() + datetime.timedelta(days=days)

	hotel_ids = set()
	hotel_codes = []
	with open(file_name, 'r') as file:
		for line in file:
			if line in hotel_ids:
				continue			
			try:
				gta_code = line.rstrip()
				city_code, item_code = line.rstrip().split('_')
			except ValueError:
				print('Warning: skipping invalid key.. ' + line.rstrip())
				continue
			hotel_codes.append(dict([('city_code', city_code), ('item_code', item_code), ('gta_code', gta_code)]))
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
		# search_tree.find('.//BookingReference').text = booking_id
		search_tree.find('.//ItemDestination').set('DestinationCode', hotel_code['city_code'])
		search_tree.find('.//ItemCode').text = hotel_code['item_code']
		search_tree.find('.//PaxRoom').set('Adults', str(2))
		search_tree.find('.//CheckInDate').text = checkin_date.strftime('%Y-%m-%d')
		ent = {}
		ent['gta_code'] = hotel_code['gta_code']
		ent['city_code'] = hotel_code['city_code']
		ent['item_code'] = hotel_code['item_code']
		ent['body'] = ET.tostring(search_tree.getroot(), encoding='UTF-8', method='xml')
		search_requests.append(ent)

	# multi thread
	responses = asp_p(asp, search_requests)

	# process res
	for response in responses:
		if response == None:
			entry = {}
			entry['gta_code'] = response['gta_code']
			entry['xml_req'] = response['body']#.replace(',', ' ')
			entry['xml_res'] = None
			res.append(entry)
			continue
		try:
			r_tree = ET.fromstring(response['text'])
		except ParseError:
			print('Warning: Parse error for..\n' + response.text)
			continue
		if r_tree.find('.//RoomCategories') == None or len(r_tree.find('.//RoomCategories')) == 0:
			entry = {}
			entry['gta_code'] = response['gta_code']
			entry['xml_req'] = response['body']#.replace(',', ' ')
			entry['xml_res'] = response['text'].replace(',', ' ')[:excel_cell_char_limit]
			res.append(entry)
			continue
		# entry['booking_id'] = response['booking_id']
		for counter, room_ele in enumerate(r_tree.find('.//RoomCategories')):
			entry = {}
			entry['gta_code'] = response['gta_code']
			entry['city_code'] = response['city_code']
			entry['item_code'] = response['item_code']			
			entry['room_id'] = room_ele.get('Id')
			entry['price'] = room_ele.find('.//ItemPrice').text
			entry['checkin'] = checkin_date.strftime('%Y-%m-%d')
			entry['xml_req'] = response['body']#.replace(',', ' ')
			entry['xml_res'] = response['text'].replace(',', ' ')[:excel_cell_char_limit]
			res.append(entry)

	for entry in res:
		if 'room_id' not in entry.keys():
			ent = {}
			ent['client'] = client
			ent['client_id'] = agent_secret['id']
			ent['gta_code'] = entry['gta_code']
			ent['checkin'] = checkin_date.strftime('%Y-%m-%d')
			f_res.append(ent)
			continue
		search_tree.find('.//ItemDestination').set('DestinationCode', entry['city_code'])
		search_tree.find('.//ItemCode').text = entry['item_code']
		# search_tree.find('.//PaxRoom').set('Adults', str(2))
		search_tree.find('.//CheckInDate').text = entry['checkin']
		search_tree.find('.//PaxRoom').set('Id', entry['room_id'])
		ent = {}
		ent['gta_code'] = entry['gta_code']
		ent['city_code'] = entry['city_code']
		ent['item_code'] = entry['item_code']
		ent['room_id'] = entry['room_id']
		ent['price'] = entry['price']
		ent['xml_req'] = entry['xml_req']
		ent['xml_res'] = entry['xml_res']
		ent['body'] = ET.tostring(search_tree.getroot(), encoding='UTF-8', method='xml')
		f_search_requests.append(ent)

	# multi thread
	f_responses = asp_p(aspp, f_search_requests)

	for response in f_responses:
		if response == None or response['text'] == None:
			entry = {}
			entry['client'] = client
			entry['client_id'] = agent_secret['id']
			entry['gta_code'] = response['gta_code']
			entry['room_id'] = response['room_id']
			entry['s_price'] = response['price']
			entry['checkin'] = checkin_date.strftime('%Y-%m-%d')
			entry['timestamp'] = response['timestamp']			
			entry['xml_req'] = response['xml_req']
			entry['xml_res'] = response['xml_res']
			entry['f_xml_req'] = response['f_body']
			entry['f_xml_res'] = response['text'].replace(',', ' ')[:excel_cell_char_limit]
			f_res.append(entry)
			continue
		try:
			r_tree = ET.fromstring(response['text'])
		except ParseError:
			print('Warning: Parse error for..\n' + response.text)
			continue
		if r_tree.find('.//ItemPrice') == None:
			entry = {}
			entry['client'] = client
			entry['client_id'] = agent_secret['id']
			entry['gta_code'] = response['gta_code']
			entry['room_id'] = response['room_id']
			entry['s_price'] = response['price']
			entry['checkin'] = checkin_date.strftime('%Y-%m-%d')
			entry['timestamp'] = response['timestamp']			

			entry['xml_req'] = response['xml_req']
			entry['xml_res'] = response['xml_res']
			entry['f_xml_req'] = response['f_body']
			entry['f_xml_res'] = response['text'].replace(',', ' ')[:excel_cell_char_limit]
			f_res.append(entry)
			continue
		# entry['booking_id'] = response['booking_id']
		for counter, room_ele in enumerate(r_tree.find('.//RoomCategories')):
			entry = {}
			entry['client'] = client
			entry['client_id'] = agent_secret['id']
			entry['gta_code'] = response['gta_code']
			entry['city_code'] = response['city_code']
			entry['item_code'] = response['item_code']			
			entry['room_id'] = response['room_id']
			entry['s_price'] = response['price']
			entry['f_price'] = room_ele.find('.//ItemPrice').text
			entry['checkin'] = checkin_date.strftime('%Y-%m-%d')
			entry['timestamp'] = response['timestamp']			

			entry['xml_req'] = response['xml_req']
			entry['xml_res'] = response['xml_res']
			entry['f_xml_req'] = response['f_body']
			entry['f_xml_res'] = response['text'].replace(',', ' ')[:excel_cell_char_limit]
			# entry['xml'] = response['text']
			f_res.append(entry)

	# for ent in f_res:

	output_file_name = '_'.join([ 'Output_final_price_check',
									file_name,
									datetime.datetime.now().strftime('%y%m%d_%H%M')
								]) + '.csv'
	
	keys = None
	max_len = 0
	for ent in f_res:
		if len(ent.keys()) > max_len:
			max_len = len(ent.keys())
			keys = ent.keys()

	# keys = res[0].keys()
	with open(output_file_name, 'w', newline='', encoding='utf-8') as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		dict_writer.writeheader()
		dict_writer.writerows(f_res)

if __name__ == '__main__':
	multiprocessing.freeze_support()
	pcheck_pool()