# Intro

This is a collection of python scripts for daily routines of testing GTA API and analysis tools.

# Content

1. [swarm.py](#swarm) - A simple python scrript to run n times of AddBookingRequest and CancelBookingRequest by response from SearchHotelPriceRequest.
2. [sp.py](#sp) - Take in a list of hotel codes defined in hotel_codes and do pax 1, 2, 3 search on each of the hotel. 
3. [mapping.py](#mapping) - Checking if a csv file have duplicate GTA_key in hotel mapping.
4. [ctrip.py](#ctrip) - Dump relavant information of a hotel on ctrip given ctrip hotel id.
5. [spp.py](#spp) - Dump a csv file of specified GTA hotel code with relavant information.
6. [ctriptrip.py](#ctriptrip) - A script using webdriver to download all rate plan of a specific hotel on ctrip
7. [spplus.py](#spplus) - Dump a csv of dates when GTA hotel has a price 
8. [elong.py](#elong) - Dump a csv of price differences between what GTA offers and the lowest by Elong
9. [asp.py](#asp) - Dump rate plans of hotels as csv
10. [sendmail.py](#) - An example of send email with attachment
11. [as400.py](#) - An example of how you could connect to IBM AS400 with Python
12. [l2b.py](#) - An example of how to parse html with Soup
13. [haoqiao.py](#) - A crawler for extracting price from HQ
14. [booking_href.py](#) - A crawler grabbing all hotel href from a starting search result url of booking
14. [booking.py](#) - A crawler grabbing all hotel facilites from booking
15. [booking_room_facility.py](#) - A crawler for extracting room facilities from booking
16. [search_info.py](#) - Search GTA Item Information API
17. [ctripplus.py](#) - Compare GTA price and Ctrip price on room type level
18. [booking_id.py](#) - Search booking and dump booking id
19. [search_item_hr.py](#) - Search booking item and get hotel reference #
20. [hc.py](#) - Crawl GC and get hotel comfirmation #
21. [ctriproom.py](#) - Crawl Ctrip and get a list of Ctrip room types
22. [asp.py](#) - Fetch a list of rate plans from GTA API
23. [ctripmultiplus.py](#) - A shortcut for `ctripplus.py`
24. [ctripref.py](#) - A shortcut for running `booking_id.py`, `search_item_hr.py` and `hc.py`
25. [ctrip_update_res_no.py](#) - Take results from `hc.py` and push hotel ref to Ctrip's API
26. [ctrip_store_booking.py](#) - Keep track of bookings so not to push to Ctrip twice
27. [ctripref_stats_gai.py](#) - Take data from `ctrip_store_booking.py` to have the stats of hotel ref coverage
28. [sendmail_win.py](#) - A imporved example of how you can send emails by a Exchange Server account
29. [asp_parallel.py](#) - Multi thread version of `asp.py`
29. [asp_pool_w.py](#) - Multi process version of `asp.py` using pool
30. [sendmail_win_cs.py](#) - Example of sending email with attachment (Exchange server)
31. [ctripref_stat_v.ipynb](#) - notebook for Ctrip hotel ref stats 
32. [fault_http.py](#) - Example of reading Triometrics xls
32. [steemit.py](#) - views?
33. [pname_pool.py](#) - Get pax names from bookings
34. [asp_multi.py](#) - run asp_pool with multiple dates
35. [pa_hb.py](#) - run analytics on Ctrip HB price and availability check API log dump
36. [hb_er.py](#) - Run analytics on HB TRioMetrics price and availability log dump
37. [hb_report.py](#) - Run sendmail_win_hb to grab email attachment from inbox; Run hr_er to do analytics; send result to relevant parties using sendmail_win_hb2
38. [sendmail_win_hb.py](#) - Download appropriate pa log file from my inbox and save it
39. [sendmail_win_hb2.py](#) - Send result to relevant parties
40. [booking_count.py](#) - Count number of bookings of a client
41. [asp_pool_hb.py](#) - Batching HB API (Multi thread)

# Question?

Drop a mail to <mailto:tctctcly@gmail.com>.