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

def check_exists_by_css_selector(driver, css_selector):
    try:
        driver.find_element_by_css_selector(css_selector)
    except NoSuchElementException:
        return False
    return True

@click.command()
@click.option('--filename', default='haoqiao.csv')
def haoqiao(filename):
	pp = pprint
	res = []

	from_date = datetime.datetime.today().date() + datetime.timedelta(days=15)
	to_date = from_date + datetime.timedelta(days=1)

	# validate_d(from_d)
	# validate_d(to_d)
	# from_date = datetime.datetime.strptime(from_d, '%Y-%m-%d').date()
	# to_date = datetime.datetime.strptime(to_d, '%Y-%m-%d').date()

	# with Browser() as b:
	driver = webdriver.Firefox()
	driver.implicitly_wait(10) 
	# driver = webdriver.Ie()

	# login
	driver.get('http://www.haoqiao.cn/')

	time.sleep(3)
	# jpwNext
	# driver.find_element_by_id("jpwNext").click()
	# $("#jpwClose").click()
	driver.execute_script('$(\"#jpwClose\").click()')
	# driver.find_element_by_id("jpwClose").click()
	# time.sleep(10)
	# jpwFinish
	# driver.find_element_by_id("jpwFinish").click()

	company_code = driver.find_element_by_id("J_header_code")
	username = driver.find_element_by_id("J_header_name")
	password = driver.find_element_by_id("J_header_paw_txt")

	company_code.send_keys("H1191")
	username.send_keys("yzj")
	password.send_keys("yzj2022")

	driver.find_element_by_id("J_header_login").click()

	hotels = []

	with open(filename, encoding='utf-8-sig') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			# pp.pprint(row['hotel_id'])
			entry = dict()
			entry['hq_id'] = row['hq_id']
			entry['hq_city_id'] = row['hq_city_id']
			hotels.append(entry)
			# hotels.add(row['hotel_id'])

	for hotel in hotels:
		from_date_plus_one = from_date + datetime.timedelta(days=1)

		# http://www.haoqiao.cn/bangkok_c1/?checkin=2017-06-29&checkout=2017-06-30&room=1&adult=2
		url = 'http://www.haoqiao.cn/' + \
			str(hotel['hq_city_id']) + '/' + str(hotel['hq_id']) + '.html?' + \
			'checkin=' + from_date.strftime('%Y-%m-%d') + \
			'&checkout=' + from_date_plus_one.strftime('%Y-%m-%d') + \
			'&room=1&adult=2'

		pp.pprint(url)
		try:
			driver.get(url)
		except TimeoutException:
			continue

		# element = WebDriverWait(driver, 15).until(
		# 	lambda driver: driver.execute_script("return $.isLoaded == true")
		# )
		time.sleep(15)

		entry = {}

		try:
			hotel_name = driver.find_element_by_css_selector('div.hotle-detail-title').text.splitlines()[0]
		except NoSuchElementException:
			continue

		if len(driver.find_elements_by_css_selector('div.hotel-d-p-wrap.J_sort_price')) == 0:
			continue

		entry_dict = {}

		for i, elem in enumerate(driver.find_elements_by_css_selector('div.hotel-d-p-wrap.J_sort_price')):
			# pp.pprint(elem)
			try:
				# room_name = elem.find_element_by_css_selector('span.hotel-d-p-l-title.J_d_price_title > em').text
				room_name = elem.find_element_by_css_selector('span.hotel-d-p-l-title.J_d_price_title > em').text
				pp.pprint(room_name)
			except NoSuchElementException:
				pp.pprint('No such element...' + str(hotel['hq_city_id']) + ' ' + str(hotel['hq_id']) )
				continue

			entry_dict[str(i)] = {}
			entry_dict[str(i)]['hotel_city_id'] = hotel['hq_city_id']
			entry_dict[str(i)]['hotel_id'] = hotel['hq_id']
			entry_dict[str(i)]['Hotel_Name'] = hotel_name
			entry_dict[str(i)]['Check_in'] = from_date.strftime('%Y-%m-%d')
			# entry_dict[str(i)]['count'] = 0

			for rp in elem.find_elements_by_css_selector('tr.hotel-d-p-list-td'):
				# pp.pprint(rp)

				# try:
				# 	book_btn = rp.find_element_by_css_selector('button.J_bookNowBtn.btns_base22')
				# except NoSuchElementException:
				# 	pp.pprint('Warning: No booking button...')
				# 	continue

				try:
					# entry = dict()
					# entry['ctrip_hotel_id'] = hotel_id
					# entry['Hotel_Name'] = hotel_name

					# entry['GTA_Room_Name'] = room_name
					entry_dict[str(i)]['hq_Room_Name'] = room_name

					entry_dict[str(i)]['hq_Room_Description'] = rp.find_element_by_css_selector('td.detail-price-info > div').text.replace(',', ' ') or ''
					# entry['RP_id'] = book_btn.get_attribute('id').rstrip().split('_')[2]
					# entry_dict[str(i)]['GTA_Bed'] = rp.find_element_by_css_selector('.hroom_col.hroom_col_bed.J_facilitiesInfoLogo').text or ''

					# n_guest_ele = rp.find_element_by_css_selector('.hroom_col.hroom_col_people')
					# entry_dict[str(i)]['hq_guest_#'] = re.sub('[^0-9]', '', n_guest_ele.find_element_by_tag_name('span').get_attribute('title'))
					'div.hotel-d-p-t-canbak.J_tips_canbre > i'

					if check_exists_by_css_selector(rp, 'div.hotel-d-p-t-canbak.J_tips_canbre > i'):
						entry_dict[str(i)]['hq_Breakfast'] = rp.find_element_by_css_selector('div.hotel-d-p-t-canbak.J_tips_canbre > i').text.replace(',', ' ')
					if check_exists_by_css_selector(rp, 'a.hotel-d-p-b-a'):
						entry_dict[str(i)]['hq_Breakfast'] = rp.find_element_by_css_selector('a.hotel-d-p-b-a').text.replace(',', ' ')
					# entry_dict[str(i)]['hq_Policy'] = ''.join(rp.find_element_by_css_selector('div.hotel-d-p-t-canbak.J_tips_canbre > span > i').text.split())
					# entry_dict[str(i)]['hq_Policy'] = rp.find_element_by_css_selector('div.hotel-d-p-t-canbak.J_tips_canbre > span > i').text
					entry_dict[str(i)]['hq_Policy'] = rp.find_elements_by_css_selector('div.hotel-d-p-t-canbak.J_tips_canbre')[1].get_attribute('data-val').replace(',', ' ')

					# entry['GTA_Check_in'] = from_date.strftime('%Y-%m-%d')
					entry_dict[str(i)]['hq_Price'] = re.sub('[^0-9]', '', rp.find_element_by_css_selector('span.hotel-d-p-t-canbak.J_hotel_price_tips > i').text)
					# res.append(entry)
				except StaleElementReferenceException:
					pp.pprint("Error: Elem became stale... fffffffff...")

				break

		for key, value in entry_dict.items():
			res.append(entry_dict[key])
		# res.append(entry)

	driver.quit()

	# pp.pprint(res)

	keys_max = None
	k_max = 0
	for ent in res:
		if len(ent.keys()) > k_max:
			keys_max = ent.keys()
			k_max = len(ent.keys())

	# keys = res[0].keys()
	with open('output_haoqiao_' + datetime.datetime.now().strftime('%y%m%d_%H%M') + '.csv', 'w', encoding='utf-8') as output_file:
		# dict_writer = csv.DictWriter(output_file, keys)
		dict_writer = csv.DictWriter(output_file, keys_max)
		dict_writer.writeheader()
		dict_writer.writerows(res)

if __name__ == '__main__':
	haoqiao()