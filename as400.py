#!/usr/bin/env python
# coding=utf-8

import pprint
import click
import pyodbc
import os
import json

as400_secret = None
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secrets.json')) as data_file:    
	as400_secret = (json.load(data_file))['as400']

def validate_d(date_text):
	try:
		datetime.datetime.strptime(date_text, '%Y-%m-%d')
	except ValueError:
		raise ValueError("Incorrect data format, should be YYYY-MM-DD")

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)

clients = { 'Qunar': '5840, 5576, 5673',
			'Ctrip': '5867, 5966',
			'Haoqiao': '5549, 5682', 
			'Dida': '5162, 5406' }

@click.command()
# @click.option('--country', default='Canada')
def as400():

	print('Connnecting...')

	connection = pyodbc.connect(
    	driver='{iSeries Access ODBC Driver}',
    	system='10.241.163.148',
    	uid=as400_secret['uid'],
    	pwd=as400_secret['pwd'])
	c1 = connection.cursor()

	print('Connnected.')

	query = "SELECT RTSCIXP.SCIX_INEX, RTSCIXP.SCIX_STEID, RTSCIXP.SCIX_CLTUI, RTSCIXP.SCIX_TYPE, RTSCIXP.SCIX_ZONE, RTSCIXP.SCIX_CNT, RTSCIXP.SCIX_CTY, RTSCIXP.SCIX_ITEM, " + \
			"RTSCIXP.SCIX_FRMDT, RTSCIXP.SCIX_TODT, " + \
			"RTSCIXP.SCIX_EFFDT, RTSCIXP.SCIX_EXPDT, " + \
			"RTSCIXP.SCIX_SETUI " + \
			"FROM RTSHRDTA.RTSCIXP RTSCIXP " + \
			"WHERE (RTSCIXP.SCIX_ACTIV = 'Y') AND (RTSCIXP.SCIX_TYPE = 'HH') AND (RTSCIXP.SCIX_TODT >= CURRENT_DATE) AND (RTSCIXP.SCIX_EXPDT >= CURRENT_DATE) AND (RTSCIXP.SCIX_STEID = '041') AND (RTSCIXP.SCIX_CLTUI In (5840, 5576, 5673)) OR (RTSCIXP.SCIX_ACTIV = 'Y') AND (RTSCIXP.SCIX_TYPE = 'HH') AND (RTSCIXP.SCIX_TODT >= CURRENT_DATE) AND (RTSCIXP.SCIX_EXPDT >= CURRENT_DATE) AND (RTSCIXP.SCIX_STEID = '041') AND (RTSCIXP.SCIX_CLTUI = 0) OR (RTSCIXP.SCIX_ACTIV='Y') AND (RTSCIXP.SCIX_TYPE='HH') AND (RTSCIXP.SCIX_TODT>=CURRENT_DATE) AND (RTSCIXP.SCIX_EXPDT>=CURRENT_DATE) AND (RTSCIXP.SCIX_STEID=' ') " + \
			"ORDER BY RTSCIXP.SCIX_STEID, RTSCIXP.SCIX_CLTUI, RTSCIXP.SCIX_INEX, RTSCIXP.SCIX_ZONE, RTSCIXP.SCIX_CNT, RTSCIXP.SCIX_CTY, RTSCIXP.SCIX_ITEM, RTSCIXP.SCIX_SETUI"

	# c1.execute('select * from qsys2.sysschemas')
	c1.execute(query)

	for row in c1:
		print(row)
	
if __name__ == '__main__':
	as400()