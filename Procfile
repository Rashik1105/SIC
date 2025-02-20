Procfile

web: gunicorn SocialInfluencersConnect.wsgi --bind 0.0.0.0:$PORT
#or works good with external database
web: python manage.py migrate && gunicorn SocialInfluencersConnect.wsgi
