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
# import logging

def validate_d(date_text):
	try:
		datetime.datetime.strptime(date_text, '%Y-%m-%d')
	except ValueError:
		raise ValueError("Incorrect data format, should be YYYY-MM-DD")

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)

@click.command()
@click.option('--file_name', default='hotel_codes')
@click.option('--from_d', default='2017-03-25')
@click.option('--to_d', default='2017-04-25')
@click.option('--n_sample', default=30, type=int)
@click.option('--skip/--no--skip', default=False)
@click.option('--sample/--no--sample', default=False)
def spplus(file_name, from_d, to_d, skip, n_sample, sample):

	url = 'https://rbs.gta-travel.com/rbscnapi/RequestListenerServlet'
	pp = pprint
	res = []

	validate_d(from_d)
	validate_d(to_d)

	from_date = datetime.datetime.strptime(from_d, '%Y-%m-%d').date()
	to_date = datetime.datetime.strptime(to_d, '%Y-%m-%d').date()

	pp.pprint('? ' + str(skip))

	hotel_codes = []
	with open(file_name, 'r') as file:
		for line in file:
			# pp.pprint(line)
			city_code, item_code = line.rstrip().split('_')
			hotel_codes.append(dict([('city_code', city_code), ('item_code', item_code), ('missing_price', [])]))

	if sample:
		hotel_codes = [ hotel_codes[i] for i in random.sample(range(len(hotel_codes)), k=n_sample) ]

	search_tree = ET.parse(os.path.join(os.getcwd(), 'SearchHotelPricePaxRequest.xml'))

	for hotel_code in hotel_codes:
		pp.pprint('Searching Price for ' + hotel_code['city_code'] + ' ' + hotel_code['item_code'])
		search_tree.find('.//ItemDestination').set('DestinationCode', city_code)
		search_tree.find('.//ItemCode').text = item_code
		# search_tree.find('.//PaxRoom').set('Adults', str(2))

		entry = dict()
		entry['Hotel_Code'] = hotel_code['city_code'] + '_' + hotel_code['item_code']

		num_days = -1

		for single_date in daterange(from_date, to_date):
			search_tree.find('.//CheckInDate').text = single_date.strftime('%Y-%m-%d')
			pp.pprint('Check in date: ' + single_date.strftime('%Y-%m-%d'))
			# pp.pprint('num of days: ' + str(num_days))
			has_price = False

			num_days += 1
			if skip and num_days != 0 and num_days != 6 and num_days != 13 and num_days != 20 and num_days != 27:
				# pp.pprint('num_days: ' + str(num_days))
				continue

			for i in range(3):
				# if has_price:
				# 	break

				pp.pprint('Pax #: ' + str(i + 1))
				search_tree.find('.//PaxRoom').set('Adults', str(i + 1))
				try:
					r = requests.post(url, data=ET.tostring(search_tree.getroot(), encoding='UTF-8', method='xml'), timeout=360)
				except OSError:
					pp.pprint('Error: ignoring OSError...')
					continue

				# pp.pprint('Search price status code: ' + str(r.status_code))
				# pp.pprint(r.headers)
				# pp.pprint('Search price Response body: ' + r.text)

				r_tree = ET.fromstring(r.text)

				# entry['hotel_name'] = room_cat.find('.//Item').text

				if (r_tree.find('.//RoomPrice') == None):
					# hotel_code['missing_price'].append('Pax ' + str(i + 1) + ': ' + single_date.strftime("%Y-%m-%d"))
					pp.pprint('Alert: Price not returned... ')
				else:
					# pp.pprint('Gross: ' + str(r_tree.find('.//RoomPrice').get('Gross')))
					for room_cat in r_tree.find('.//RoomCategories'):
						pp.pprint('Id: ' + str(room_cat.get('Id')))
						pp.pprint('Id: ' + str(room_cat.find('.//Description').text))
						has_price = True
						# break

			entry[single_date.strftime('%Y-%m-%d')] = 'Y' if has_price else 'N'
		res.append(entry)

	keys = res[0].keys()
	# with open('output_SearchPrice_' + date.today().strftime('%Y_%m_%d') + '.csv', 'w', encoding='utf-8') as output_file:
	with open('output_SearchPrice_' + datetime.datetime.now().strftime('%Y_%m_%d_%H_%M') + '.csv', 'w', encoding='utf-8') as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		dict_writer.writeheader()
		dict_writer.writerows(res)
	

if __name__ == '__main__':
	spplus()