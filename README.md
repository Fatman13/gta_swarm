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

# Elong<a name="elong"></a>

### Run

1. Run `python elong.py --hotel 330229`

# spplus<a name="spplus"></a>

### Run

1. Run `python spplus.py --from_d 2017-04-20 --to_d 2017-05-20 --file_name hotel_codes`.
2. You coud add `--skip` option to skip some dates.
3. `--n_sample` option will sample random entries in `--file_name`, ex: `--n_sample 100`

# Ctriptrip<a name="ctriptrip"></a>

### Install ctriptrip

1. Install [geckodriver](https://github.com/mozilla/geckodriver/releases) and properly [config](http://stackoverflow.com/questions/40208051/selenium-using-python-geckodriver-executable-needs-to-be-in-path) it.
2. Install [Chromedriver](https://sites.google.com/a/chromium.org/chromedriver/downloads). (Optional, depends on which browser you prefer to use)
3. Run `pip install splinter`.

### Run 

1. Run `python ctriptrip.py --hotel 4512809 --from_d 2017-05-05 --to_d 2017-05-15`

# SPP<a name="spp"></a>

### Run SPP

1. Run `python ctrip.py --hotel_code MEL_912 --from_d 2017-06-01 --to_d 2017-06-05`

# SP<a name="sp"></a>

### Install sp

1. run `pip install requests`.

### Config SP

1. Hotel codes shoul be put one per line in hotel_codes file.
2. `url`, `from_date` and `to_date` can be configed on top of the sp.py file.

# Mapping<a name="mapping"></a>

empty

# Ctrip<a name="ctrip"></a>

### Install Ctrip

1. run `pip install click`.
2. run `pip install requests`

### Run Ctrip

1. Open `cmd`, within the directory of the script, run `python ctrip.py`
2. Another example, run `python ctrip.py --hotel 996727 --from_d 2017-06-01 --to_d 2017-06-05`
3. A `output.csv` will be dumped with relavant information of the hotel.

NOTE: Not well tested on different hotels, might break at any point.

# SWARM<a name="swarm"></a>

### Install Swarm

1. Install [python 3.6](https://www.python.org/ftp/python/3.6.0/python-3.6.0.exe). (Remember to check add to PATH when installing)
2. Unzip the content. 
3. Open `cmd`, `cd` to the directory with extracted script. (Try `python --version`, if something went wrong try [add python executable folder to system or local PATH](http://stackoverflow.com/questions/3701646/how-to-add-to-the-pythonpath-in-windows-7))
4. run `pip install requests`.

### Run Swarm

1. Open `cmd`, within the directory of the script, run `python swarm.py` 
2. If you want output to be redirected to a file, run `python swarm.py > output`

Note: script not well tested, might break at any point.

### Config Swarm

1. `url`(request url) and `counter`(number of booking request) could be configed at the top of swarm.py script.
2. user credentials could be configed in SearchHotelPriceRequest.xml. The script will take credentials from SearchHotelPriceRequest.xml and override whatever is in AddBookingRequest.xml, and CancelBookingRequest.xml.
3. The script will try to keep some of the critical xml element consistent through the booking.
4. It is not recommended to remove any XML element or XML attributes in AddBookingRequest.xml, CancelBookingRequest.xml or SearchHotelPriceRequest.xml. It is also recommended that to keep Room element as it is. 

# Question?

Please send an email to <mailto:yu.leng@gta-travel.com>.