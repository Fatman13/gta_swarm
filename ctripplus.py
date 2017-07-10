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
@click.option('--filename', default='ctrip_hotel_ids')
@click.option('--days', default=15, type=int)
def ctripplus(filename, days):
	pp = pprint
	res = []

	# from_date = datetime.datetime.today().date() + datetime.timedelta(days=30)
	from_date = datetime.datetime.today().date() + datetime.timedelta(days=days)
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

	for hotel_id in hotel_ids:
		from_date_plus_one = from_date + datetime.timedelta(days=1)

		url = 'http://hotels.ctrip.com/international/' + \
			str(hotel_id) + '.html?' + \
			'CheckIn=' + from_date.strftime('%Y-%m-%d') + \
			'&CheckOut=' + from_date_plus_one.strftime('%Y-%m-%d') + \
			'&fixsubhotel=t'

		pp.pprint(url)
		try:
			driver.get(url)
		except TimeoutException:
			continue

		# element = WebDriverWait(driver, 15).until(
		# 	lambda driver: driver.execute_script("return $.isLoaded == true")
		# )
		time.sleep(10)

		entry = {}

		try:
			hotel_name = driver.find_element_by_css_selector('h1.name').text
		except NoSuchElementException:
			continue

		if len(driver.find_elements_by_css_selector('div.hroom_tr.J_baseRoomlist')) == 0:
			continue

		entry_dict = {}

		for i, elem in enumerate(driver.find_elements_by_css_selector('div.hroom_tr.J_baseRoomlist')):
			# pp.pprint(elem)
			room_name = elem.find_element_by_css_selector('dt.hroom_base_tit').text
			pp.pprint(room_name)

			entry_dict[str(i)] = {}
			entry_dict[str(i)]['ctrip_hotel_id'] = hotel_id
			entry_dict[str(i)]['Hotel_Name'] = hotel_name
			entry_dict[str(i)]['Check_in'] = from_date.strftime('%Y-%m-%d')
			entry_dict[str(i)]['count'] = 0

			for rp in elem.find_elements_by_css_selector('div.hroom_tr_col.J_subRoomlist'):
				# pp.pprint(rp)

				try:
					book_btn = rp.find_element_by_css_selector('button.J_bookNowBtn.btns_base22')
				except NoSuchElementException:
					pp.pprint('Warning: No booking button...')
					continue

				try:
					# entry = dict()
					# entry['ctrip_hotel_id'] = hotel_id
					# entry['Hotel_Name'] = hotel_name

					# entry['GTA_Room_Name'] = room_name
					entry_dict[str(i)]['GTA_Room_Name'] = room_name

					entry_dict[str(i)]['GTA_Room_Description'] = rp.find_element_by_css_selector('.hroom_roomname.J_rooms_name').text or ''
					# entry['RP_id'] = book_btn.get_attribute('id').rstrip().split('_')[2]
					entry_dict[str(i)]['GTA_Bed'] = rp.find_element_by_css_selector('.hroom_col.hroom_col_bed.J_facilitiesInfoLogo').text or ''

					n_guest_ele = rp.find_element_by_css_selector('.hroom_col.hroom_col_people')
					entry_dict[str(i)]['GTA_guest_#'] = re.sub('[^0-9]', '', n_guest_ele.find_element_by_tag_name('span').get_attribute('title'))

					entry_dict[str(i)]['GTA_Breakfast'] = rp.find_element_by_css_selector('.abbr.J_facilitiesInfoLogo').text
					entry_dict[str(i)]['GTA_Policy'] = ''.join(rp.find_element_by_css_selector('.abbr.J_cancelBookingLogo').text.split())
					# entry['GTA_Check_in'] = from_date.strftime('%Y-%m-%d')
					entry_dict[str(i)]['GTA_Price(on ctrip)'] = re.sub('[^0-9]', '', rp.find_element_by_css_selector('.txt_taxtips').text)
					# res.append(entry)
				except StaleElementReferenceException:
					pp.pprint("Error: Elem became stale... fffffffff...")

				break

			

		# second run..
		url = 'http://hotels.ctrip.com/international/' + \
			str(hotel_id) + '.html?' + \
			'CheckIn=' + from_date.strftime('%Y-%m-%d') + \
			'&CheckOut=' + from_date_plus_one.strftime('%Y-%m-%d')

		pp.pprint(url)

		try:
			driver.get(url)
		except TimeoutException:
			continue


		time.sleep(10)
		# element = WebDriverWait(driver, 15).until(
		# 	lambda driver: driver.execute_script("return $.isLoaded == true")
		# )
		# time.sleep(10)

		try:
			driver.find_elements_by_css_selector('a.foldMe')[-1].click()
		except ElementNotVisibleException:
			pp.pprint('Warning: No expanding...')
		except IndexError:
			pp.pprint('Error: a.foldMe out of bound...')
		except WebDriverException:
			pp.pprint('Error: WebDriverException when clicking expanding all...')

		time.sleep(5)

		# pprint.pprint(entry_dict)

		for i, elem in enumerate(driver.find_elements_by_css_selector('div.hroom_tr.J_baseRoomlist')):
			# pp.pprint(elem)
			room_name = elem.find_element_by_css_selector('dt.hroom_base_tit').text
			# pp.pprint(room_name)

			entry = None
			# entry = find_entry(entry_dict, room_name)

			# for key, value in entry_dict.items():
			# 	# pprint.pprint(entry)
			# 	if entry_dict[key]['GTA_Room_Name'] == room_name:
			# 		entry = entry_dict[key]

			for rp in elem.find_elements_by_css_selector('div.hroom_tr_col.J_subRoomlist'):
				# pp.pprint(rp)

				try:
					book_btn = rp.find_element_by_css_selector('button.J_bookNowBtn.btns_base22')
				except NoSuchElementException:
					pp.pprint('Warning: No booking button...')
					continue

				try:

					n_guest_ele = rp.find_element_by_css_selector('.hroom_col.hroom_col_people')
					n_guest = re.sub('[^0-9]', '', n_guest_ele.find_element_by_tag_name('span').get_attribute('title'))
					# n_guests = re.sub('[^0-9]', '', rp.find_element_by_css_selector('.txt_taxtips').get('title'))

					for key, value in entry_dict.items():
						# pprint.pprint(entry)
						if entry_dict[key]['GTA_Room_Name'] == room_name and entry_dict[key]['GTA_guest_#'] == n_guest:
							entry = entry_dict[key]

					# entry = dict()
					if entry == None:
						continue

					breakfast = rp.find_element_by_css_selector('.abbr.J_facilitiesInfoLogo').text
					policy = ''.join(rp.find_element_by_css_selector('.abbr.J_cancelBookingLogo').text.split())

					if entry['GTA_Breakfast'] != breakfast:
						continue

					# if not( (('不可取消' in policy) and ('不可取消' in entry['GTA_Policy'])) or ( ('免费取消' in policy) and ('免费取消' in entry['GTA_Policy']) ) ):
					# 	continue

					if (('不可取消' in policy) and ('免费取消' in entry['GTA_Policy'])) or ( ('免费取消' in policy) and ('不可取消' in entry['GTA_Policy']) ) :
						continue

					entry['Ctrip_room_name_' + str(entry['count'])] = room_name

					entry['Ctrip_room_description_' + str(entry['count'])] = rp.find_element_by_css_selector('.hroom_roomname.J_rooms_name').text or ''

					# entry['RP_id'] = book_btn.get_attribute('id').rstrip().split('_')[2]
					entry['Ctrip_Bed_' + str(entry['count'])] = rp.find_element_by_css_selector('.hroom_col.hroom_col_bed.J_facilitiesInfoLogo').text or ''
					
					entry['Ctrip_guest_#_' + str(entry['count'])] = n_guest

					entry['ctrip_Breakfast_' + str(entry['count'])] = breakfast
					# entry['ctrip_Breakfast_' + str(entry['count'])] = rp.find_element_by_css_selector('.abbr.J_facilitiesInfoLogo').text
					entry['ctrip_Policy_' + str(entry['count'])] = policy
					# entry['ctrip_Policy_' + str(entry['count'])] = ''.join(rp.find_element_by_css_selector('.abbr.J_cancelBookingLogo').text.split())
					entry['ctrip_lowest_Price_' + str(entry['count'])] = re.sub('[^0-9]', '', rp.find_element_by_css_selector('.txt_taxtips').text)

					gta_price = float(entry['GTA_Price(on ctrip)'])
					ctrip_price = float(entry['ctrip_lowest_Price_' + str(entry['count'])]) 

					entry['diff_percentage_' + str(entry['count'])] = float('{0:.3f}'.format(float( (ctrip_price - gta_price) / gta_price)))
					entry['count'] += 1

					# res.append(entry)
				except StaleElementReferenceException:
					pp.pprint("Error: Elem became stale... fffffffff...")
				except ValueError:
					pp.pprint("Error: Value error when converting to float... fffffffff...")


				break

		for key, value in entry_dict.items():
			res.append(entry_dict[key])
		# res.append(entry)

	driver.quit()

	# pp.pprint(res)
	if not res:
		pprint.pprint("List is empty! No price found for every hotel in the file!")
		return

	keys_max = None
	k_max = 0
	for ent in res:
		if len(ent.keys()) > k_max:
			keys_max = ent.keys()
			k_max = len(ent.keys())

	# keys = res[0].keys()
	with open('output_Ctripplus_' + datetime.datetime.now().strftime('%y%m%d_%H%M') + '_' + str(days) + 'days.csv', 'w', encoding='utf-8') as output_file:
		# dict_writer = csv.DictWriter(output_file, keys)
		dict_writer = csv.DictWriter(output_file, keys_max)
		dict_writer.writeheader()
		dict_writer.writerows(res)

if __name__ == '__main__':
	ctripplus()