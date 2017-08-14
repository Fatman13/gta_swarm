#!/usr/bin/env python
# coding=utf-8

import pprint
import csv
import click 
import requests
import datetime as datetime
# from splinter import Browser
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException   
from selenium.common.exceptions import ElementNotVisibleException   
from selenium.common.exceptions import StaleElementReferenceException   
from selenium.common.exceptions import WebDriverException   
from selenium.common.exceptions import TimeoutException   

def validate_d(date_text):
	try:
		datetime.datetime.strptime(date_text, '%Y-%m-%d')
	except ValueError:
		raise ValueError("Incorrect data format, should be YYYY-MM-DD")

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + datetime.timedelta(n)


@click.command()
@click.option('--page', default=23, type=int)
@click.option('--url', default='https://www.booking.com/searchresults.html?aid=304142&label=gen173nr-1FCAEoggJCAlhYSDNiBW5vcmVmaDGIAQGYATK4AQbIAQ_YAQHoAQH4AQuSAgF5qAID&sid=c24f665d504aac0a9c235ce5f00da065&checkin_month=11&checkin_monthday=13&checkin_year=2017&checkout_month=11&checkout_monthday=14&checkout_year=2017&class_interval=1&group_adults=2&group_children=0&label_click=undef&lsf=class%7C5%7C22&nflt=ht_id%3D204%3Bclass%3D3%3Bclass%3D4%3Bclass%3D5%3B&no_rooms=1&region=5757&room1=A%2CA&sb_price_type=total&src=searchresults&ss=Pattaya&ssb=empty&ssne=Pattaya&ssne_untouched=Pattaya&track_BHKF=1&unchecked_filter=class&unchecked_filter=class&unchecked_filter=class&unchecked_filter=hoteltype&rows=15')
def booking_href(page, url):
	pp = pprint
	res = []

	# with Browser() as b:
	driver = webdriver.Firefox()
	driver.implicitly_wait(10) 
	# driver = webdriver.Ie()

	wait_s = 3
	wait_m = 10
	wait_l = 15

	# paris
	# url = 'https://www.booking.com/searchresults.html?aid=304142&label=gen173nr-1DCAsoTUIQaG90ZWxkdWJvaXNwYXJpc0gzYgVub3JlZmgxiAEBmAExuAEGyAEO2AED6AEB-AECkgIBeagCAw&sid=8131a341a0017240f7d3946be1baa8e3&checkin_month=6&checkin_monthday=29&checkin_year=2017&checkout_month=6&checkout_monthday=30&checkout_year=2017&city=-1456928&class_interval=1&group_adults=2&group_children=0&highlighted_hotels=50864&hp_sbox=1&label_click=undef&mih=0&no_rooms=1&room1=A%2CA&sb_price_type=total&src=hotel&ss=Paris&ssb=empty&ssne=Paris&ssne_untouched=Paris&unchecked_filter=class&unchecked_filter=hoteltype&nflt=class%3D3%3Bclass%3D4%3Bclass%3D5%3Bht_id%3D204%3B&lsf=ht_id|204|1160&update_av=1'
	# main_url = 'https://www.booking.com'
	# tokyo
	# url = 'https://www.booking.com/searchresults.html?aid=304142;label=gen173nr-1FCAsoTUIQaG90ZWxkdWJvaXNwYXJpc0gzYgVub3JlZmgxiAEBmAExuAEGyAEO2AEB6AEB-AECkgIBeagCAw;sid=455fb47c61b5bc889b31eedf9a24406d;checkin_month=7;checkin_monthday=10;checkin_year=2017;checkout_month=7;checkout_monthday=11;checkout_year=2017;class_interval=1;dest_id=-246227;dest_type=city;dtdisc=0;group_adults=2;group_children=0;inac=0;index_postcard=0;label_click=undef;lsf=class%7C3%7C322;mih=0;nflt=class%3D5%3Bclass%3D4%3Bclass%3D3%3B%3Bht_id%3D204;no_rooms=1;offset=0;pop_filter_id=ht_id-204;pop_filter_pos=0;pop_filter_rank=0;postcard=0;raw_dest_type=city;room1=A%2CA;sb_price_type=total;search_selected=1;src=index;ss=Tokyo%2C%20Tokyo%20Prefecture%2C%20Japan;ss_all=0;ss_raw=tokyo;ssb=empty;sshis=0;unchecked_filter=class;unchecked_filter=class;unchecked_filter=class&'
	# osaka
	# url = 'https://www.booking.com/searchresults.html?aid=304142&label=gen173nr-1FCAsoTUIQaG90ZWxkdWJvaXNwYXJpc0gzYgVub3JlZmgxiAEBmAExuAEGyAEO2AEB6AEB-AECkgIBeagCAw&sid=455fb47c61b5bc889b31eedf9a24406d&checkin_month=7&checkin_monthday=10&checkin_year=2017&checkout_month=7&checkout_monthday=11&checkout_year=2017&city=-246227&class_interval=1&dest_id=-240905&dest_type=city&group_adults=2&group_children=0&label_click=undef&lsf=class%7C4%7C40&mih=0&nflt=class%3D3%3Bclass%3D5%3Bclass%3D4%3Bht_id%3D204%3B&no_rooms=1&offset=0&pop_filter_id=ht_id-204&pop_filter_pos=0&pop_filter_rank=0&raw_dest_type=city&room1=A%2CA&sb_price_type=total&search_selected=1&src=searchresults&ss=Osaka%2C%20Osaka%20Prefecture%2C%20Japan&ss_raw=osaka&ssb=empty&ssne_untouched=Tokyo&unchecked_filter=class&unchecked_filter=class&unchecked_filter=class'
	# okinawa
	# url = 'https://www.booking.com/searchresults.html?aid=304142&label=gen173nr-1FCAEoggJCAlhYSDNiBW5vcmVmaDGIAQGYATG4AQbIAQ_YAQHoAQH4AQKSAgF5qAID&sid=455fb47c61b5bc889b31eedf9a24406d&checkin_month=7&checkin_monthday=3&checkin_year=2017&checkout_month=7&checkout_monthday=4&checkout_year=2017&class_interval=1&dest_id=2351&dest_type=region&dtdisc=0&group_adults=2&group_children=0&inac=0&index_postcard=0&label_click=undef&map=1&mih=0&no_rooms=1&postcard=0&raw_dest_type=region&room1=A%2CA&sb_price_type=total&search_selected=1&src=index&ss=Okinawa%2C%20Japan&ss_all=0&ss_raw=okinawa&ssb=empty&sshis=0&unchecked_filter=class&unchecked_filter=class&unchecked_filter=class&unchecked_filter=hoteltype&nflt=class%3D3%3Bclass%3D4%3Bclass%3D5%3Bht_id%3D204%3B&lsf=ht_id%7C204%7C148&update_av=1'
	# sapporo
	# url = 'https://www.booking.com/searchresults.html?aid=304142&label=gen173nr-1FCAEoggJCAlhYSDNiBW5vcmVmaDGIAQGYATG4AQbIAQ_YAQHoAQH4AQKSAgF5qAID&sid=455fb47c61b5bc889b31eedf9a24406d&checkin_month=7&checkin_monthday=3&checkin_year=2017&checkout_month=7&checkout_monthday=4&checkout_year=2017&class_interval=1&dest_id=-242395&dest_type=city&group_adults=2&group_children=0&label_click=undef&mih=0&no_rooms=1&raw_dest_type=city&room1=A%2CA&sb_price_type=total&search_selected=1&src=searchresults&ss=Sapporo%2C%20Hokkaido%2C%20Japan&ss_raw=sapp&ssb=empty&ssne_untouched=Okinawa&unchecked_filter=class&unchecked_filter=class&unchecked_filter=class&nflt=ht_id%3D204%3Bclass%3D3%3Bclass%3D4%3Bclass%3D5%3B&lsf=class%7C5%7C8'
	# fukuoka
	# url = 'https://www.booking.com/searchresults.html?aid=304142&label=gen173nr-1FCAEoggJCAlhYSDNiBW5vcmVmaDGIAQGYATG4AQbIAQ_YAQHoAQH4AQKSAgF5qAID&sid=455fb47c61b5bc889b31eedf9a24406d&checkin_month=7&checkin_monthday=3&checkin_year=2017&checkout_month=7&checkout_monthday=4&checkout_year=2017&city=-242395&class_interval=1&dest_id=900047908&dest_type=city&group_adults=2&group_children=0&label_click=undef&mih=0&no_rooms=1&raw_dest_type=city&room1=A%2CA&sb_price_type=total&search_selected=1&src=searchresults&ss=Fukuoka%2C%20Fukuoka%2C%20Japan&ss_raw=fukuo&ssb=empty&ssne_untouched=Sapporo&unchecked_filter=class&unchecked_filter=class&unchecked_filter=class&nflt=class%3D3%3Bht_id%3D204%3Bclass%3D4%3Bclass%3D5%3B&lsf=class%7C5%7C5'
	# nagoya
	# url = 'https://www.booking.com/searchresults.html?aid=304142&label=gen173nr-1FCAEoggJCAlhYSDNiBW5vcmVmaDGIAQGYATG4AQbIAQ_YAQHoAQH4AQKSAgF5qAID&sid=455fb47c61b5bc889b31eedf9a24406d&checkin_month=7&checkin_monthday=3&checkin_year=2017&checkout_month=7&checkout_monthday=4&checkout_year=2017&city=900047908&class_interval=1&dest_id=-237874&dest_type=city&group_adults=2&group_children=0&label_click=undef&mih=0&no_rooms=1&raw_dest_type=city&room1=A%2CA&sb_price_type=total&search_selected=1&src=searchresults&ss=Nagoya%2C%20Aichi%2C%20Japan&ss_raw=nagoya&ssb=empty&ssne_untouched=Fukuoka&unchecked_filter=class&unchecked_filter=class&unchecked_filter=class&nflt=ht_id%3D204%3Bclass%3D3%3Bclass%3D4%3Bclass%3D5%3B&lsf=class%7C5%7C4'
	# kobe
	# url = 'https://www.booking.com/searchresults.html?aid=304142&label=gen173nr-1FCAEoggJCAlhYSDNiBW5vcmVmaDGIAQGYATG4AQbIAQ_YAQHoAQH4AQKSAgF5qAID&sid=455fb47c61b5bc889b31eedf9a24406d&checkin_month=7&checkin_monthday=3&checkin_year=2017&checkout_month=7&checkout_monthday=4&checkout_year=2017&city=-237874&class_interval=1&dest_id=-233817&dest_type=city&group_adults=2&group_children=0&label_click=undef&mih=0&no_rooms=1&raw_dest_type=city&room1=A%2CA&sb_price_type=total&search_selected=1&src=searchresults&ss=Kobe%2C%20Hyogo%2C%20Japan&ss_raw=kobe&ssb=empty&ssne_untouched=Nagoya&unchecked_filter=class&unchecked_filter=class&unchecked_filter=class&nflt=ht_id%3D204%3Bclass%3D3%3Bclass%3D4%3Bclass%3D5%3B&lsf=class%7C5%7C7'
	# 普吉岛
	# url = 'https://www.booking.com/searchresults.zh-cn.html?label=gen173nr-1FCAEoggJCAlhYSDNiBW5vcmVmaDGIAQGYATG4AQbIAQ_YAQHoAQH4AQKSAgF5qAID&lang=zh-cn&sid=455fb47c61b5bc889b31eedf9a24406d&track_cisspo=1&sb=1&src=index&src_elem=sb&error_url=https%3A%2F%2Fwww.booking.com%2Findex.zh-cn.html%3Flabel%3Dgen173nr-1FCAEoggJCAlhYSDNiBW5vcmVmaDGIAQGYATG4AQbIAQ_YAQHoAQH4AQKSAgF5qAID%3Bsid%3D455fb47c61b5bc889b31eedf9a24406d%3Bsb_price_type%3Dtotal%26%3B&ss=%E6%99%AE%E5%90%89%E5%B2%9B346%E5%AE%BE%E9%A6%86%2C+%E6%99%AE%E5%90%89%E9%95%87%2C+%E6%99%AE%E5%90%89%E5%BA%9C%2C+%E6%B3%B0%E5%9B%BD&ssne=%E7%A5%9E%E6%88%B7&ssne_untouched=%E7%A5%9E%E6%88%B7&checkin_year=2017&checkin_month=7&checkin_monthday=18&checkout_year=2017&checkout_month=7&checkout_monthday=19&room1=A%2CA&group_adults=2&group_children=0&no_rooms=1&ss_raw=%E6%99%AE%E5%90%89%E5%B2%9B&ac_position=4&ac_langcode=zh&dest_id=431516&dest_type=hotel&search_pageview_id=d6f61ce153620037&search_selected=true&search_pageview_id=d6f61ce153620037&ac_suggestion_list_length=5&ac_suggestion_theme_list_length=0'
	# 普吉岛2
	# url = 'https://www.booking.com/searchresults.zh-cn.html?label=gen173nr-1FCAEoggJCAlhYSDNiBW5vcmVmaDGIAQGYATK4AQbIAQ_YAQHoAQH4AQuSAgF5qAID&sid=455fb47c61b5bc889b31eedf9a24406d&checkin_month=7&checkin_monthday=26&checkin_year=2017&checkout_month=7&checkout_monthday=27&checkout_year=2017&class_interval=1&dest_id=-3253342&dest_type=city&dtdisc=0&group_adults=2&group_children=0&inac=0&index_postcard=0&label_click=undef&no_rooms=1&postcard=0&raw_dest_type=city&room1=A%2CA&sb_price_type=total&search_selected=1&src=index&ss=%E6%99%AE%E5%90%89%E9%95%87%2C%20%E6%99%AE%E5%90%89%E5%BA%9C%2C%20%E6%B3%B0%E5%9B%BD&ss_all=0&ss_raw=%E6%99%AE%E5%90%89&ssb=empty&sshis=0&ssne_untouched=%E6%99%AE%E5%90%89%E9%95%87&nflt=ht_id%3D204%3B&lsf=ht_id%7C204%7C79&unchecked_filter=hoteltype'
	# pattaya
	# url = 'https://www.booking.com/searchresults.html?aid=304142&label=gen173nr-1FCAEoggJCAlhYSDNiBW5vcmVmaDGIAQGYATK4AQbIAQ_YAQHoAQH4AQuSAgF5qAID&sid=c24f665d504aac0a9c235ce5f00da065&checkin_month=11&checkin_monthday=13&checkin_year=2017&checkout_month=11&checkout_monthday=14&checkout_year=2017&class_interval=1&group_adults=2&group_children=0&label_click=undef&lsf=class%7C5%7C22&nflt=ht_id%3D204%3Bclass%3D3%3Bclass%3D4%3Bclass%3D5%3B&no_rooms=1&region=5757&room1=A%2CA&sb_price_type=total&src=searchresults&ss=Pattaya&ssb=empty&ssne=Pattaya&ssne_untouched=Pattaya&track_BHKF=1&unchecked_filter=class&unchecked_filter=class&unchecked_filter=class&unchecked_filter=hoteltype&rows=15'
	pages = page

	driver.get(url)

	element = WebDriverWait(driver, 20).until(
		lambda driver: driver.execute_script("return $.active == 0")
		)
	time.sleep(wait_m)

	for i in range(pages - 1):
		hotels = driver.find_elements_by_css_selector('a.hotel_name_link.url')
		for hotel in hotels:
			entry = {}
			entry['hotel_href'] = str(hotel.get_attribute('href'))
			print(str(hotel.get_attribute('href')))
			res.append(entry)
		# pages[i+2].click()
		# pages = driver.find_elements_by_css_selector('a.sr_pagination_link')
		pages = driver.find_elements_by_css_selector('li.sr_pagination_item')

		# page_cur = driver.find_element_by_css_selector('a.sr_pagination_link.current')
		page_cur = driver.find_element_by_css_selector('li.sr_pagination_item.current')
		i_cur = pages.index(page_cur)

		# pages[i+1].click()
		try:
			pages[i_cur+1].click()
			element = WebDriverWait(driver, 20).until(
				lambda driver: driver.execute_script("return $.active == 0")
			)
		except TimeoutException as e:
			print('Error: Time out exception not handled..')
			break
		
		time.sleep(wait_m)

	driver.quit()

	# 
	keys = res[0].keys()
	with open('output_booking_hotel_href' + datetime.datetime.now().strftime('_%y%m%d_%H%M') + '.csv', 'w', newline='', encoding='utf-8') as output_file:
		dict_writer = csv.DictWriter(output_file, keys)
		dict_writer.writeheader()
		dict_writer.writerows(res)
	
if __name__ == '__main__':
	booking_href()