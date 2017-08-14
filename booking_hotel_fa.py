#!/usr/bin/env python
# coding=utf-8

import pprint
# import csv
import click 
# import requests
# import datetime as datetime
# from datetime import date
# from xml.etree import ElementTree as ET
import os
# from random import sample
# import random
# import json
# import logging
import subprocess
import glob
import time
import sys
import datetime
import csv

@click.command()
# @click.option('--page', default=1, type=int)
# @click.option('--url', default='https://www.booking.com/searchresults.html?aid=304142&label=gen173nr-1FCAEoggJCAlhYSDNiBW5vcmVmaDGIAQGYATK4AQbIAQ_YAQHoAQH4AQuSAgF5qAID&sid=c24f665d504aac0a9c235ce5f00da065&checkin_month=11&checkin_monthday=13&checkin_year=2017&checkout_month=11&checkout_monthday=14&checkout_year=2017&class_interval=1&group_adults=2&group_children=0&label_click=undef&lsf=class%7C5%7C22&nflt=ht_id%3D204%3Bclass%3D3%3Bclass%3D4%3Bclass%3D5%3B&no_rooms=1&region=5757&room1=A%2CA&sb_price_type=total&src=searchresults&ss=Pattaya&ssb=empty&ssne=Pattaya&ssne_untouched=Pattaya&track_BHKF=1&unchecked_filter=class&unchecked_filter=class&unchecked_filter=class&unchecked_filter=hoteltype&rows=15')
# @click.option('--days', default=1, type=int)
def booking_hotel_fa():

	hotels = []
	with open('booking_hotel_urls.csv', encoding='utf-8-sig') as csvfile:
		reader = csv.DictReader(csvfile)
		for row in reader:
			# pp.pprint(row['hotel_id'])
			entry = dict()
			entry['city'] = row['city']
			entry['page'] = row['page']				
			entry['url'] = row['url']				
			hotels.append(entry)

	for hotel in hotels: 
		
		if hotel['page'] == None or hotel['url'] == None:
			print('Warning: no page or url in csv..')
			continue

		# python booking_id.py --days 0 --duration 0 --client ctrip --d_type departure
		subprocess.call(['python', 'booking_href.py', '--page', str(hotel['page']), '--url', str(hotel['url'])])

		for i in range(3):
			print('sleeping..')
			time.sleep(1)

		newest = max(glob.iglob('output_booking_hotel_href*.csv'), key=os.path.getctime)
		subprocess.call(['python', 'booking.py', '--filename', newest, '--city', str(hotel['city'])])

	# for i in range(3):
	# 	print('sleeping..')
	# 	time.sleep(1)

	# newest = max(glob.iglob('output_Search_item_hr_*.csv'), key=os.path.getctime)
	# subprocess.call(['python', 'hc.py', '--filename', newest])

	# for i in range(3):
	# 	print('sleeping..')
	# 	time.sleep(1)

	# # newest = max(glob.iglob('output_Search_item_hr_*.csv'), key=os.path.getctime)
	# # subprocess.call(['python', 'sendmail.py', '--filename', 'output_hotel_ref_*.csv', '--title', 'Ctrip_hotel_ref'])

	# newest = max(glob.iglob('output_hotel_ref_*.csv'), key=os.path.getctime)

	# today_date = datetime.datetime.now().strftime('%y%m%d')
	# try:
	# 	newest_date = re.search('output_hotel_ref_(\d+)', newest).group(1)
	# except AttributeError:
	# 	newest_date = ''
	# if newest_date != today_date:
	# 	print('Error: newest date != today date.. mannual intervention needed..')
	# 	return

	# print('newest date: ' + newest_date)

	# while True:
	# 	sys.stdout.write("Would you like to proceed to call Ctrip's update hotel res no API? " + newest + " [Y/N]")
	# 	choice = input().lower()
	# 	if choice == 'y' or choice == 'yes':
	# 		break
	# 	if choice == 'n' or choice == 'no':
	# 		return

	# subprocess.call(['python', 'ctrip_update_res_no.py', '--filename', newest])


if __name__ == '__main__':
	booking_hotel_fa()