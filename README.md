wpmphite
========

Neustar's WPM (Web Performance Monitoring, http://www.neustar.biz/services/web-performance/monitoring), formerly known as WebMetrics is a sophisticated web synthetic transaction generator, typically used to measure availability of 
web applications and servers from probing nodes across the world.

The WPM scripting interface allows the user to configure quite advanced functionality to test journeys across your website, however the reporting interface is a bit limited on how information can be represented. We developed wpmphite to
be able to regularly import the WPM results into a Graphite carbon system so that presenting the data would be much easier. For instance, in our case we are using a dashing (http://shopify.github.io/dashing/) dashboard to show availability
metrics in a way that our business understands it.

wpmphite uses the splendid WPM API to fetch results associated with your monitors and feeds them into Graphite.

Configuration and usage
-----------------------

wpmphite is configured through the following environment variables:

````
wpm_apikey: The API key that wpmphite will use to access WPM, get it from your WPM contorl panel
wpm_apisecret: The API secret associated with the key
wpm_frequency: Frequency, in seconds, to query the WPM interface. We do not recommend to set it to less than 60, WPM has some throttling controls that coudl skew your results
wpm_monitor: Comma-separated list of monitors to query, use the monitor names as defined in WPM, e.g.: wpm_monitor: monitor1,monitor2,monitor3

carbon_host: Carbon host to send the data to
carbon_port: Carbon daemon port, typically 2004
carbon_apikey: We are using hosted graphite, which requires an API key for metric insertion. Leave empty if you are not using hosted graphite

````

Once the environment variables are defined, just run the application like this:

````shell
python wpmphite.py
````

Running wpmphite on Heroku
--------------------------

wpmphite comes pre-configured to run on heroku (that's how we run it!), it takes 30 seconds to get it up and running, just make sure your environment variables are on a '.env' file and run:

````shell
git init
git add .
git commit -m "wpmphite"
heroku apps:create myapp
git push heroku master
````

