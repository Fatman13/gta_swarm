#!/usr/bin/env python
# coding=utf-8

import pprint
import csv

class MyPrettyPrinter(pprint.PrettyPrinter):
	def format(self, object, context, maxlevels, level):
		if isinstance(object, unicode):
			return (object.encode('utf8'), True, False)
		return pprint.PrettyPrinter.format(self, object, context, maxlevels, level)

# pp = MyPrettyPrinter()
pp = pprint

is_unique = True

gta_keys = []
gta_keys_sorted = []
gta_keys_dup = []
duplicates = {}

with open('Confident.csv', encoding='utf-8') as csvfile:
	reader = csv.DictReader(csvfile, delimiter='|')
	# pp.pprint(reader.__class__)
	# pp.pprint(reader.fieldnames)
	# pp.pprint(reader.line_num)reader.

	for row in reader:
		if row['GTAKey']:
			# pp.pprint(row['GTAKey'])
			gta_keys.append(row['GTAKey'])

	# pp.pprint(reader.line_num)
	csvfile.seek(0)

	gta_keys_sorted = sorted(gta_keys)
	pre_key = ''
	for key in gta_keys_sorted:
		if pre_key == key:
			gta_keys_dup.append(key)
		pre_key = key

	pp.pprint('GTA keys dup list: ' + str(gta_keys_dup))

	for row in reader:
		a = 1
		if row['GTAKey'] in gta_keys_dup:
			if row['GTAKey'] in duplicates:
				duplicates[row['GTAKey']].append(row)
			else:
				duplicates[row['GTAKey']] = [row]
			# indices = [i for i, x in enumerate(gta_keys) if x == row['GTAKey']]
			# if len(indices) >= 2:
			# 	if row['GTAKey'] in duplicates:
			# 		duplicates[row['GTAKey']].append(row)
			# 	else:
			# 		duplicates[row['GTAKey']] = [row]

pp.pprint('/// /// /// Test Result /// /// ///')
pp.pprint(duplicates)

# pp.pprint(gta_keys)