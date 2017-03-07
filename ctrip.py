#!/usr/bin/env python
# coding=utf-8

import pprint
import csv
import click 
import requests
import datetime as datetime
# import logging

pp = pprint

def validate_d(date_text):
	try:
		datetime.datetime.strptime(date_text, '%Y-%m-%d')
	except ValueError:
		raise ValueError("Incorrect data format, should be YYYY-MM-DD")

res = []

@click.command()
@click.option('--hotel', default=996727, type=int)
@click.option('--ci', default='2017-04-01')
@click.option('--co', default='2017-04-02')
def ctrip(hotel, ci, co):
	# logging.basicConfig(level=logging.DEBUG, filename="output", filemode="w+", format="%(message)s")
	validate_d(ci)
	validate_d(co)
	payload = {'hotel': hotel, 
				'EDM': 'F',
				'urlReferedForOtherSeo': 'False',
				'Pkg': 'F',
				# 'StartDate': '2017-03-10',
				'StartDate': ci,
				# 'DepDate': '2017-03-11',
				'DepDate': co,
				'RoomNum': '2',
				'IsNoLocalRoomHotel': 'T',
				# 'UserUnicode': '',
				'requestTravelMoney': 'F',
				'abt': 'B',
				# 'promotionid': '',
				't': '1488787388256',
				'childNum': '2',
				'FixSubHotel': 'F',
				# 'allianceid': '',
				# 'sid': '',
				# 'userCouponPromoId': '',
				# 'Coupons': '',
				'isNeedAddInfo': 'true',
				'PageLoad': 'false',
				}

	r = requests.get('http://hotels.ctrip.com/international/Tool/AjaxHotelRoomInfoDetailPart.aspx', params=payload)

	# pp.pprint(r.text)
	r_json = r.json()
	# pp.pprint(r.json())
	hotel_name = r_json['HotelRoomData']['name']

	for rp in r_json['HotelRoomData']['subRoomList']:
		room_name = None
		for room in r_json['HotelRoomData']['roomList']:
			if rp['baseRoomId'] == room['id']:
				room_name = room['name']
		entry = dict([
						('Hotel_id', hotel),
						('Hotel_name', hotel_name),
						('Room_Name', room_name), 
						('Room_id', rp['id']),
						('RP_Name', rp['roomTitle']),
						('Bed', rp['bed']),
						('Breakfast', rp['breakfast']),
						('Policy', rp['policyInfo']['title']),
						('Check_in', ci),
						('Check_out', co),
						('Price', rp['price']['TotalPrice']),
						])
		res.append(entry)
	pp.pprint('/// /// /// Result /// /// ///')
	pp.pprint(res)
	# logging.info(res)

	keys = res[0].keys()
	with open('output.csv', 'w') as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		dict_writer.writeheader()
		dict_writer.writerows(res)
	

if __name__ == '__main__':
	ctrip()