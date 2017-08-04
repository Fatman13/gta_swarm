#!/usr/bin/env python
# coding=utf-8

import pprint
import csv
import click 
import requests
import datetime as datetime
# from splinter import Browser
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException   
from selenium.common.exceptions import ElementNotVisibleException   
from selenium.common.exceptions import StaleElementReferenceException   
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException

def validate_d(date_text):
	try:
		datetime.datetime.strptime(date_text, '%Y-%m-%d')
	except ValueError:
		raise ValueError("Incorrect data format, should be YYYY-MM-DD")

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)

def find_entry(entry_dict, room_name):
	for entry in entry_dict:
		pprint.pprint(entry)
		if entry['GTA_Room_Name'] == room_name:
			return entry
	return None


@click.command()
@click.option('--filename', default='ctrip_hotel_ids_for_roomtypes')
# @click.option('--days', default=15, type=int)
def ctriproom(filename):
	pp = pprint
	res = []

	# from_date = datetime.datetime.today().date() + datetime.timedelta(days=30)
	from_date = datetime.datetime.today().date() + datetime.timedelta(days=30)
	to_date = from_date + datetime.timedelta(days=1)

	# validate_d(from_d)
	# validate_d(to_d)
	# from_date = datetime.datetime.strptime(from_d, '%Y-%m-%d').date()
	# to_date = datetime.datetime.strptime(to_d, '%Y-%m-%d').date()

	# with Browser() as b:
	driver = webdriver.Firefox()
	driver.implicitly_wait(10) 
	# driver = webdriver.Ie()

	hotel_ids = set()

	with open(filename, encoding='utf-8-sig') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			# pp.pprint(row['hotel_id'])
			hotel_ids.add(row['hotel_id'])

	for counter, hotel_id in enumerate(hotel_ids):
		pp.pprint('Counter: ' + str(counter))

		from_date_plus_one = from_date + datetime.timedelta(days=1)

		url = 'http://hotels.ctrip.com/international/' + \
			str(hotel_id) + '.html?' + \
			'CheckIn=' + from_date.strftime('%Y-%m-%d') + \
			'&CheckOut=' + from_date_plus_one.strftime('%Y-%m-%d')

		pp.pprint(url)
		try:
			driver.get(url)
		except TimeoutException:
			continue

		# element = WebDriverWait(driver, 15).until(
		# 	lambda driver: driver.execute_script("return $.isLoaded == true")
		# )
		time.sleep(5)

		try:
			hotel_name = driver.find_element_by_css_selector('h1.name').text
		except NoSuchElementException:
			continue

		if len(driver.find_elements_by_css_selector('div.hroom_tr.J_baseRoomlist')) == 0:
			continue

		# entry_dict = {}

		for i, elem in enumerate(driver.find_elements_by_css_selector('div.hroom_tr.J_baseRoomlist')):
			# pp.pprint(elem)
			room_name = elem.find_element_by_css_selector('dt.hroom_base_tit').text
			pp.pprint(room_name)

			entry = {}
			entry['Ctrip_Hotel_id'] = hotel_id
			entry['Hotel_Name'] = hotel_name
			entry['Check_in'] = from_date.strftime('%Y-%m-%d')
			entry['Room_Name'] = room_name
			res.append(entry)
		# for key, value in entry_dict.items():
		# 	res.append(entry_dict[key])
		# res.append(entry)

	driver.quit()

	# pp.pprint(res)
	if not res:
		pprint.pprint("List is empty! No room found for every hotel in the file!")
		return

	# keys_max = None
	# k_max = 0
	# for ent in res:
	# 	if len(ent.keys()) > k_max:
	# 		keys_max = ent.keys()
	# 		k_max = len(ent.keys())

	keys = res[0].keys()
	with open('output_Ctrip_Room_' + datetime.datetime.now().strftime('%y%m%d_%H%M') + '.csv', 'w', newline='', encoding='utf-8') as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		# dict_writer = csv.DictWriter(output_file, keys_max)
		dict_writer.writeheader()
		dict_writer.writerows(res)

if __name__ == '__main__':
	ctriproom()