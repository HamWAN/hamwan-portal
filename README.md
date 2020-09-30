# INSTALLATION

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

Open in Browser: http://127.0.0.1:8000/admin/
