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

* ALLOWED_HOSTS - Allowed hosts
* POSTGRES_DB - PostgreSQL DB name
* POSTGRES_USER - PostgreSQL DB user name
* POSTGRES_PASSWORD - PostgreSQL DB password
* POSTGRES_HOST - PostgreSQL DB host
* POSTGRES_PORT - PostgreSQL DB port
* DJANGO_SECRET_KEY - Your django project secret key
* CLIENT_SECRET_GMAIL - Your gmail client secret key
* CLIENT_ID_GMAIL - Your gmail client ID
* CLIENT_ID_SLACK - Your slack client ID
* CLIENT_SECRET_SLACK - Your slack client secret key
* GOOGLE_REDIRECT_URI - Your gmail project redirect uri
* USER_AGENT - Web browser user agent
* AWS_SECRET_ACCESS_KEY - Your AWS account secret access key
* AWS_ACCESS_KEY_ID - Your AWS account access key ID
* AWS_STORAGE_BUCKET_NAME - Your S3 bucket name


