#!/usr/bin/env python
# coding=utf-8

# from openpyxl import Workbook
# from openpyxl import load_workbook
# wb = load_workbook('TUNIU-Look-to-Book_v202233_s532_2017-06-08-00-00.xls')
# ws = wb.active
# row_range = ws[22:51]
from bs4 import BeautifulSoup
import locale
# locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )
# res = []
import csv
import datetime
import glob, os
import click

clients = ['feizhu']
def find_client_by_filename(filename):
	l = [ client.lower() in filename.lower() for client in clients ]
	if any(l):
		i = l.index(True)
		return clients[i]
	return None

@click.command()
# @click.option('--days', default=0, type=int)
# @click.option('--duration', default=2, type=int)
# @click.option('--days', default=1, type=int)
def fault():
	res_error_dict = {}
	res_l2b_dict = {}
	res = []
	res_stage = []

	ERROR = 'errors'
	L2B = 'l2b'

	for file in glob.glob("*.xls"):
		client = find_client_by_filename(file)
		if client != None:
			entry = None
			if ERROR in file.lower():
				entry_list = res_error_dict[client] = []
			if L2B in file.lower():
				entry_list = res_l2b_dict[client] = []

			with open(file) as fp:
				soup = BeautifulSoup(fp)

				# entry[client] = soup.find_all('p', class_='reportTitle')[0].get_text()

				for i, tr_ele in enumerate(soup.find_all('tr')):
					if i == 0:
						continue
					date = None
					ent = {}
					for j, td_ele in enumerate(tr_ele.find_all('td')):
						# ent = None
						if ERROR in file.lower():
							
							if j == 0:
								date = td_ele.get_text()
								ent['date'] = date
							if j == 1:
								if 'add' in td_ele.get_text().lower():
									ent['type'] = 'add'
								elif 'search' in td_ele.get_text().lower():
									ent['type'] = 'search'
								else:
									ent['type'] = 'unknown'
							if j == 2:
								ent['value'] = int(td_ele.get_text().replace(',',''))
								entry_list.append(ent)

						if L2B in file.lower():
							if j == 0:
								date = td_ele.get_text()
							if j == 1:
								ent = {}
								ent['date'] = date
								ent['type'] = 'search'
								ent['value'] = int(td_ele.get_text().replace(',',''))
								entry_list.append(ent)
							if j == 2:
								ent = {}
								ent['date'] = date
								ent['type'] = 'add'
								ent['value'] = int(td_ele.get_text().replace(',',''))
								entry_list.append(ent)

	print(res_error_dict)			
	print(res_l2b_dict)

	for client in clients:
		for data1 in res_error_dict[client]:
			for data2 in res_l2b_dict[client]:
				if data1['date'] == data2['date'] and data1['type'] == data2['type']:
					entry = {}
					entry['name'] = '_'.join([client, data1['type'], 'failure_%'])
					entry[data1['date']] = float('{0:.3f}'.format(float(data1['value'] / (data1['value'] + data2['value']) )))
					res_stage.append(entry)
					break

	for client in clients:
		add_failure = {}
		search_failure = {}
		for ent in res_stage:
			if client in ent['name'] and 'add' in ent['name']:
				for k, v in ent.items():
					add_failure[k] = v
			if client in ent['name'] and 'search' in ent['name']:
				for k, v in ent.items():
					search_failure[k] = v
		res.append(add_failure)
		res.append(search_failure)

	keys = res[0].keys()
	print(res)
	traget_filename = '_'.join(['output_failure_weekly', datetime.datetime.now().strftime('%y%m%d_%H%M')]) + '.csv'
	with open(traget_filename, 'w', newline='', encoding='utf-8') as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		dict_writer.writeheader()
		dict_writer.writerows(res)

if __name__ == '__main__':
	fault()
# os.chdir("/mydir")
# for file in glob.glob("*.xls"):
#     # print(file)

# 	# with open('TUNIU-Look-to-Book_v202233_s532_2017-06-08-00-00.xls') as fp:
# 	with open(file) as fp:
# 		soup = BeautifulSoup(fp)
# 		# soup = BeautifulSoup('TUNIU-Look-to-Book_v202233_s532_2017-06-08-00-00.xls', 'html.parser')

# 		# pp.pprint(soup.find_all('tr'))

# 		# new
# 		entry_searches = {}
# 		entry_bookings = {}

# 		entry = {}

# 		name = soup.find_all('p', class_='reportTitle')[0].get_text()
# 		entry['name'] = name

# 		# new
# 		entry_searches['name'] = name + ' (searches)'
# 		entry_bookings['name'] = name + ' (bookings)'

# 		counter = 0

# 		trs_num = len(soup.find_all('tr'))

# 		# last_searches = -1
# 		# last_bookings = -1
# 		# last_l2b = -1

# 		for tr_ele in soup.find_all('tr'):
# 			counter += 1
# 			if counter == 1:
# 				continue
# 			# leave out most current week
# 			# if counter == 6:
# 			# 	continue	

