#!/usr/bin/env python
# coding=utf-8

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

from exchangelib.errors import ErrorItemNotFound

TO_REGISTER = 'Confirmed (to register)'

def dump_csv(res, output_filename, from_date):
	keys = res[0].keys()
	final_output_filename = '_'.join(['Output_sendmail', 
										output_filename, 
										from_date.strftime('%y%m%d'), 
										datetime.datetime.now().strftime('%H%M')
										]) + '.csv'
	with open(final_output_filename, 'w', newline='', encoding='utf-8') as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		dict_writer.writeheader()
		dict_writer.writerows(res)

@click.command()
@click.option('--email', default='yu.leng@gta-travel.com')
@click.option('--days', default=-1, type=int)
def sendmail_win_hb(email, days):
	# target_filename = filename + '*.csv'
	# newest = max(glob.iglob(target_filename), key=os.path.getctime)
	# print('newest file: ' + newest)
	# today_date = datetime.datetime.now().strftime('%y%m%d')
	# try:
	# 	newest_date = re.search( filename + '(\d+)', newest).group(1)
	# except AttributeError:
	# 	newest_date = ''
	# print('newest date: ' + newest_date)
	# if newest_date != today_date:
	# 	print('Error: newest date != today date.. mannual intervention needed..')
	# 	return

	try:
		sendmail_secret = None
		# with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secrets.json')) as data_file:    
		# with open(os.path.join(os.path.dirname('C:\\Users\\809452\\gta_swarm'), 'secrets.json')) as data_file:    
		with open(os.path.join('C:\\Users\\809452\\gta_swarm', 'secrets.json')) as data_file:    
			sendmail_secret = (json.load(data_file))['sendmail_win']
	except FileNotFoundError:
		print('Secret file not found..')
		return

	print('Setting account..')
	# Username in WINDOMAIN\username format. Office365 wants usernames in PrimarySMTPAddress
	# ('myusername@example.com') format. UPN format is also supported.
	credentials = Credentials(username='APACNB\\809452', password=sendmail_secret['password'])

	print('Discovering..')

	# If the server doesn't support autodiscover, use a Configuration object to set the server
	# location:
	config = Configuration(server='emailuk.kuoni.com', credentials=credentials)

	try:
		account = Account(primary_smtp_address=email, config=config,
					autodiscover=False, access_type=DELEGATE)
	except ConnectionError as e:
		print('Fatal: Connection Error.. aborted..')
		return

	print('Logged in as: ' + str(email))

	to_date = datetime.datetime.now() + datetime.timedelta(days=1)
	# from_date = to_date + datetime.timedelta(days=days)
	from_date = datetime.datetime.now() + datetime.timedelta(days=days)

	# tz = EWSTimeZone.timezone('Europe/Copenhagen')
	# tz = EWSTimeZone.timezone('Europe/London')
	tz = EWSTimeZone.timezone('Asia/Shanghai')
	# tz = EWSTimeZone.localzone()

	print('Filtering from ' + str(from_date))
	print('Filtering to ' + str(to_date))

	items_for_days = account.inbox.filter(datetime_received__range=(
		# tz.localize(EWSDateTime(2017, 1, 1)),
		tz.localize(EWSDateTime(from_date.year, from_date.month, from_date.day)),
		# tz.localize(EWSDateTime(2018, 1, 1))
		tz.localize(EWSDateTime(to_date.year, to_date.month, to_date.day))
	# )).filter(sender='no-reply@gta-travel.com')  # Filter by a date range
	# )).filter(author='no-reply@gta-travel.com')  # Filter by a date range
	))  # Filter by a date range
	# )).filter(sender='no-reply@gta-travel.com')

	if not items_for_days:
		print('items_for_days is none..')

	print('Items count: ' + str(items_for_days.count()))

	for item in items_for_days:
		# print('? Email subject: ' + item.subject)
		# print('?? Email sender: ' + str(item.sender))
		# print('??? Email date time: ' + str(item.datetime_received))
		for attachment in item.attachments:
			if isinstance(attachment, FileAttachment):
				print('- Email subject: ' + item.subject)
				print('-- Email sender: ' + str(item.sender))
				print('--- Email date time: ' + str(item.datetime_received))
				# local_path = os.path.join('/tmp', attachment.name)
				# local_path = os.path.join('', attachment.name)
				if 'CTRIP---API-Errors---API-valuation-step-issues' not in attachment.name:
					print('Warning: attachment not API report.. ')
					continue
				local_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), attachment.name)
				with open(local_path, 'wb') as f:
					try:
						f.write(attachment.content)
					except ErrorItemNotFound:
						print('Error: item not found.. ')
						continue
				print('---- Saved attachment to', local_path)

	# recipient_email = 'yu.leng@gta-travel.com'
	# recipient_email1 = 'Alex.Sha@gta-travel.com'
	# recipient_email2 = 'will.he@gta-travel.com'
	# recipient_email3 = 'Crystal.liu@gta-travel.com'
	# recipient_email4 = 'lily.yu@gta-travel.com'
	# recipient_email6 = 'intern.shanghai@gta-travel.com'
	# recipient_email5 = 'Emilie.wang@gta-travel.com'
	# body_text = 'FYI\n' + \
	# 			'Best\n' + \
	# 			'-Yu'
	# title_text = '[[[ Ctrip hotel reference ]]]'

	# # Or, if you want a copy in e.g. the 'Sent' folder
	# m = Message(
	# 	account=account,
	# 	folder=account.sent,
	# 	sender=Mailbox(email_address=email),
	# 	author=Mailbox(email_address=email),
	# 	subject=title_text,
	# 	body=body_text,
	# 	# to_recipients=[Mailbox(email_address=recipient_email1),
	# 	# 				Mailbox(email_address=recipient_email2),
	# 	# 				Mailbox(email_address=recipient_email3)
	# 	# 				]
	# 	# to_recipients=[Mailbox(email_address=recipient_email1),
	# 	# 				Mailbox(email_address=recipient_email2),
	# 	# 				Mailbox(email_address=recipient_email3),
	# 	# 				Mailbox(email_address=recipient_email4),
	# 	# 				Mailbox(email_address=recipient_email5)
	# 	# 				]
	# 	to_recipients=[Mailbox(email_address=recipient_email1),
	# 					Mailbox(email_address=recipient_email2),
	# 					Mailbox(email_address=recipient_email3),
	# 					Mailbox(email_address=recipient_email4)
	# 					]
	# 	)

	# with open(newest, 'rb') as f:
	# 	update_csv = FileAttachment(name=newest, content=f.read())
	# m.attach(update_csv)
	# m.send_and_save()

	# print('Message sent.. ')

if __name__ == '__main__':
	sendmail_win_hb()