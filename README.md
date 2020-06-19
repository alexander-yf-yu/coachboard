# clubs-hrm

## Workforce and payroll management Webapp for Sports Teams/Clubs

This django-based webapp helps sports clubs manage their staff and reduce communications. 

> In a typical sports club, there are coaches, atheletes, and managing staff. Managing the day to day operations of the club poses a challenge. 

This app offers a centralized location for coaches and administrative staff to manage coaching schedules. The app also allows managing staff to keep track of employee hours and calculate their hours over specific time period.

In the app, coaches and managing staff create an account they use to identify themselves as either a coach or managing staff member.

A typical use case for a coach would be to log in and view their shifts, preview the upcoming work schedule, and respond to any other coaches that need a substitute.

A managing staff member can view the shifts of all coaches and calculate employees' hours for payroll. 
___

## Demo Video

[![DEMO](https://i9.ytimg.com/vi/S_uITy0Y_aQ/mq1.jpg?sqp=CLTbsPcF&rs=AOn4CLD6eFgmzMvAU2svp90NXspGMTbcUg)](https://www.youtube.com/watch?v=S_uITy0Y_aQ "Demo")

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








