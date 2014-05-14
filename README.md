wpmphite
========

Fetch Neustar WPM synthetic web monitoring results and feed them into Carbon for ease of use.

Configuration and usage
-----------------------

wpmphite is configured to

Running wpmphite on Heroku
--------------------------

wpmphite comes pre-configured to run on heroku (that's how we run it!), it takes 30 seconds to get it up and running:

````shell
git init
git add .
git commit -m "wpmphite"
heroku apps:create myapp
git push heroku master
````

