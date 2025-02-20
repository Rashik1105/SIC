Procfile

web: gunicorn SocialInfluencersConnect.wsgi --log-file - 
#or works good with external database
web: python manage.py migrate && gunicorn SocialInfluencersConnect.wsgi
