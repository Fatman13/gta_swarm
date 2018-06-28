#!/usr/bin/env python
# coding=utf-8

import pprint
import csv
# import openpyxl
from openpyxl import Workbook
from openpyxl import load_workbook
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
from json import JSONDecodeError

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
# @click.option('--days', default=0, type=int)
# @click.option('--duration', default=0, type=int)
@click.option('--hb_pa_file', default='HB二次可订失败20180625.xlsx')
# @click.option('--d_type', default=TYPE_DEPARTURE)
# def pa_hb(days, duration, d_type):
def pa_hb(hb_pa_file):

	# wb2 = load_workbook('test.xlsx')
	try:
		wb = load_workbook(hb_pa_file)
	except FileNotFoundError:
		print('File not found.. Specify file in --hb_pa_file option')
		return

	ws = wb.active
	errors = []
	for i, t in enumerate(tuple(ws.rows)):
		if i == 0:
			continue
		print('i: ' + str(i))
		print(t[0].value)
		if t[0].value == None or t[1].value == None:
			continue

		try:
			t0 = json.loads(t[0].value)
		except JSONDecodeError:
			print('tuple 0.. json load error..')
			continue
		try:
			t1 = json.loads(t[1].value)
		except JSONDecodeError:
			print('tuple 1.. json load error..')
			continue

		ent = {}
		ent['req'] = t0
		ent['res'] = t1
		errors.append(ent)

	err_hotels = []
	err_res = []

	for ent in errors:
		if 'hotel' not in ent['res'].keys():
			continue
		if ent['res']['hotel']['name'] not in err_hotels:
			err_hotels.append(ent['res']['hotel']['name'])
			err_ent = {}
			err_ent['hotel'] = ent['res']['hotel']['name']
			err_ent['code'] = ent['res']['hotel']['code']
			err_ent['count'] = 1
			err_ent['rps'] = set()
			for rp in ent['req']['rooms']:
				err_ent['rps'].add(rp['rateKey'])			
			err_ent['parsed_from'] = hb_pa_file
			err_res.append(err_ent)
		else:
			for err_ent in err_res:
				if ent['res']['hotel']['name'] == err_ent['hotel']:
					err_ent['count'] = err_ent['count'] + 1
					for rp in ent['req']['rooms']:
						err_ent['rps'].add(rp['rateKey'])

	for err_ent in err_res:
		err_ent['rps'] = ', '.join([ val for val in err_ent['rps']])

	output_filename = '_'.join(['output_pa_hb', datetime.datetime.now().strftime('%y%m%d'), 
									datetime.datetime.now().strftime('%H%M'), '.csv'])

	keys = err_res[0].keys()
	with open(output_filename, 'w', newline='', encoding='utf-8') as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		dict_writer.writeheader()
		dict_writer.writerows(err_res)

	# url = 'https://rbs.gta-travel.com/rbscnapi/RequestListenerServlet'
	# pp = pprint
	# res = []
	# clients = ['ctrip', 'ctrip_di', 'ctrip_dd']

	# # validate_d(from_d)
	# # validate_d(to_d)

	# from_date = datetime.datetime.today().date() + datetime.timedelta(days=days)
	# to_date = from_date + datetime.timedelta(days=duration)

	# print('Search booking.. ' + from_date.strftime('%Y-%m-%d'))
	# # print('Duration.. ' + )

	# # from_date = datetime.datetime.strptime(from_d, '%Y-%m-%d').date()
	# # to_date = datetime.datetime.strptime(to_d, '%Y-%m-%d').date()

	# # pp.pprint('? ' + str(skip))

	# # hotel_codes = []
	# # with open(file_name, 'r') as file:
	# # 	for line in file:
	# # 		# pp.pprint(line)
	# # 		city_code, item_code = line.rstrip().split('_')
	# # 		hotel_codes.append(dict([('city_code', city_code), ('item_code', item_code), ('missing_price', [])]))

	# agent_secret = None
	# with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secrets.json')) as data_file:
	# 	agent_secret = json.load(data_file)

	# search_tree = ET.parse(os.path.join(os.getcwd(), 'SearchBookingRequest.xml'))

	# for client in clients:

	# 	search_tree.find('.//RequestorID').set('Client', agent_secret[client]['id'])
	# 	search_tree.find('.//RequestorID').set('EMailAddress', agent_secret[client]['email'])
	# 	search_tree.find('.//RequestorID').set('Password', agent_secret[client]['password'])

	# 	search_tree.find('.//FromDate').text = from_date.strftime('%Y-%m-%d')
	# 	search_tree.find('.//ToDate').text = to_date.strftime('%Y-%m-%d')
	# 	search_tree.find('.//BookingDateRange').set('DateType', d_type)

	# 	try:
	# 		r = requests.post(url, data=ET.tostring(search_tree.getroot(), encoding='UTF-8', method='xml'), timeout=600)
	# 	except OSError:
	# 		pp.pprint('Error: OSError.. Searching has stopped..')
	# 		return

	# 	r_tree = ET.fromstring(r.text)

	# 	for booking in r_tree.find('.//Bookings'):
	# 		entry = {}
	# 		entry['client_booking_id'] = entry['agent_booking_id'] = entry['gta_api_booking_id'] = ''
	# 		entry['booking_status'] = entry['booking_creation_date'] = entry['booking_departure_date'] = ''
	# 		entry['booking_name'] = entry['booking_net_price'] = entry['booking_currency'] = ''

	# 		for booking_ref in booking.find('.//BookingReferences'):
	# 			ref_type = booking_ref.get('ReferenceSource')

	# 			if ref_type == REF_CLIENT:
	# 				entry['client_booking_id'] = booking_ref.text
	# 			if ref_type == REF_AGENT:
	# 				entry['agent_booking_id'] = booking_ref.text
	# 			if ref_type == REF_API:
	# 				entry['gta_api_booking_id'] = '041/' + booking_ref.text

	# 		entry['booking_status'] = booking.find('.//BookingStatus').text
	# 		entry['booking_creation_date'] = booking.find('.//BookingCreationDate').text
	# 		entry['booking_departure_date'] = booking.find('.//BookingDepartureDate').text
	# 		entry['booking_name'] = booking.find('.//BookingName').text
	# 		entry['booking_net_price'] = booking.find('.//BookingPrice').get('Nett')
	# 		entry['booking_currency'] = booking.find('.//BookingPrice').get('Currency')

	# 		# fix client with multi ids
	# 		entry['client_name'] = client
	# 		res.append(entry)

	# # keys = res[0].keys()
	# keys = res[0].keys()
	# # with open('output_SearchPrice_' + date.today().strftime('%Y_%m_%d') + '.csv', 'w', encoding='utf-8') as output_file:
	# with open('output_Search_booking_id_' + from_date.strftime('%y%m%d') + '_' + datetime.datetime.now().strftime('%H%M') + '_' + str(duration) + 'd.csv', 'w', newline='', encoding='utf-8') as output_file:
	# 	dict_writer = csv.DictWriter(output_file, keys)
	# 	dict_writer.writeheader()
	# 	dict_writer.writerows(res)
	

if __name__ == '__main__':
	pa_hb()