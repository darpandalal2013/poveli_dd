PV App Installation Guild
==========================

Install prerequisites::

	sudo apt-get update
	sudo apt-get install python-pip apache2 mysql-server git-core memcached python-dev build-essential python-setuptools mysql-client libmysqlclient-dev libapache2-mod-wsgi openssl libcurl4-nss-dev  libjpeg-dev libfreetype6-dev

	pip install virtualenv virtualenvwrapper

Add the following to the ~/.bashrc::

	source /usr/local/bin/virtualenvwrapper.sh
	export WORKON_HOME=~/webapps
	export ENV='dev'

Create new virtual environment::

	mkdir ~/webapps
	cd ~/webapps
	mkvirtualenv pv
	mkdir ~/webapps/pv/src
	cd ~/webapps/pv/src
	git clone git@github.com:Povelli/app.git pv

Activate the virtual environment and install the packages::

	workon pv
	cd ~/webapps/pv/src/pv/
	pip install -r requirements.pip

Create database::

    ./manage.py syncdb
    ./manage.py loaddata fixtures.json
    
Run the Django development server::

    ./manage.py runserver