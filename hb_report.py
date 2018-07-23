#!/usr/bin/env python
# coding=utf-8

import pprint
import click 
import os
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
def hb_report():

	subprocess.call(['python', 'sendmail_win_hb.py', '--days', '-1'])

	hua_style_sleep()

	newest = max(glob.iglob('CTRIP---API-Errors---API-valuation-step-issues*.csv'), key=os.path.getctime)
	print('Using.. ' + newest)

	subprocess.call(['python', 'hb_er.py', '--filename', newest])
	# subprocess.call(['python', 'search_item_hr.py', '--filename', newest])

	hua_style_sleep()
	subprocess.call(['python', 'sendmail_win_hb2.py'])

if __name__ == '__main__':
	hb_report()