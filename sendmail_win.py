#!/usr/bin/env python
# coding=utf-8

# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# # from email.MIMEText import MIMEText
# from email.mime.base import MIMEBase
# # from email.MIMEBase import MIMEBase
# from email import encoders
import glob
import click
import os
import json
import datetime
import re
import csv
from requests.exceptions import ConnectionError

from exchangelib import DELEGATE, IMPERSONATION, Account, Credentials, ServiceAccount, \
    EWSDateTime, EWSTimeZone, Configuration, NTLM, CalendarItem, Message, \
    Mailbox, Attendee, Q, ExtendedProperty, FileAttachment, ItemAttachment, \
    HTMLBody, Build, Version
 
# filename = "output_Ctripplus_170614_1827_japan.xlsx"
sendmail_secret = None
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secrets.json')) as data_file:    
	sendmail_secret = (json.load(data_file))['sendmail_win']

TO_REGISTER = 'Confirmed (to register)'

@click.command()
@click.option('--filename', default='output_hotel_ref_*.csv')
@click.option('--email', default='no-reply@gta-travel.com')
# @click.option('--email', default='yu.leng@gta-travel.com')
# @click.option('--duration', default=3, type=int)
# @click.option('--days', default=1, type=int)
def sendmail(filename, email):

	# today_date = datetime.datetime.today().date()
	newest = max(glob.iglob('output_hotel_ref_*.csv'), key=os.path.getctime)
	today_date = datetime.datetime.now().strftime('%y%m%d')
	try:
		newest_date = re.search('output_hotel_ref_(\d+)', newest).group(1)
	except AttributeError:
		newest_date = ''
	if newest_date != today_date:
		print('Error: newest date != today date.. mannual intervention needed..')
		return

	print('newest date: ' + newest_date)

	bookings = []
	res = []
	# filename = 'gtaConfirmRefs_5867_2017-06-30_2017-07-07.csv'
	with open(newest, encoding='utf-8-sig') as csvfile:
		ids = set()
		reader = csv.DictReader(csvfile)
		for row in reader:
			# pp.pprint(row['hotel_id'])
			if row['gta_api_booking_id'] not in ids:
				entry = dict()
				entry['client_booking_id'] = row['client_booking_id']
				entry['agent_booking_id'] = row['agent_booking_id']
				entry['gta_api_booking_id'] = row['gta_api_booking_id']
				entry['booking_status'] = row['booking_status']
				entry['booking_creation_date'] = row['booking_creation_date']
				entry['booking_departure_date'] = row['booking_departure_date']
				entry['booking_name'] = row['booking_name']
				entry['booking_net_price'] = row['booking_net_price']
				entry['booking_currency'] = row['booking_currency']
				entry['hotel_confirmation_#'] = ''
				entry['hotel_confirmation_status'] = ''
				if 'hotel_confirmation_#' in row:
					entry['hotel_confirmation_#'] = row['hotel_confirmation_#']
				if 'hotel_confirmation_status' in row:
					entry['hotel_confirmation_status'] = row['hotel_confirmation_status']
				# hotel email
				entry['hotel_email'] = ''
				if 'hotel_email' in row:
					entry['hotel_email'] = row['hotel_email']
				bookings.append(entry)
			ids.add(row['gta_api_booking_id'])

	print('Setting account..')
	# Username in WINDOMAIN\username format. Office365 wants usernames in PrimarySMTPAddress
	# ('myusername@example.com') format. UPN format is also supported.
	credentials = Credentials(username='APACNB\\809452', password=sendmail_secret['password'])
	# credentials = ServiceAccount(username='APACNB\\809452', password=sendmail_secret['password'])

	print('Discovering..')

	# If the server doesn't support autodiscover, use a Configuration object to set the server
	# location:
	# config = Configuration(server='outlookuk.kuoni.int', credentials=credentials)
	config = Configuration(server='emailuk.kuoni.com', credentials=credentials)

	try:
		account = Account(primary_smtp_address=email, config=config,
					autodiscover=False, access_type=DELEGATE)
		# account = Account(primary_smtp_address=email, config=config,
		# 			autodiscover=False, access_type=IMPERSONATION)
	except ConnectionError as e:
		print('Fatal: Connection Error.. aborted..')
		return

	# Set up a target account and do an autodiscover lookup to find the target EWS endpoint:
	# account = Account(primary_smtp_address='yu.leng@gta-travel.com', credentials=credentials,
				#autodiscover=True, access_type=DELEGATE)

	print('Logged in as: ' + str(email))

	for counter, booking in enumerate(bookings):
		print('Reminder email id: ' + str(counter) + ': ' + str(booking['gta_api_booking_id']))

		if booking['hotel_email'] == None or booking['hotel_email'] == '':
			print('No hotel email.. skipping.. ')
			continue

		if booking['hotel_confirmation_status'] != TO_REGISTER:
			print('Not to register status.. skipping')
			continue

		if booking['hotel_confirmation_#'] != None and booking['hotel_confirmation_#'] != '':
			print('Have confirmation number.. skipping')
			continue

		recipient_email = booking['hotel_email']
		body_text = 'Dear supplier, \n\n' + \
			'This is a reminder that you haven’t registered hotel confirmation number with GTA for the following item: \n\n' + \
			'GTA booking id: ' + str(booking['gta_api_booking_id']) + '\n\n' + \
			'Please kindly login to https://hotels.gta-travel.com/gcres/auth/securelogin to register hotel confirmation number in our system. Thank you!\n\n' + \
			'Best regards,\n' + \
			'-GTA Travel\n' + \
			'p.s. Please do not reply this email.'
		title_text = '[Reminder] Please register confirmation number with GTA'

		# Or, if you want a copy in e.g. the 'Sent' folder
		m = Message(
			account=account,
			folder=account.sent,
			sender=Mailbox(email_address=email),
			author=Mailbox(email_address=email),
			subject=title_text,
			body=body_text,
			to_recipients=[Mailbox(email_address=recipient_email)]
			)
		m.send_and_save()

		print('Message sent to ... ... ' + str(booking['hotel_email']))

	# fromaddr = "tctctcly@gmail.com"
	# # toaddr = "yu.leng@gta-travel.com, l"
	# recipients = ['yu.leng@gta-travel.com', 'lily.yu@gta-travel.com', 'yun.liu@gta-travel.com']

	# # msg = MIMEMultipart()
	 
	# # msg['From'] = fromaddr
	# # # msg['To'] = toaddr
	# # msg['To'] = ", ".join(recipients)
	# # msg['Subject'] = title + '_' + today_date.strftime('%m%d')
	 
	# # # body = "FYI\n\nThis email is auto generated by yu.leng@gta-travel.com."
	# # body = "This email is auto generated by yu.leng@gta-travel.com."
	 
	# # msg.attach(MIMEText(body, 'plain'))

	# # newest = max(glob.iglob(filename), key=os.path.getctime)
	# # attachment = open(newest, "rb")

	# # part = MIMEBase('application', 'octet-stream')
	# # part.set_payload((attachment).read())
	# # encoders.encode_base64(part)
	# # part.add_header('Content-Disposition', "attachment; filename= %s" % newest)
	 
	# # msg.attach(part)
	 
	# # server = smtplib.SMTP('smtp.gmail.com', 587)
	# # server.starttls()
	# # server.login(fromaddr, sendmail_secret['password'])
	# # text = msg.as_string()
	# # server.sendmail(fromaddr, recipients, text)
	# # server.quit()

if __name__ == '__main__':
	sendmail()