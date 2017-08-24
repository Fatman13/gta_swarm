# from openpyxl import Workbook
# from openpyxl import load_workbook
import pprint

pp = pprint

# wb = load_workbook('TUNIU-Look-to-Book_v202233_s532_2017-06-08-00-00.xls')
# ws = wb.active
# row_range = ws[22:51]


from bs4 import BeautifulSoup

import locale
# locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )

res = []

import csv
import datetime
import glob, os
import re
# os.chdir("/mydir")
for file in glob.glob("*.xls"):
    # print(file)
	s = ''
	with open(file) as fp:
		s = fp.read()

	# with open('TUNIU-Look-to-Book_v202233_s532_2017-06-08-00-00.xls') as fp:
	with open(file) as fp:
		soup = BeautifulSoup(fp)
		# soup = BeautifulSoup('TUNIU-Look-to-Book_v202233_s532_2017-06-08-00-00.xls', 'html.parser')

		# pp.pprint(soup.find_all('tr'))

		entry = {}

		# name = soup.find_all('p', class_='reportTitle')[0].get_text()
		# entry['name'] = name

		# print(str(soup))

		try:
			# client_name = re.search("class=3D'reportTitle'>(.*?)</p>", str(soup)).group(1)
			client_name = re.search("class=3D'reportTitle'>(.*?)</p>", s).group(1)
		except AttributeError:
			print('Warning: fail to get client name.. ')
			client_name = ''
		entry['name'] = client_name

		counter = 0

		for tr_ele in soup.find_all('tr'):
			counter += 1
			if counter == 1:
				continue

			td_eles = tr_ele.find_all('td')

			# pp.pprint(counter)
			# pp.pprint(td_eles)
			# pp.pprint(td_eles[0])

			searches = 0
			date = ''
			for i, td_ele in enumerate(tr_ele.find_all('td')):
				# pp.pprint(i)
				# pp.pprint(td_ele)
				if i == 0:
					date = td_ele.get_text()
					entry[date] = 0
				if i == 1:
					if td_ele.get_text() == '-':
						searches = 0
						continue
					searches = int(td_ele.get_text().replace(',',''))
					# searches = locale.atoi(td_ele.get_text())
				if i == 2: 
					if td_ele.get_text() != '-':
						entry[date] = float('{0:.0f}'.format(float(searches / int(td_ele.get_text().replace(',','')) )))
					if td_ele.get_text() == '-':
						entry[date] = str(searches) + '*'	
					# entry[date] = float(searches / locale.atoi(td_ele.get_text()))

			# entry[td_eles[0].get_text()] = 1

		pp.pprint(entry)
		res.append(entry)

# field_names = set()
# for entry in res:
# 	field_names |= set(entry.keys())
# field_names.add('name')

keys = None
max_len = 0
for ent in res:
	if len(ent.keys()) > max_len:
		max_len = len(ent.keys())
		keys = ent.keys()

# keys = res_weekly[0].keys()
with open('output_l2b_weekly_' + datetime.datetime.now().strftime('%y%m%d_%H%M') + '.csv', 'w', newline='', encoding='utf-8') as output_file:
	# dict_writer = csv.DictWriter(output_file, keys)
	# dict_writer = csv.DictWriter(output_file, field_names)
	dict_writer = csv.DictWriter(output_file, keys)
	dict_writer.writeheader()
	dict_writer.writerows(res)

# 
# keys = res[0].keys()
# with open('output_l2b_' + datetime.datetime.now().strftime('%y%m%d_%H%M') + '.csv', 'w', encoding='utf-8') as output_file:
# 	# dict_writer = csv.DictWriter(output_file, keys)
# 	# dict_writer = csv.DictWriter(output_file, field_names)
# 	dict_writer = csv.DictWriter(output_file, keys)
# 	dict_writer.writeheader()
# 	dict_writer.writerows(res)