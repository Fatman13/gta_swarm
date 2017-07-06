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
def booking():
	pp = pprint
	res = []

	# with Browser() as b:
	driver = webdriver.Firefox()
	driver.implicitly_wait(10) 
	# driver = webdriver.Ie()

	wait_s = 3
	wait_m = 10
	wait_l = 15

	# with open('output_booking_hotel_osaka_href.csv', encoding='utf-8-sig') as csvfile:
	# with open('output_booking_hotel_href_okinawa.csv', encoding='utf-8-sig') as csvfile:
	# with open('output_booking_hotel_href_sapporo.csv', encoding='utf-8-sig') as csvfile:
	# with open('output_booking_hotel_href_nagoya.csv', encoding='utf-8-sig') as csvfile:
	# with open('output_booking_hotel_href_kobe.csv', encoding='utf-8-sig') as csvfile:
	# with open('output_booking_hotel_href_fukuoka.csv', encoding='utf-8-sig') as csvfile:
	# with open('output_booking_hotel_href_phuket.csv', encoding='utf-8-sig') as csvfile:
	with open('output_booking_hotel_href_phuket2.csv', encoding='utf-8-sig') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			if row['hotel_href']:
				url = row['hotel_href']

				driver.get(url)
				element = WebDriverWait(driver, 20).until(
					lambda driver: driver.execute_script("return $.active == 0")
				)
				time.sleep(wait_m)
				# gta_keys.append(row['hotel_href'])

				

				# pp.pprint(entry['hotel_name'])
				# pp.pprint(driver.find_element_by_css_selector('h2#hp_hotel_name').text)

				

				rps = driver.find_elements_by_css_selector('td.roomType.room-type-container.rt__room-detail.rt__room-detail--legibility ')

				for rp in rps:
					entry = {}
					entry['hotel_name'] = driver.find_element_by_css_selector('h2#hp_hotel_name').text
					entry['hotel_href'] = url
					entry['room_name'] = rp.find_element_by_css_selector('a.jqrt.togglelink.js-track-hp-rt-room-name').text
					
					if check_exists_by_css_selector(rp, 'div.iconfont_wrapper > span'):
						facilities = rp.find_elements_by_css_selector('div.iconfont_wrapper > span')
						for facility in facilities:
							entry[facility.text] = 'Y'

					if check_exists_by_css_selector(rp, 'a.more_facilities.rt-show-more-facilities'):
						rp.find_element_by_css_selector('a.more_facilities.rt-show-more-facilities').click()
						facilities = rp.find_elements_by_css_selector('div.rt-all-facilities-hidden > span')
						for facility in facilities:
							entry[facility.text] = 'Y'

					# pp.pprint(entry)
					res.append(entry)
				

	driver.quit()

	field_names = set()
	for entry in res:
		field_names |= set(entry.keys())

	# 
	keys = res[0].keys()
	with open('output_hotel_facilities_' + datetime.datetime.now().strftime('%y%m%d_%H%M') + '.csv', 'w', encoding='utf-8') as output_file:
		# dict_writer = csv.DictWriter(output_file, keys)
		dict_writer = csv.DictWriter(output_file, field_names)
		dict_writer.writeheader()
		dict_writer.writerows(res)
	

if __name__ == '__main__':
	booking()