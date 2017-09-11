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
		return False
	print('newest date: ' + newest_date)
	return True

def hua_style_sleep():
	for i in range(3):
		print('sleeping..' + str(i))
		time.sleep(1)

@click.command()
@click.option('--days', default=0, type=int)
@click.option('--duration', default=0, type=int)
# @click.option('--days', default=1, type=int)
def ctripref(days, duration):

	subprocess.call(['python', 'booking_id_ctrip.py', '--days', str(days), '--duration', str(duration), '--d_type', 'departure'])

	newest = max(glob.iglob('output_Search_booking_id_*.csv'), key=os.path.getctime)
	if is_bad_date('output_Search_booking_id_(\d+)', newest):
		print('Error: bad date.. ')
		return
	subprocess.call(['python', 'search_item_hr.py', '--filename', newest])

	hua_style_sleep()

	newest = max(glob.iglob('output_Search_item_hr_*.csv'), key=os.path.getctime)
	if is_bad_date('output_Search_item_hr_(\d+)', newest):
		print('Error: bad date.. ')
		return
	subprocess.call(['python', 'hc.py', '--filename', newest])

	hua_style_sleep()

	# newest = max(glob.iglob('output_Search_item_hr_*.csv'), key=os.path.getctime)
	# subprocess.call(['python', 'sendmail.py', '--filename', 'output_hotel_ref_*.csv', '--title', 'Ctrip_hotel_ref'])

	newest = max(glob.iglob('output_hotel_ref_*.csv'), key=os.path.getctime)

	if is_bad_date('output_hotel_ref_(\d+)', newest):
		print('Error: bad date.. ')
		return

	# while True:
	# 	sys.stdout.write("Would you like to proceed to call Ctrip's update hotel res no API? " + newest + " [Y/N]")
	# 	choice = input().lower()
	# 	if choice == 'y' or choice == 'yes':
	# 		break
	# 	if choice == 'n' or choice == 'no':
	# 		return

	subprocess.call(['python', 'ctrip_update_res_no.py', '--filename', newest])

if __name__ == '__main__':
	ctripref()