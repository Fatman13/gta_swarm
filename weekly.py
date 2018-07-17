#!/usr/bin/env python
# coding=utf-8

import pprint
# import csv
import click 
# import requests
# import datetime as datetime
# from datetime import date
# from xml.etree import ElementTree as ET
import os
# from random import sample
# import random
# import json
# import logging
import subprocess
import glob
import time
import sys
import datetime
import re

# hua shi shui jiao
def hua_style_sleep():
	for i in range(3):
		print('sleeping..' + str(i))
		time.sleep(1)

# import glob, os
# os.chdir("/mydir")
# for file in glob.glob("*.txt"):
# 	print(file)

@click.command()
# @click.option('--days', default=0, type=int)
# @click.option('--duration', default=3, type=int)
# @click.option('--days', default=1, type=int)
def weekly():

	os.chdir('C:\\YuYuYu\\Stats')
	for file in glob.glob('*.xls'):
		os.remove(file)
		print('removing.. ' + file)
	subprocess.call(['python', 'sendmail_win_at.py', '--days', '-10'])
	subprocess.call(['python', 'fault.py'])
	subprocess.call(['python', 'fault_http.py'])
	subprocess.call(['python', 'l2b.py'])
	subprocess.call(['python', 'sendmail_win_at2.py'])



if __name__ == '__main__':
	weekly()