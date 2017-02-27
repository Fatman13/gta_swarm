# GTA SWARM

A simple python scrript to run n times of AddBookingRequest and CancelBookingRequest by response from SearchHotelPriceRequest.

# Install

1. Install [python 3.6](https://www.python.org/ftp/python/3.6.0/python-3.6.0.exe). (Remember to check add to PATH when installing)
2. Unzip the content. 
3. Open `cmd`, `cd` to the directory with extracted script. (Try `python --version`, if something went wrong try [add python executable folder to system or local PATH](http://stackoverflow.com/questions/3701646/how-to-add-to-the-pythonpath-in-windows-7))
4. run `pip install requests`.

# Run

1. Open `cmd`, within the directory of the script, run `python swarm.py` 
2. If you want output to be redirected to a file, run `python swarm.py > output`

Note: script not well tested, might break at any point.

# Config

1. `url`(request url) and `counter`(number of booking request) could be configed at the top of swarm.py script.
2. user credentials could be configed in SearchHotelPriceRequest.xml. The script will take credentials from SearchHotelPriceRequest.xml and override whatever is in AddBookingRequest.xml, and CancelBookingRequest.xml.
3. The script will try to keep some of the critical xml element consistent through the booking.
4. It is not recommended to remove any XML element or XML attributes in AddBookingRequest.xml, CancelBookingRequest.xml or SearchHotelPriceRequest.xml. It is also recommended that to keep Room element as it is. 

# Question?

Please send an email to <mailto:yu.leng@gta-travel.com>.