#!/usr/bin/env python

import pprint
import os
import uuid
from xml.etree import ElementTree as ET
import requests
import datetime as datetime

# url of rbs API
url = 'https://interface.demo.gta-travel.com/rbshkapi/RequestListenerServlet'
# number of add and cancel booking pair to be run; cannot be zero
counter = 10 

Ids = []
trees = []
num_add_suc = 0
num_cancel_suc = 0
add_r_deltas = cancel_r_deltas = []
add_r_max_delta = cancel_r_max_delta = datetime.timedelta.min
add_r_min_delta = cancel_r_min_delta = datetime.timedelta.max

pp = pprint.PrettyPrinter(indent=4)

pp.pprint(str('/// /// /// Start Swarming /// /// ///'))
pp.pprint('Current WD path: ' + os.getcwd())

if counter <= 0:
	pp.pprint("Error: counter less than zero...")

# datafile = None
# with open(os.path.join(os.getcwd(), 'AddBookingRequest.xml'), 'r') as f:
# 	datafile = f.read()

# pp.pprint(datafile)

add_tree = ET.parse(os.path.join(os.getcwd(), 'AddBookingRequest.xml'))
cancel_tree = ET.parse(os.path.join(os.getcwd(), 'CancelBookingRequest.xml'))
search_tree = ET.parse(os.path.join(os.getcwd(), 'SearchHotelPriceRequest.xml'))

checkin_date = search_tree.find('.//CheckInDate').text
search_tree.find('.//NumberOfReturnedItems').text = str(counter)
credentials = dict([('client', search_tree.find('.//RequestorID').get('Client')), 
	('email_address', search_tree.find('.//RequestorID').get('EMailAddress')), 
	('password', search_tree.find('.//RequestorID').get('Password'))])

preferences = dict([('country', search_tree.find('.//RequestorPreferences').get('Country')), 
	('currency', search_tree.find('.//RequestorPreferences').get('Currency')), 
	('language', search_tree.find('.//RequestorPreferences').get('Language'))])

trees.append(add_tree)
trees.append(cancel_tree)

for tree in trees:
	tree.find('.//RequestorID').set('Client', credentials['client'])
	tree.find('.//RequestorID').set('EMailAddress', credentials['email_address'])
	tree.find('.//RequestorID').set('Password', credentials['password'])
	tree.find('.//RequestorPreferences').set('Country', preferences['country'])
	tree.find('.//RequestorPreferences').set('Currency', preferences['currency'])
	tree.find('.//RequestorPreferences').set('Language', preferences['language'])

pp.pprint('Passenger checkin_date: ' + checkin_date)

pp.pprint('////// Search Hotel Price Request ////// ')

r = requests.post(url, data=ET.tostring(search_tree.getroot(), encoding='UTF-8', method='xml'))

search_r_tree = ET.fromstring(r.text)
pp.pprint('////// Getting Ids from Search Hotel Price Response ////// ')

for hotel in search_r_tree.find('.//HotelDetails'):
	city_code = hotel.find('.//City').get('Code')
	item_code = hotel.find('.//Item').get('Code')
	for room_category in hotel.find('.//RoomCategories'):
		# Ids.append(room_category.get('Id'))
		Ids.append(dict([('Id', room_category.get('Id')), ('cityCode', city_code), ('itemCode', item_code)]))

pp.pprint('list of Ids (' + str(len(Ids)) + '): ' + ''.join(str(d) for d in Ids))

if len(Ids) < counter:
	pp.pprint("Error: length of Ids is less than counter...")

for i in range(counter):
	book_ref = str(uuid.uuid4())[:20];

	pp.pprint(str(i) + ' Random Booking Reference: ' + str(book_ref))
	add_tree.find('.//BookingReference').text = book_ref
	# to be changed
	add_tree.find('.//BookingDepartureDate').text = checkin_date
	add_tree.find('.//CheckInDate').text = checkin_date
	# set booking details dict
	item_info = Ids.pop()
	add_tree.find('.//HotelRoom').set('Id', item_info['Id'])
	add_tree.find('.//ItemCity').set('Code', item_info['cityCode'])
	add_tree.find('.//Item').set('Code', item_info['itemCode'])

	cancel_tree.find('.//BookingReference').text = book_ref
	# add_tree.write('test1.xml')
	# cancel_tree.write('test2.xml')
	# add_tree.
	# ET.tostring(element, encoding, method)
	# pp.pprint(ET.tostring(add_tree.getroot(), encoding='utf8', method='xml'))
	# root = add_tree.getroot()
	# xmlstr = ET.tostring(root)
	# pprint(xmlstr)

	r = requests.post(url, data=ET.tostring(add_tree.getroot(), encoding='UTF-8', method='xml'))
	# r.text
	pp.pprint('////// Add Booking Response ////// ' + str(i))
	if r.status_code == 200:
		num_add_suc += 1

	pp.pprint('Add Booking Response status code: ' + str(r.status_code))
	pp.pprint(r.headers)
	pp.pprint('Add Booking Response body: ' + r.text)
	if r.elapsed < add_r_min_delta:
		add_r_min_delta = r.elapsed
	if r.elapsed > add_r_max_delta:
		add_r_max_delta = r.elapsed
	add_r_deltas.append(r.elapsed)
	pp.pprint('Response time: ' + str(r.elapsed))


	r = requests.post(url, data=ET.tostring(cancel_tree.getroot(), encoding='UTF-8', method='xml'))
	pp.pprint('////// Cancel Booking Response ////// ' + str(i))
	if r.status_code == 200:
		num_cancel_suc += 1
	pp.pprint('Cancel Booking Response status code: ' + str(r.status_code))
	pp.pprint(r.headers)
	pp.pprint('Cancel Booking Response body: ' + r.text)
	if r.elapsed < cancel_r_min_delta:
		cancel_r_min_delta = r.elapsed
	if r.elapsed > cancel_r_max_delta:
		cancel_r_max_delta = r.elapsed
	cancel_r_deltas.append(r.elapsed)
	pp.pprint('Response time: ' + str(r.elapsed))


pp.pprint('/// /// /// Test Result /// /// ///')
pp.pprint(str(num_add_suc) + ' out of ' + str(counter) + ' AddBookingrequest got HTTP 200')
pp.pprint(str(num_cancel_suc) + ' out of ' + str(counter) + ' CancelBookingrequest got HTTP 200')
pp.pprint('AddBookingrequest min: ' + str(add_r_min_delta) + ' max: ' + str(add_r_max_delta) + ' average: ' + str(sum(add_r_deltas, datetime.timedelta(0)) / len(add_r_deltas)))
pp.pprint('CancelBookingrequest min: ' + str(cancel_r_min_delta) + ' max: ' + str(cancel_r_max_delta) + ' average: ' + str(sum(cancel_r_deltas, datetime.timedelta(0)) / len(cancel_r_deltas)))