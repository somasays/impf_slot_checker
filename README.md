Install python > 3.7
Install pipenv

Add your doctolib credentials to  creds.template and rename the file to creds

```
~ pipenv install
~ pipenv shell
~ python main.py
```
running main.py will open a new chrome window for every impfzentrum that has a open slot in the last minute
and you can select the vaccine and try to book the appointment.

The same window shall be used for the corresponding center till you quit it, in which case it will open a new window.