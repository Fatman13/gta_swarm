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
import random

def validate_d(date_text):
	try:
		datetime.datetime.strptime(date_text, '%Y-%m-%d')
	except ValueError:
		raise ValueError("Incorrect data format, should be YYYY-MM-DD")

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)

@click.command()
@click.option('--from_d', default='2017-03-25')
@click.option('--to_d', default='2017-04-25')
def ds(from_d, to_d):

	url = 'https://rbs.gta-travel.com/rbscnapi/RequestListenerServlet'
	pp = pprint
	res = []

	validate_d(from_d)
	validate_d(to_d)

	from_date = datetime.datetime.strptime(from_d, '%Y-%m-%d').date()
	to_date = datetime.datetime.strptime(to_d, '%Y-%m-%d').date()

	pp.pprint('Test Test Test..')

	with open('Germany2.14.csv', encoding='utf-8-sig') as csvfile:
		reader = csv.DictReader(csvfile, delimiter=',')

		for row in reader:
			pprint.pprint(row)
	

if __name__ == '__main__':
	ds()