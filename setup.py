#!/usr/bin/env python

from distutils.core import setup

setup(name = 'GTA_swarm',
	version = '0.0.1',
	description = 'GTA API testing tools',
	author = 'Yu Leng',
	author_email = 'yu.leng@foxmail.com',
	url = 'http://tauntaunslayer13.me',
	install_requires = [
		'click',
		'requests'
	],
)