<h1>Project Management's Integration</h1>

Project Management's Integration is a project that combines data from different sources(Gmail and Slack) and displays in Confluence Software

<h3>Features</h3>

*  Gmail, Slack and Confluence authorization.
*  Retriving files and messages by tag/label automatically once a day.
*  Displaying retrieved data in Confluence software program.
*  PostgreSQL database support with psycopg2.



<h3>How to install and run</h3>

```
git clone https://gitlab.com/zensoft-rts/pms_integration_backend.git
cd pms_integration_backend
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```


<h3>Environment variables</h3>

* POSTGRES_DB - PostgreSQL DB name
* POSTGRES_USER - PostgreSQL DB user name
* POSTGRES_PASSWORD - PostgreSQL DB password
* POSTGRES_HOST - PostgreSQL DB host
* POSTGRES_PORT - PostgreSQL DB port
* DJANGO_SECRET_KEY - Your django project secret key
* GMAIL_CLIENT_SECRET - Your gmail client secret key
* GMAIL_CLIENT_ID - Your gmail client id
* GMAIL_PROJECT_ID - Your gmail project id 


