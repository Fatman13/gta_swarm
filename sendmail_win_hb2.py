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
 
sendmail_secret = None
with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secrets.json')) as data_file:    
	sendmail_secret = (json.load(data_file))['sendmail_win']

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
@click.option('--filename', default='output_hb_pa_stats_')
@click.option('--email', default='no-reply@gta-travel.com')
def sendmail_win_hb2(filename, email):
	target_filename = filename + '*.csv'
	newest = max(glob.iglob(target_filename), key=os.path.getctime)
	print('newest file: ' + newest)
	today_date = datetime.datetime.now().strftime('%y%m%d')
	try:
		newest_date = re.search( filename + '(\d+)', newest).group(1)
	except AttributeError:
		newest_date = ''
	print('newest date: ' + newest_date)
	if newest_date != today_date:
		print('Error: newest date != today date.. mannual intervention needed..')
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

	recipient_email = 'asaf.steinfeld@touricoholidays.com'
	recipient_email1 = 'ronald.chan@touricoholidays.com'
	recipient_email2 = 'yun.liu@gta-travel.com'
	recipient_email3 = 'lwang@hotelbeds.com'
	recipient_email4 = 'kfu@hotelbeds.com'
	body_text = 'FYI\n' + \
				'For chain offline recommendation, please open the attachment and filter \"recommend_offline\" column by \"yes\".\n' + \
				'This is an automated message. Please do not reply.\n' + \
				'Best\n' + \
				'-Yu'
	title_text = '[[[ Ctrip PA Stats ]]]'

	# Or, if you want a copy in e.g. the 'Sent' folder
	m = Message(
		account=account,
		folder=account.sent,
		sender=Mailbox(email_address=email),
		author=Mailbox(email_address=email),
		subject=title_text,
		body=body_text,
		# to_recipients=[Mailbox(email_address=recipient_email1),
		# 				Mailbox(email_address=recipient_email2),
		# 				Mailbox(email_address=recipient_email3)
		# 				]
		# to_recipients=[Mailbox(email_address=recipient_email1),
		# 				Mailbox(email_address=recipient_email2),
		# 				Mailbox(email_address=recipient_email3),
		# 				Mailbox(email_address=recipient_email4),
		# 				Mailbox(email_address=recipient_email5)
		# 				]
		to_recipients=[Mailbox(email_address=recipient_email1),
						Mailbox(email_address=recipient_email),
						Mailbox(email_address=recipient_email2),
						Mailbox(email_address=recipient_email3),
						Mailbox(email_address=recipient_email4)
						]
		)

	with open(newest, 'rb') as f:
		update_csv = FileAttachment(name=newest, content=f.read())
	m.attach(update_csv)
	m.send_and_save()

	print('Message sent.. ')

if __name__ == '__main__':
	sendmail_win_hb2()