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

import multiprocessing

TIME_OUT = 30

# hua shi shui jiao
def hua_style_sleep(seconds):
	for i in range(seconds):
		print('hc sleeping..' + str(i))
		time.sleep(1)

hc_secret = None
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secrets.json')) as data_file:    
	hc_secret = (json.load(data_file))['hc']

def validate_d(date_text):
	try:
		datetime.datetime.strptime(date_text, '%Y-%m-%d')
	except ValueError:
		raise ValueError("Incorrect data format, should be YYYY-MM-DD")

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)

HOTEL_REF = 'Hotel Ref:'

def get_hotel_ref(booking_id, cookies):
	hotel_ref_url = 'http://hotels.gta-travel.com/gcres/bookingDetail/section/' + str(booking_id) + '?cbsRevision=0'
	try:
		r = requests.get(hotel_ref_url, cookies=cookies, timeout=TIME_OUT)
	except ConnectionError as e:
		print('fatal Connection error...r')
		return None
	except ReadTimeout as e:
		print('fatal Read timeout error...r')
		return None
	except ChunkedEncodingError as e:
		print('fatal Chunked encoding error...s')
		return None
	# print('parsing hotel ref...')

	soup = BeautifulSoup(r.text)
	hotel_ref_label = soup.find('label', {"for":"hotelRef"})

	if hotel_ref_label != None:
		hotel_ref = hotel_ref_label.parent.get_text().replace(HOTEL_REF, '').strip()
		# print(hotel_ref)
		return hotel_ref
	return None

STATUS = 'Status:'

def get_hotel_status(booking_id, cookies):
	hotel_status_url = 'http://hotels.gta-travel.com/gcres/bookingHeader/show/' + str(booking_id) + '?cbsRevision=0'
	try: 
		r = requests.get(hotel_status_url, cookies=cookies, timeout=TIME_OUT)
	except ConnectionError as e:
		print('fatal Connection error...st')
		return None
	except ReadTimeout as e:
		print('fatal Read timeout error...r')
		return None
	except ChunkedEncodingError as e:
		print('fatal Chunked encoding error...s')
		return None

	soup = BeautifulSoup(r.text)
	hotel_status_label = soup.find('label', {"for":"status"})

	if hotel_status_label != None:
		# booking_status = hotel_status_label.parent.get_text().replace(STATUS, '').strip()
		booking_status = ' '.join(hotel_status_label.parent.get_text().replace(STATUS, '').strip().split())
		# print(booking_status)
		return booking_status
	return None

RESERVATIONS = 'FIT Reservations'

def get_hotel_email(hotel_id, cookies):
	# section=bookingContacts&containingElementContent=bookingContactsContent&containingElementCreate=bookingContacts_create&additionalParams=
	payload = {'section': 'bookingContacts',
				'containingElementContent': 'bookingContactsContent',
				'containingElementCreate': 'bookingContacts_create'
				}
	hotel_status_url = 'http://hotels.gta-travel.com/gcres/bookingContacts/list/' + str(hotel_id)
	try: 
		r = requests.get(hotel_status_url, params=payload, cookies=cookies, timeout=TIME_OUT)
	except ConnectionError as e:
		print('fatal Connection error...st')
		return None
	except ReadTimeout as e:
		print('fatal Read timeout error...r')
		return None
	except ChunkedEncodingError as e:
		print('fatal Chunked encoding error...s')
		return None

	soup = BeautifulSoup(r.text)
	# hotel_email_td = soup.find("td", text=RESERVATIONS)
	hotel_email_tbl = soup.find("tbody")
	if hotel_email_tbl == None:
		return None

	rows = hotel_email_tbl.find_all('tr')
	if rows == None:
		return None

	hotel_email_td = None

	for row in rows:
		cols = row.find_all('td')
		if cols[0].text == RESERVATIONS:
			hotel_email_td = cols[5]
			# for i in range(5):
			# 	hotel_email_td = hotel_email_td.find_next_sibling("td")
			# 	break

	if hotel_email_td != None:
		# booking_status = hotel_status_label.parent.get_text().replace(STATUS, '').strip()
		# booking_status = ' '.join(hotel_status_label.parent.get_text().replace(STATUS, '').strip().split())
		hotel_email = hotel_email_td.text.strip()
		# print(hotel_email)
		return hotel_email
	return None

TO_REGISTER = 'Confirmed (to register)'

MAX_RETRIES = 100

def login_GCres(driver):
	GCres_url = 'https://hotels.gta-travel.com/gcres/auth/securelogin'

	for i in range(MAX_RETRIES):
		try:
			driver.get(GCres_url)
	
			company_code = driver.find_element_by_id("qualifier")
			username = driver.find_element_by_id("username")
			password = driver.find_element_by_id("password")
		except TimeoutException:
			print('Error: f.. GCres login page time out..')
			print('retry.. ' + str(i))
			continue
		except NoSuchElementException:
			print('Error: f.. GCres login page not displaying properly?..')
			print('retry.. ' + str(i))	
			continue 
		except WebDriverException:
			print('Error: f.. GCres login WebDriverException..')
			print('retry.. ' + str(i))	
			continue

		company_code.clear()
		username.clear()
		password.clear()

		company_code.send_keys("GTA")
		username.send_keys(hc_secret['username'])
		password.send_keys(hc_secret['password'])

		driver.find_element_by_id("login").click()
		time.sleep(5)

		# get cookie
		cookies = {}
		for cookie in driver.get_cookies():
			# pprint.pprint(cookie)
			pprint.pprint('Setting cookie..')
			cookies[cookie['name']] = cookie['value']

		print(cookies)
		if len(cookies.items()) <= 1:
			print('Warning: Retry login.. ' + str(i))
			hua_style_sleep(30)
			continue
		else:
			print('Cookies secured.. ' + str(i))
			break
	return cookies

