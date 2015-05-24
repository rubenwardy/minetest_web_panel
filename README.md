Minetest Web Panel
------------------

A web panel to control Minetest servers, written using Python and Flask. WIP.

Created by rubenwardy. License: GPL 3.0 or later.

![Screenshot of Minetest Web Panel](http://a.pomf.se/laswnl.png)

Installation
============

This software isn't really ready to be used quite yet.
But if you're interested:

	# Install requirements
	$ pip install -r requirements.txt
	$ sudo apt-get install luarocks
	$ sudo luarocks install luasocket

	# Setup database
	$ python db_create.py

	# Setup configuration
	$ cp config.cfg.example config.cfg

	# now edit config.cfg to point to your Minetest exe, etc!

Running
=======

* `$ python run.py`
* Go to <http://localhost:5000/>.
* The default username is 'admin' and the password 'pass'
