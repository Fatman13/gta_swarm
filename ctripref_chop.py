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
import re

def is_bad_date(filename_regex, newest):
	today_date = datetime.datetime.now().strftime('%y%m%d')
	try:
		newest_date = re.search(filename_regex, newest).group(1)
	except AttributeError:
		newest_date = ''
	if newest_date != today_date:
		print('Error: newest date != today date.. mannual intervention needed..')
		return True
	print('newest date: ' + newest_date)
	return False

def is_bad_date_re(filename_regex, newest):
	today_date = datetime.datetime.now().date()
	try:
		newest_date = re.search(filename_regex, newest).group(1)
	except AttributeError:
		newest_date = ''
	try:
		newest_date = datetime.datetime.strptime(newest_date , '%y%m%d').date()
	except ValueError:
		print('Error: Unable to convert date')
		return True
	if newest_date < today_date:
		print('Error: newest date < today date.. mannual intervention needed..')
		return True
	print('newest date: ' + str(newest_date))
	return False

# hua shi shui jiao
def hua_style_sleep():
	for i in range(3):
		print('sleeping..' + str(i))
		time.sleep(1)

@click.command()
@click.option('--days', default=0, type=int)
@click.option('--duration', default=2, type=int)
# @click.option('--days', default=1, type=int)
def ctripref(days, duration):

	# subprocess.call(['python', 'booking_id_ctrip.py', '--days', str(days), '--duration', str(duration), '--d_type', 'departure'])

	# newest = max(glob.iglob('output_Search_booking_id_*.csv'), key=os.path.getctime)
	# if is_bad_date_re('output_Search_booking_id_(\d+)', newest):
	# 	print('Error: bad date.. ')
	# 	return
	# subprocess.call(['python', 'ctrip_store_booking.py', '--filename', newest, '--days', '-30', '--output', 'output_ctrip_search_booking_store.csv'])
	# subprocess.call(['python', 'search_item_hr.py', '--filename', newest])

	# hua_style_sleep()

	# newest = max(glob.iglob('output_Search_item_hr_*.csv'), key=os.path.getctime)
	# if is_bad_date_re('output_Search_item_hr_(\d+)', newest):
	# 	print('Error: bad date.. ')
	# 	return
	# subprocess.call(['python', 'hc.py', '--filename', newest])

	# hua_style_sleep()

	newest = max(glob.iglob('output_hotel_ref_*.csv'), key=os.path.getctime)
	if is_bad_date_re('output_hotel_ref_(\d+)', newest):
		print('Error: bad date.. ')
		return

	subprocess.call(['python', 'ctrip_update_res_no.py', '--filename', newest])

	# keep track of bookings that has been pushed
	newest = max(glob.iglob('output_ctrip_update_res_no_*.csv'), key=os.path.getctime)
	if is_bad_date_re('output_ctrip_update_res_no_(\d+)', newest):
		print('Error: bad date.. ')
		return
	subprocess.call(['python', 'ctrip_store_booking.py', '--filename', newest, '--days', '-30', '--output', 'output_ctrip_booking_store.csv'])

	subprocess.call(['python', 'sendmail_win_cs.py', 
						'--filename', 'output_hotel_ref_', 
						'--email', 'no-reply@gta-travel.com'])

if __name__ == '__main__':
	ctripref()