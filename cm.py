#!/usr/bin/env python
# coding=utf-8

import pprint
import csv
import click 

pp = pprint

@click.command()
# @click.argument('input_fs', type=click.File('rb'), nargs=-1)
@click.argument('output_f', type=click.File('wb'))
def cm(output_f):
	pp.pprint(input_fs)
	pp.pprint(output_f)
	for f in input_fs:
		while True:
			chunk = f.read(1024)
			if not chunk:
				break
			output_f.write(chunk)
			output_f.flush()

if __name__ == '__main__':
	cm()