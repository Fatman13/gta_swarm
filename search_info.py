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

@click.command()
@click.option('--filename', default='search_item_info_keys')
@click.option('--client', default='ali')
# @click.option('--days', default=1, type=int)
def search_info(filename, client):

	url = 'https://rbs.gta-travel.com/rbscnapi/RequestListenerServlet'
	pp = pprint
	res = []

	agent_secret = None
	with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secrets.json')) as data_file:    
		agent_secret = (json.load(data_file))[client]

	# validate_d(from_d)
	# validate_d(to_d)

	# from_date = datetime.datetime.today().date() + datetime.timedelta(days=days)
	# to_date = from_date + datetime.timedelta(days=1)

	print('Search client.. ' + client)
	# print('Duration.. ' + )

	# from_date = datetime.datetime.strptime(from_d, '%Y-%m-%d').date()
	# to_date = datetime.datetime.strptime(to_d, '%Y-%m-%d').date()

	# pp.pprint('? ' + str(skip))

	hotel_codes = []
	with open(filename, 'r') as file:
		for line in file:
			# pp.pprint(line)
			try:
				city_code, item_code = line.rstrip().split('_')
			except ValueError:
				print('Warning: Invalid GTA key format..')
				continue
			hotel_codes.append(dict([('city_code', city_code), ('item_code', item_code)]))

	search_tree = ET.parse(os.path.join(os.getcwd(), 'SearchItemInformationRequest.xml'))

	for hotel_code in hotel_codes:
		pp.pprint('Searching info for ' + hotel_code['city_code'] + ' ' + hotel_code['item_code'])
		search_tree.find('.//ItemDestination').set('DestinationCode', hotel_code['city_code'])
		search_tree.find('.//ItemCode').text = hotel_code['item_code']

		try:
			r = requests.post(url, data=ET.tostring(search_tree.getroot(), encoding='UTF-8', method='xml'), timeout=600)
		except OSError:
			pp.pprint('Error: OSError.. Searching has stopped..')
			continue

		r_tree = ET.fromstring(r.text)

		entry = {}
		entry['GTA_key'] = hotel_code['city_code'] + '_' + hotel_code['item_code']
		entry['hotel_name'] = ''
		entry['hotel_email'] = ''
		name_ele = r_tree.find('.//Item')
		if name_ele != None:
			entry['hotel_name'] = r_tree.find('.//Item').text
		email_ele = r_tree.find('.//EmailAddress')
		if email_ele != None:
			entry['hotel_email'] = r_tree.find('.//EmailAddress').text
		res.append(entry)

	# keys = res[0].keys()
	keys = res[0].keys()
	# with open('output_SearchPrice_' + date.today().strftime('%Y_%m_%d') + '.csv', 'w', encoding='utf-8') as output_file:
	with open('output_SearchInfo_' + datetime.datetime.today().date().strftime('%y%m%d') + '_' + datetime.datetime.now().strftime('%H%M') + '.csv', 'w', encoding='utf-8') as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		dict_writer.writeheader()
		dict_writer.writerows(res)
	

if __name__ == '__main__':
	search_info()