CONFIRMED = 'Confirmed or Completed'
HOTEL_CONFIRMED = 'Confirmed (registered )'

def get_hotel_conf(booking):
	# print('Search booking id: ' + str(booking['gta_api_booking_id']))
	print('pid: {} Search booking id: {}'.format(os.getpid(), str(booking['gta_api_booking_id'])))
	results = []

	if not booking['cookies']:
		print('Fatal: Failed to get cookies...')
		return None  
	if len(booking['cookies'].items()) <= 1:
		print('Fatal: Login may have failed...')
		return None

	if CONFIRMED not in booking['booking_status']:
		print('Booking not confirmed.. skipping..')
		return None

	search_url = 'http://hotels.gta-travel.com/gcres/bookingSearch/search'
	payload = {'bookingId': booking['gta_api_booking_id'],
				'searchType': 'manual',
				'currentLanguage': 'en',
				'bookingType': 'F',
				'dateType': 'A',
				'statusAll': '*',
				'statuses': 'P',
				'statuses': 'C',
				'statuses': 'R',
				'statuses': 'X',
				'search': 'Search'}
	try:
		r = requests.get(search_url, params=payload, cookies=booking['cookies'], timeout=TIME_OUT)
	except ConnectionError as e:
		print('fatal Connection error...s')
		return None
	except ChunkedEncodingError as e:
		print('fatal Chunked encoding error...s')
		return None
	except ReadTimeout as e:
		print('fatal Read timeout error...r')
		return None
	# print(r.text)
	soup = BeautifulSoup(r.text)

	for i in range(4):
		tr_element = soup.find('tr', id='bkgList_row' + str(i))
		if tr_element == None:
			# first time no search result from ajax search request
			if i == 0:
				entry = copy.deepcopy(booking)
				results.append(entry)
				return results
			continue
		hotel_onclick = tr_element['onclick']
		# print(hotel_onclick)

		try:
			booking_id = re.search('/gcres/bookingHeader/show/(\d+)', hotel_onclick).group(1)
			hotel_id = re.search('/gcres/bookingContacts/section/(\d+)', hotel_onclick).group(1)
		except AttributeError:
			booking_id = ''
			hotel_id = ''

		if booking_id == '':
			continue
		# print('Booking id: ' + booking_id)
		# print('Hotel id: ' + hotel_id)

		booking['hotel_confirmation_status'] = get_hotel_status(booking_id, booking['cookies'])
		booking['hotel_confirmation_#'] = get_hotel_ref(booking_id, booking['cookies'])
		entry = copy.deepcopy(booking)
		results.append(entry)

	return results


def hotel_conf_pool(bookings):
	# pool = ThreadPool(threads)
	# results = pool.map(asp, search_requests)
	# pool.close()
	# pool.join()
	PROCESSES = 4
	with multiprocessing.Pool(PROCESSES) as pool:
		results = pool.map(get_hotel_conf, bookings)
	return results

@click.command()
@click.option('--filename', default='output_Search_item_hr_171127_1032.csv')
# @click.option('--days', default=15, type=int)
def hc_pool(filename):
	bookings = []
	res = []
	# filename = 'gtaConfirmRefs_5867_2017-06-30_2017-07-07.csv'
	with open(filename, encoding='utf-8-sig') as csvfile:
		ids = set()
		reader = csv.DictReader(csvfile)
		for row in reader:
			# pp.pprint(row['hotel_id'])
			# if row['gta_api_booking_id'] not in ids:
			entry = dict()
			entry['client_booking_id'] = row['client_booking_id']
			entry['agent_booking_id'] = row['agent_booking_id']
			entry['gta_api_booking_id'] = row['gta_api_booking_id']
			entry['booking_status'] = row['booking_status']
			entry['booking_creation_date'] = row['booking_creation_date']
			entry['booking_departure_date'] = row['booking_departure_date']
			entry['booking_name'] = row['booking_name']
			entry['booking_net_price'] = row['booking_net_price']
			entry['booking_currency'] = row['booking_currency']
			entry['hotel_confirmation_#'] = ''
			entry['hotel_confirmation_status'] = ''
			if 'hotel_confirmation_#' in row:
				entry['hotel_confirmation_#'] = row['hotel_confirmation_#']
			if 'hotel_confirmation_status' in row:
				entry['hotel_confirmation_status'] = row['hotel_confirmation_status']
			entry['hotel_email'] = ''
			bookings.append(entry)
			# ids.add(row['gta_api_booking_id'])

	# print(bookings)

	driver = webdriver.Firefox()
	driver.implicitly_wait(10)
	print('Logging in..')
	cookies = login_GCres(driver)

	for booking in bookings:
		booking['cookies'] = cookies

	results = hotel_conf_pool(bookings)
	# print(results)
	# results = filter(None, res)
	# print(results)

	for rt in results:
		if rt is not None:
			for ent in rt:
				ent.pop('cookies')
				res.append(ent)
	# print(res)

	driver.quit()

	if not res:
		print('List is empty!')
		return

	keys = res[0].keys()
	with open('output_hotel_ref_' + datetime.datetime.now().strftime('%y%m%d_%H%M') + '.csv', 'w', newline='', encoding='utf-8') as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		# dict_writer = csv.DictWriter(output_file, field_names)
		dict_writer.writeheader()
		dict_writer.writerows(res)

if __name__ == '__main__':
	multiprocessing.freeze_support()
	hc_pool()