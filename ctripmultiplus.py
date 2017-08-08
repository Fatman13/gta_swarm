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
@click.option('--days', default=10, type=int)
@click.option('--span', default=5, type=int)
# @click.option('--duration', default=3, type=int)
# @click.option('--days', default=1, type=int)
def ctripmultiplus(days, span):

	start_days = days
	for i in range(span):
		subprocess.call(['python', 'ctripplus.py', '--days', str(start_days + i*10)])

		for i in range(3):
			print('sleeping..')
			time.sleep(1)

	# newest = max(glob.iglob('output_Search_item_hr_*.csv'), key=os.path.getctime)
	# subprocess.call(['python', 'sendmail.py', '--filename', 'output_hotel_ref_*.csv', '--title', 'Ctrip_hotel_ref'])


if __name__ == '__main__':
	ctripmultiplus()