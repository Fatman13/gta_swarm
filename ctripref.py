#!/usr/bin/env python
# coding=utf-8

import pprint
import csv
import click 
import requests
import datetime as datetime
from datetime import date
from xml.etree import ElementTree as ET
import os
# from random import sample
import random
import json
# import logging
import subprocess
import glob
import time

@click.command()
@click.option('--days', default=0, type=int)
@click.option('--duration', default=3, type=int)
# @click.option('--days', default=1, type=int)
def ctripref(days, duration):

	subprocess.call(['python', 'booking_id.py', '--days', str(days), '--duration', str(duration)])

	for i in range(3):
		print('sleeping..')
		time.sleep(1)

	newest = max(glob.iglob('output_Search_booking_id_*.csv'), key=os.path.getctime)
	subprocess.call(['python', 'search_item_hr.py', '--filename', newest])

	for i in range(3):
		print('sleeping..')
		time.sleep(1)

	newest = max(glob.iglob('output_Search_item_hr_*.csv'), key=os.path.getctime)
	subprocess.call(['python', 'hc.py', '--filename', newest])

	for i in range(3):
		print('sleeping..')
		time.sleep(1)

	# newest = max(glob.iglob('output_Search_item_hr_*.csv'), key=os.path.getctime)
	subprocess.call(['python', 'sendmail.py', '--filename', 'output_hotel_ref_*.csv', '--title', 'Ctrip_hotel_ref'])


if __name__ == '__main__':
	ctripref()