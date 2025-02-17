# Installation

## Create a Virutalenv

    virtualenv env
    source env/bin/activate

## Install Dependencies

    pip install -r requirements.txt

# Test

    python manage.py test

# Run

    python manage.py syncdb
    python manage.py migrate
    python manage.py runserver

Open in browser: http://127.0.0.1:8000/admin/

## Postgresql fix (after running manage.py migrate)

# manually change portal_ipaddress.ip to type "inet"

    sudo su postgres
    psql -d portal
    ALTER TABLE portal_ipaddress ALTER COLUMN ip TYPE inet USING(ipinet);
    or if that fails (in newer Postgresql)
    ALTER TABLE portal_ipaddress ALTER COLUMN ip TYPE inet USING ip::inet;
    \q
    exit

