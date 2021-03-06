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

def check_exists_by_css_selector(element, selector):
	try:
		element.find_element_by_css_selector(selector)
	except NoSuchElementException:
		return False
	return True

@click.command()
@click.option('--filename', default='output_booking_hotel_href_test15.csv')
@click.option('--city', default='test_city')
def booking(filename, city):
	pp = pprint
	res = []

	# with Browser() as b:
	driver = webdriver.Firefox()
	driver.implicitly_wait(10) 
	# driver = webdriver.Ie()

	wait_s = 3
	wait_m = 5
	wait_l = 15

	# with open('output_booking_hotel_tokyo_href.csv', encoding='utf-8-sig') as csvfile:
	# with open('output_booking_hotel_osaka_href.csv', encoding='utf-8-sig') as csvfile:
	# with open('output_booking_hotel_href_okinawa.csv', encoding='utf-8-sig') as csvfile:
	# with open('output_booking_hotel_href_sapporo.csv', encoding='utf-8-sig') as csvfile:
	# with open('output_booking_hotel_href_nagoya.csv', encoding='utf-8-sig') as csvfile:
	# with open('output_booking_hotel_href_kobe.csv', encoding='utf-8-sig') as csvfile:
	# with open('output_booking_hotel_href_fukuoka.csv', encoding='utf-8-sig') as csvfile:
	# with open('output_booking_hotel_href_phuket.csv', encoding='utf-8-sig') as csvfile:
	with open(filename, encoding='utf-8-sig') as csvfile:
		reader = csv.DictReader(csvfile)
		for counter, row in enumerate(reader):
			if row['hotel_href']:
				url = row['hotel_href']

				try:
					driver.get(url)
					element = WebDriverWait(driver, 10).until(
						lambda driver: driver.execute_script("return $.active == 0")
					)
				except TimeoutException as e:
					print('Error: time out exception..')
					continue
				except WebDriverException as e:
					print('Error: wev driver exception..')
					continue
				# try:
					
				# except WebDriverException as e:
				# 	print('Error: failed to get hotel... WebDriverException..')
				# 	continue
				time.sleep(wait_m)
				# gta_keys.append(row['hotel_href'])

				sections = driver.find_elements_by_css_selector('div.facilitiesChecklistSection')
				entry = {}
				entry['hotel_name'] = driver.find_element_by_css_selector('h2#hp_hotel_name').text
				print('hotel name: ' + str(counter) + ': ' + str(entry['hotel_name']))
				if entry['hotel_name'] == None or entry['hotel_name'] == '':
					entry['hotel_name'] = driver.find_element_by_css_selector('h1.b-crumb__hp-current').text
					print('hotel name 2nd try: ' + str(counter) + ': ' + str(entry['hotel_name']))
				entry['hotel_star'] = driver.find_element_by_css_selector('i.bk-icon-wrapper.bk-icon-stars.star_track').get_attribute('title')

				# pp.pprint(entry['hotel_name'])
				# pp.pprint(driver.find_element_by_css_selector('h2#hp_hotel_name').text)

				# entry['hotel_href'] = url

				for section in sections:
					section_name = section.find_element_by_css_selector('h5').text
					# entry[section_name] = []
					lis = section.find_elements_by_css_selector('li')
					for li in lis:
						if check_exists_by_css_selector(li, 'span'):
							# entry[section_name].append(str(li.find_element_by_css_selector('span').text))
							entry[str(li.find_element_by_css_selector('span').text)] = 'Y'
						else:
							# entry[section_name].append(str(li.text))
							entry[str(li.text)] = 'Y'
				# pp.pprint(entry)
				entry['hotel_href'] = url
				res.append(entry)			

	driver.quit()

	field_names = set()
	for entry in res:
		field_names |= set(entry.keys())

	# keys_max = None
	# k_max = 0
	# for ent in res:
	# 	if len(ent.keys()) > k_max:
	# 		keys_max = ent.keys()
	# 		k_max = len(ent.keys())

	if not res:
		print('Res empty.. ')
		return

	# 
	keys = res[0].keys()
	with open('output_hotel_facilities_' + city + datetime.datetime.now().strftime('_%y%m%d_%H%M') + '.csv', 'w', newline='', encoding='utf-8') as output_file:
		# dict_writer = csv.DictWriter(output_file, keys)
		dict_writer = csv.DictWriter(output_file, field_names)
		dict_writer.writeheader()
		dict_writer.writerows(res)

if __name__ == '__main__':
	booking()