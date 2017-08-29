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
import csv

def getcdate(filename):
	return datetime.datetime.fromtimestamp(os.path.getctime(filename)).date()

CONFIRMED = 'Confirmed or Completed'

@click.command()
@click.option('--days', default=-5, type=int)
# @click.option('--days', default=1, type=int)
def ctripref_stats(days):

	from_date = datetime.datetime.today().date() + datetime.timedelta(days=days)
	list1 = [ ent for ent in glob.iglob('output_Search_booking_id_*.csv') if from_date <= getcdate(ent)]
	print('List1: ' + str(list1))
	list2 = [ ent for ent in glob.iglob('output_ctrip_update_res_no_*.csv') if from_date <= getcdate(ent)]
	print('List2: ' + str(list2))

	filename2_dict = {}
	for filename2 in list2:
		try:
			filename2_date = re.search('output_ctrip_update_res_no_(\d+)', filename2).group(1)
		except AttributeError:
			filename2_date = ''
		filename2_dict[filename2_date] = filename2

	res = []

	for filename1 in list1:
		entry = {}

		try:
			filename1_date = re.search('output_Search_booking_id_(\d+)', filename1).group(1)
		except AttributeError:
			filename1_date = ''
		if filename1_date != '':			
			entry['date'] = filename1_date
		entry['booking_file'] = filename1

		try:
			print(filename2_dict[filename1_date])
		except KeyError:
			print('Warning: expected date is not in the dictionary..')
			continue
		entry['ctrip_api_file'] = filename2_dict[filename1_date]
		res.append(entry)

	for ent in res:
		total_booking_num = 0
		ctrip_booking_num = 0
		with open(ent['booking_file'], encoding='utf-8-sig') as csvfile:
			reader = csv.DictReader(csvfile)
			ids = set()
			for row in reader:
				if row['gta_api_booking_id'] not in ids:
					if row['booking_status'] == CONFIRMED:
						total_booking_num = total_booking_num + 1
				ids.add(row['gta_api_booking_id'])	
		with open(ent['ctrip_api_file'], encoding='utf-8-sig') as csvfile:
			reader = csv.DictReader(csvfile)
			for row in reader:
				ctrip_booking_num = ctrip_booking_num + 1
		ent['booking_hotel_ref_percentage'] = '{0:.3f}'.format(float( ctrip_booking_num / total_booking_num ))

	keys = res[0].keys()
	with open('output_hotel_ref_stats_' + datetime.datetime.now().strftime('%y%m%d_%H%M') + '.csv', 'w', newline='', encoding='utf-8') as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		dict_writer.writeheader()
		dict_writer.writerows(res)

	# # python booking_id.py --days 0 --duration 0 --client ctrip --d_type departure
	# subprocess.call(['python', 'booking_id.py', '--days', str(days), '--duration', str(duration), '--client', 'ctrip', '--d_type', 'departure'])

	# for i in range(3):
	# 	print('sleeping..')
	# 	time.sleep(1)

	# newest = max(glob.iglob('output_Search_booking_id_*.csv'), key=os.path.getctime)
	# subprocess.call(['python', 'search_item_hr.py', '--filename', newest])

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

	# # while True:
	# # 	sys.stdout.write("Would you like to proceed to call Ctrip's update hotel res no API? " + newest + " [Y/N]")
	# # 	choice = input().lower()
	# # 	if choice == 'y' or choice == 'yes':
	# # 		break
	# # 	if choice == 'n' or choice == 'no':
	# # 		return

	# subprocess.call(['python', 'ctrip_update_res_no.py', '--filename', newest])


if __name__ == '__main__':
	ctripref_stats()