#!/usr/bin/env python
# coding=utf-8

import pprint
import csv
import click 
import requests
import datetime as datetime
from bs4 import BeautifulSoup
# from splinter import Browser
import time
import re
import copy
import os
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException   
from selenium.common.exceptions import ElementNotVisibleException   
from selenium.common.exceptions import StaleElementReferenceException   
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import TimeoutException
from requests.exceptions import ConnectionError
from requests.exceptions import ChunkedEncodingError
from requests.exceptions import ReadTimeout

TIME_OUT = 30

# hua shi shui jiao
def hua_style_sleep(seconds):
	for i in range(seconds):
		if i % 10 == 0:
			print('hc sleeping..' + str(i))
		time.sleep(1)

MAX_RETRIES = 300

@click.command()
# @click.option('--filename', default='output_Search_item_hr_171027_1210.csv')
# @click.option('--days', default=15, type=int)
def steemit():
	url = 'https://steemit.com/cn/@fatman13/netflix'

	driver = webdriver.Firefox()
	driver.implicitly_wait(10) 

	for i in range(MAX_RETRIES):
		try:
			driver.get(url)
		except TimeoutException:
			print('Error: f.. time out..')
			continue
		except NoSuchElementException:
			print('Error: f.. not displaying properly?..')
			continue 
		except WebDriverException:
			print('Error: f.. WebDriverException..')
			continue
		# scroll to the bottom
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		
		counter_ele = driver.find_element_by_css_selector('.PageViewsCounter')
		print('Current Views.. ' + str(counter_ele.get_attribute('title')))
		hua_style_sleep(600)
	driver.quit()
	# # cookies = login_GCres(driver)

	# bookings = []
	# res = []
	# # filename = 'gtaConfirmRefs_5867_2017-06-30_2017-07-07.csv'
	# with open(filename, encoding='utf-8-sig') as csvfile:
	# 	ids = set()
	# 	reader = csv.DictReader(csvfile)
	# 	for row in reader:
	# 		# pp.pprint(row['hotel_id'])
	# 		# if row['gta_api_booking_id'] not in ids:
	# 		entry = dict()
	# 		entry['client_booking_id'] = row['client_booking_id']
	# 		entry['agent_booking_id'] = row['agent_booking_id']
	# 		entry['gta_api_booking_id'] = row['gta_api_booking_id']
	# 		entry['booking_status'] = row['booking_status']
	# 		entry['booking_creation_date'] = row['booking_creation_date']
	# 		entry['booking_departure_date'] = row['booking_departure_date']
	# 		entry['booking_name'] = row['booking_name']
	# 		entry['booking_net_price'] = row['booking_net_price']
	# 		entry['booking_currency'] = row['booking_currency']
	# 		entry['hotel_confirmation_#'] = ''
	# 		entry['hotel_confirmation_status'] = ''
	# 		if 'hotel_confirmation_#' in row:
	# 			entry['hotel_confirmation_#'] = row['hotel_confirmation_#']
	# 		if 'hotel_confirmation_status' in row:
	# 			entry['hotel_confirmation_status'] = row['hotel_confirmation_status']
	# 		entry['hotel_email'] = ''
	# 		bookings.append(entry)
	# 		# ids.add(row['gta_api_booking_id'])

	# # print(bookings)

	# for counter, booking in enumerate(bookings):
	# 	print('Search booking id: ' + str(counter) + ': ' + str(booking['gta_api_booking_id']))

	# 	if counter % 300 == 0:
	# 		print('Logging in..')
	# 		cookies = login_GCres(driver)
	# 		if not cookies:
	# 			print('Fatal: Failed to get cookies...')
	# 			break  
	# 		if len(cookies.items()) <= 1:
	# 			print('Fatal: Login may have failed...')
	# 			break

	# 	if CONFIRMED not in booking['booking_status']:
	# 		print('Booking not confirmed.. skipping..')
	# 		continue

	# 	search_url = 'http://hotels.gta-travel.com/gcres/bookingSearch/search'
	# 	payload = {'bookingId': booking['gta_api_booking_id'],
	# 			'searchType': 'manual',
	# 			'currentLanguage': 'en',
	# 			'bookingType': 'F',
	# 			'dateType': 'A',
	# 			'statusAll': '*',
	# 			'statuses': 'P',
	# 			'statuses': 'C',
	# 			'statuses': 'R',
	# 			'statuses': 'X',
	# 			'search': 'Search'}
	# 	try:
	# 		r = requests.get(search_url, params=payload, cookies=cookies, timeout=TIME_OUT)
	# 	except ConnectionError as e:
	# 		print('fatal Connection error...s')
	# 		continue
	# 	except ChunkedEncodingError as e:
	# 		print('fatal Chunked encoding error...s')
	# 		continue
	# 	except ReadTimeout as e:
	# 		print('fatal Read timeout error...r')
	# 		continue
	# 	# print(r.text)

	# 	soup = BeautifulSoup(r.text)

	# 	for i in range(4):
	# 		tr_element = soup.find('tr', id='bkgList_row' + str(i))
	# 		if tr_element == None:
	# 			# first time no search result from ajax search request
	# 			if i == 0:
	# 				entry = copy.deepcopy(booking)
	# 				res.append(entry)
	# 				break
	# 			continue
	# 		hotel_onclick = tr_element['onclick']
	# 		# print(hotel_onclick)

	# 		try:
	# 			booking_id = re.search('/gcres/bookingHeader/show/(\d+)', hotel_onclick).group(1)
	# 			hotel_id = re.search('/gcres/bookingContacts/section/(\d+)', hotel_onclick).group(1)
	# 		except AttributeError:
	# 			booking_id = ''
	# 			hotel_id = ''

	# 		if booking_id == '':
	# 			continue
	# 		print('Booking id: ' + booking_id)
	# 		# print('Hotel id: ' + hotel_id)

	# 		booking['hotel_confirmation_status'] = get_hotel_status(booking_id, cookies)

	# 		# hotel_ref_num = get_hotel_ref(booking_id, cookies)
	# 		# booking['hotel_confirmation_status'] = ''
	# 		# booking['hotel_confirmation_#'] = get_hotel_ref(booking_id, cookies)
	# 		# if hotel_ref_num == None:
	# 		# 	# when internet is extremely slow booking['hotel_confirmation_status'] would be None sometimes
	# 		# 	if booking['hotel_confirmation_status'] != None and HOTEL_CONFIRMED in booking['hotel_confirmation_status']:
	# 		# 		# ctrip doesn't like this...
	# 		# 		# booking['hotel_confirmation_#'] = 'Confirmed'
	# 		# 		pass
	# 		# 	# elif TO_REGISTER in booking['hotel_confirmation_status']:
	# 		# 	# 	continue
	# 		# 	else:
	# 		# 		booking['hotel_confirmation_#'] = hotel_ref_num
	# 		# if hotel_ref_num != None:
	# 		# 	booking['hotel_confirmation_#'] = hotel_ref_num
	# 		booking['hotel_confirmation_#'] = get_hotel_ref(booking_id, cookies)

	# 		# turn off for now
	# 		# booking['hotel_email'] = get_hotel_email(hotel_id, cookies)

	# 		entry = copy.deepcopy(booking)
	# 		# print(entry)
	# 		res.append(entry)

	# # print('fetching hotel ref...')

	# # hotel_ref_url = 'http://hotels.gta-travel.com/gcres/bookingDetail/section/37102807?cbsRevision=0'
	# # r = requests.get(hotel_ref_url, cookies=cookies)

	# # # print(r.text)
	# # print('parsing hotel ref...')

	# # soup = BeautifulSoup(r.text)
	# # # hotel_ref = name = soup.find('label', attrs={"for":True}).get_text()
	# # # hotel_ref_label = name = soup.find('label', {"for":"hotelRef"}).get_text()
	# # hotel_ref_label = soup.find('label', {"for":"hotelRef"})

	# # if hotel_ref_label != None:
	# # 	hotel_ref = hotel_ref_label.parent.get_text().replace(HOTEL_REF, '').strip()
	# # 	print(hotel_ref)

	# # cookies = dict(JSESSIONID='A43FFE768312463D43CFE945A5292EB9.01bgs-tc4',
	# # 				__qca='P0-1834765283-1494573658960',
	# # 				_ga='GA1.2.440674599.1494573659',
	# # 				qualifier='GTA')

	

	# keys = res[0].keys()
	# with open('output_hotel_ref_' + datetime.datetime.now().strftime('%y%m%d_%H%M') + '.csv', 'w', newline='', encoding='utf-8') as output_file:
	# 	dict_writer = csv.DictWriter(output_file, keys)
	# 	# dict_writer = csv.DictWriter(output_file, field_names)
	# 	dict_writer.writeheader()
	# 	dict_writer.writerows(res)

if __name__ == '__main__':
	steemit()