# clubs-hrm
Workforce and payroll management software for Sports Teams / Clubs
___



___
## Installation and Setup

Prerequisites:

+ [Python3](https://www.python.org/downloads/release/python-377/) with pip
+ Local [Postgresql](https://www.postgresql.org/download/) installation or another backend


### Installation Instructions

Clone repository:

    git clone https://github.com/alexander-yf-yu/clubs-hrm.git

If you want to use a virtualenv, create one now. Here is a link to the python virtual environments [documentation](http://dev.nodeca.com).

Install python package requirements using pip:
    
    pip install -r path/to/requirements.txt

### Configure backend:
This section assumes the use of postgresql, for more information on using other databases, checkout the django [docs](https://docs.djangoproject.com/en/3.0/ref/settings/#std:setting-DATABASES).

Create a new database and database-user in postgresql. You can do this through the psql CLI. Check out the [psql docs](https://www.postgresql.org/docs/12/app-psql.html) for more info. [This](https://www.youtube.com/watch?v=qw--VYLpxG4) video is a good resource for a beginner to postgresql and for troubleshooting issues.

In the settings.py file at path/to/clubs-hrm/mysite/mysite/settings.py, edit the file to connect django to the database installation. Fill in the 'DATABASES' dictionary with your database name and user credentials. Change the port number if you're not using the default 5432.


```python
# settings.py

...

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'DATABASE_NAME',
        'USER': 'DATABASE_USER_USERNAME',
        'PASSWORD': 'DATABASE_USER_PASSWORD',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

...
```

### Running server on localhost:

Navigate to the directory containing manage.py:

    cd clubs-hrm/mysite/

Migrate the django default models and our custom models into the database.

    python3 manage.py migrate

Now start the server with:

    python3 manage.py runserver

The server should be running on [http://127.0.0.1:8000/](http://127.0.0.1:8000/), and visiting that url in a browser should display the site.

___








