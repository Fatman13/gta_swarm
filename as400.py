#!/usr/bin/env python
# coding=utf-8

import pprint
import click
import pyodbc
import os
import json
import datetime
import csv

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

def dump_csv(res, filename):
	keys = res[0].keys()
	with open(filename + datetime.datetime.now().strftime('_%y%m%d_%H%M') + '.csv', 'w', newline='', encoding='utf-8') as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		# dict_writer = csv.DictWriter(output_file, field_names)
		dict_writer.writeheader()
		dict_writer.writerows(res)

clients = { 'Qunar': '5840, 5576, 5673',
			'Ctrip': '5867, 5966',
			'Haoqiao': '5549, 5682', 
			'Dida': '5162, 5406',
			'Hotel_Travel_17': '7598, 7182, 7793',
			'Hotel_Travel_28': '1123' }

@click.command()
# @click.option('--country', default='Canada')
@click.option('--client', default='Ctrip')
@click.option('--site', default='41')
def as400(client, site):

	print('Connnecting...')
	res = []
	res_set = []

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
			"WHERE (RTSCIXP.SCIX_ACTIV = 'Y') AND (RTSCIXP.SCIX_TYPE = 'HH') AND (RTSCIXP.SCIX_TODT >= CURRENT_DATE) AND (RTSCIXP.SCIX_EXPDT >= CURRENT_DATE) AND (RTSCIXP.SCIX_STEID = '" + site + "') AND (RTSCIXP.SCIX_CLTUI In (" + clients[client] + ")) OR (RTSCIXP.SCIX_ACTIV = 'Y') AND (RTSCIXP.SCIX_TYPE = 'HH') AND (RTSCIXP.SCIX_TODT >= CURRENT_DATE) AND (RTSCIXP.SCIX_EXPDT >= CURRENT_DATE) AND (RTSCIXP.SCIX_STEID = '" + site + "') AND (RTSCIXP.SCIX_CLTUI = 0) OR (RTSCIXP.SCIX_ACTIV='Y') AND (RTSCIXP.SCIX_TYPE='HH') AND (RTSCIXP.SCIX_TODT>=CURRENT_DATE) AND (RTSCIXP.SCIX_EXPDT>=CURRENT_DATE) AND (RTSCIXP.SCIX_STEID=' ') " + \
			"ORDER BY RTSCIXP.SCIX_STEID, RTSCIXP.SCIX_CLTUI, RTSCIXP.SCIX_INEX, RTSCIXP.SCIX_ZONE, RTSCIXP.SCIX_CNT, RTSCIXP.SCIX_CTY, RTSCIXP.SCIX_ITEM, RTSCIXP.SCIX_SETUI"

	# c1.execute('select * from qsys2.sysschemas')
	c1.execute(query)

	print('Fetching... ' + client)

	columns = [column[0] for column in c1.description]
	print(columns)

	for row in c1.fetchall():
		res.append(dict(zip(columns, row)))

	dump_csv(res, 'output_as400_exclu')

	exclu_set = set()
	for ent in res:
		if ent['SCIX_SETUI'] != None and ent['SCIX_SETUI'] != 0:
			exclu_set.add(ent['SCIX_SETUI'])

	query_set = "SELECT RTIXSDP.IXSD_SETUI, RTIXSDP.IXSD_TYPE, RTIXSDP.IXSD_ZONE, RTIXSDP.IXSD_CNT, RTIXSDP.IXSD_CTY, RTIXSDP.IXSD_ITEM, " + \
				"RTIXSDP.IXSD_FRMDT, RTIXSDP.IXSD_TODT, RTIXSDP.IXSD_EFFDT, RTIXSDP.IXSD_EXPDT, RTIXSDP.IXSD_INEX " + \
				"FROM RTSHRDTA.RTIXSDP RTIXSDP " + \
				"WHERE (RTIXSDP.IXSD_ACTIV='Y') AND (RTIXSDP.IXSD_EXPDT>=CURRENT_DATE) AND " + \
				"(IXSD_TODT >=CURRENT_DATE) AND  (RTIXSDP.IXSD_SETUI In (" + ",".join([ str(id) for id in exclu_set ]) + ")) " + \
				"ORDER BY RTIXSDP.IXSD_SETUI, RTIXSDP.IXSD_ZONE, RTIXSDP.IXSD_CNT, RTIXSDP.IXSD_CTY, RTIXSDP.IXSD_ITEM"

	print('Query sets...')

	c1.execute(query_set)

	columns = [column[0] for column in c1.description]
	print(columns)

	for row in c1.fetchall():
		res_set.append(dict(zip(columns, row)))

	dump_csv(res_set, 'output_as400_exclu_sets')
	

if __name__ == '__main__':
	as400()