# 			td_eles = tr_ele.find_all('td')

# 			# pp.pprint(counter)
# 			# pp.pprint(td_eles)
# 			# pp.pprint(td_eles[0])

# 			searches = 0
# 			date = ''
# 			for i, td_ele in enumerate(tr_ele.find_all('td')):
# 				# if i == 5:
# 				# 	continue
# 				# pp.pprint(i)
# 				# pp.pprint(td_ele)
# 				# bookings = -1
# 				# l2b = -1
# 				if i == 0:
# 					date = td_ele.get_text()
# 					entry[date] = 0
# 				if i == 1:
# 					searches = int(td_ele.get_text().replace(',',''))
# 					# searches = locale.atoi(td_ele.get_text())
# 					entry_searches[date] = searches
# 				if i == 2: 
# 					if td_ele.get_text() != '-':
# 						bookings = int(td_ele.get_text().replace(',',''))
# 						l2b = float('{0:.0f}'.format(float(searches / bookings )))
# 						entry[date] = l2b
# 						entry_bookings[date] = bookings
# 					if td_ele.get_text() == '-':
# 						bookings = 0
# 						l2b = searches
# 						entry[date] = l2b
# 						entry_bookings[date] = bookings
# 				# if counter == trs_num - 1:
# 				# 	last_searches = searches
# 				# 	last_bookings = bookings
# 				# 	last_l2b = l2b
# 				# if counter == trs_num:
# 				# 	if last_searches != 0:
# 				# 		entry_searches['Percentage'] = float('{0:.3f}'.format(float( (searches - last_searches) / last_searches )))
# 				# 	else:
# 				# 		entry_searches['Percentage'] = 1
# 				# 	print('last search ' + str(last_searches))
# 				# 	print('search ' + str(searches))
# 				# 	if last_bookings != 0:
# 				# 		entry_bookings['Percentage'] = float('{0:.3f}'.format(float( (bookings - last_bookings) / last_bookings )))
# 				# 	else:
# 				# 		entry_bookings['Percentage'] = 1
# 				# 	if last_l2b != 0:
# 				# 		entry['Percentage'] = float('{0:.3f}'.format(float( (l2b - last_l2b) / last_l2b ))) 
# 				# 	else:
# 				# 		entry['Percentage'] = 1

# 					# entry[date] = float(searches / locale.atoi(td_ele.get_text()))

# 			# entry[td_eles[0].get_text()] = 1

# 		pp.pprint(entry)

# 		index = -2
# 		index_minus_one = index - 1
# 		searches = list(entry_searches.values())[index]
# 		last_searches = list(entry_searches.values())[index_minus_one]
# 		if last_searches != 0:
# 			entry_searches['Percentage'] = float('{0:.3f}'.format(float( (searches - last_searches) / last_searches )))
# 		else:
# 			entry_searches['Percentage'] = 1
# 		bookings = list(entry_bookings.values())[index]
# 		last_bookings = list(entry_bookings.values())[index_minus_one]
# 		if last_bookings != 0:
# 			entry_bookings['Percentage'] = float('{0:.3f}'.format(float( (bookings - last_bookings) / last_bookings )))
# 		else:
# 			entry_bookings['Percentage'] = 1
# 		l2b = list(entry.values())[index]
# 		last_l2b = list(entry.values())[index_minus_one]
# 		if last_l2b != 0:
# 			entry['Percentage'] = float('{0:.3f}'.format(float( (l2b - last_l2b) / last_l2b )))
# 		else:
# 			entry['Percentage'] = 1
# 		entry_searches['comment'] = ''		
# 		entry_bookings['comment'] = ''		
# 		entry['comment'] = ''		
# 		res.append(entry_searches)
# 		res.append(entry_bookings)
# 		res.append(entry)

# # field_names = set()
# # for entry in res:
# # 	field_names |= set(entry.keys())
# # field_names.add('name')

# keys = None
# max_len = 0
# for ent in res:
# 	if len(ent.keys()) > max_len:
# 		max_len = len(ent.keys())
# 		keys = ent.keys()

# # keys = res_weekly[0].keys()
# with open('output_l2b_weekly_' + datetime.datetime.now().strftime('%y%m%d_%H%M') + '.csv', 'w', newline='', encoding='utf-8') as output_file:
# 	# dict_writer = csv.DictWriter(output_file, keys)
# 	# dict_writer = csv.DictWriter(output_file, field_names)
# 	dict_writer = csv.DictWriter(output_file, keys)
# 	dict_writer.writeheader()
# 	dict_writer.writerows(res)

# 
# keys = res[0].keys()
# with open('output_l2b_' + datetime.datetime.now().strftime('%y%m%d_%H%M') + '.csv', 'w', encoding='utf-8') as output_file:
# 	# dict_writer = csv.DictWriter(output_file, keys)
# 	# dict_writer = csv.DictWriter(output_file, field_names)
# 	dict_writer = csv.DictWriter(output_file, keys)
# 	dict_writer.writeheader()
# 	dict_writer.writerows(res)