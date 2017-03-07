# Intro

This is a collection of python scripts to ease daily routines of testing GTA API and analysis tools.

# Content

1. [swarm.py](#swarm)
2. [sp.py](#sp)
3. [mapping.py](#mapping)
4. [ctrip.py](#ctrip)

# GTA SP<a name="sp"></a>

Take in a list of hotel codes defined in hotel_codes and do pax 1, 2, 3 search on each of the hotel. 

### Install sp

1. run `pip install requests`.

### Config SP

1. Hotel codes shoul be put one per line in hotel_codes file.
2. `url`, `from_date` and `to_date` can be configed on top of the sp.py file.

# GTA Mapping<a name="swarm"></a>

Checking if a csv file have duplicate GTA_key in hotel mapping.

# GTA Ctrip<a name="ctrip"></a>

Dump relavant information of a hotel on ctrip given ctrip hotel id.

### Install Ctrip

1. run `pip install click`.
2. run `pip install requests`

### Run Ctrip

1. Open `cmd`, within the directory of the script, run `python ctrip.py`
2. Another example, run `python ctrip.py --hotel 996727 --ci 2017-06-01 --co 2017-06-02`

# GTA SWARM<a name="swarm"></a>

A simple python scrript to run n times of AddBookingRequest and CancelBookingRequest by response from SearchHotelPriceRequest.

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