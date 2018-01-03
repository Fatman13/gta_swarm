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
			print('PPID: {} PID: {} GTA_key: {}'.format(os.getppid(), os.getpid(), str(s_request['booking_id'])) )
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
	ent['booking_id'] = s_request['booking_id']
	ent['text'] = r.text
	return ent
	# return r

def asp_p(search_requests):
	# pool = ThreadPool(threads)
	# results = pool.map(asp, search_requests)
	# pool.close()
	# pool.join()
	PROCESSES = 4
	with multiprocessing.Pool(PROCESSES) as pool:
		results = pool.map(asp, search_requests)
	return results

def add_empty_ent(response, checkin_date, res):
	ent = {}
	ent['GTA_key'] = response['gta_key']
	ent['Check_in'] = checkin_date.strftime('%Y-%m-%d')
	res.append(ent)

@click.command()
@click.option('--file_name', default='bookings')
@click.option('--client', default='dida')
def pname_pool(file_name, client):
	res = []
	search_requests = []

	booking_ids = set()
	# hotel_codes = []
	with open(file_name, 'r') as file:
		for line in file:
			booking_ids.add(line.rstrip())

	agent_secret = None
	with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secrets.json')) as data_file:    
		agent_secret = (json.load(data_file))[client]
	search_tree = ET.parse(os.path.join(os.getcwd(), 'SearchBookingItemRequest_pname.xml'))
	search_tree.find('.//RequestorID').set('Client', agent_secret['id'])
	search_tree.find('.//RequestorID').set('EMailAddress', agent_secret['email'])
	search_tree.find('.//RequestorID').set('Password', agent_secret['password'])

	# prep search_requests
	for counter, booking_id in enumerate(booking_ids):
		search_tree.find('.//BookingReference').text = booking_id
		ent = {}
		ent['booking_id'] = booking_id
		ent['body'] = ET.tostring(search_tree.getroot(), encoding='UTF-8', method='xml')
		search_requests.append(ent)

	# multi thread
	responses = asp_p(search_requests)

	# process res
	for response in responses:
		if response == None:
			continue
		try:
			r_tree = ET.fromstring(response['text'])
		except ParseError:
			print('Warning: Parse error for..\n' + response.text)
			continue
		if r_tree.find('.//PaxNames') == None:
			print('Warning: No pax name?.. skipping.. ')
			continue
		entry = {}
		entry['booking_id'] = response['booking_id']
		for counter, pax_ele in enumerate(r_tree.find('.//PaxNames')):
			entry['pax' + str(counter)] = pax_ele.text
		res.append(entry)

	output_file_name = '_'.join([ 'Output_search_pname',
									file_name,
									datetime.datetime.now().strftime('%H%M')
								]) + '.csv'
	
	keys = None
	max_len = 0
	for ent in res:
		if len(ent.keys()) > max_len:
			max_len = len(ent.keys())
			keys = ent.keys()

	# keys = res[0].keys()
	with open(output_file_name, 'w', newline='', encoding='utf-8') as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		dict_writer.writeheader()
		dict_writer.writerows(res)

if __name__ == '__main__':
	multiprocessing.freeze_support()
	pname_pool()