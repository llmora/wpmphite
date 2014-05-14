#!/usr/bin/env python

"""wpmphite.py: import Neustar WPM monitor results to carbon, for use in graphite"""

__author__ = "Lluis Mora"
__license__ = "BSD"
__version__ = "1.0.0"
__email__ = "lluismh+code@gmail.com"
__status__ = "Production"

import urllib2
import hashlib
import time
import string
import json
from pprint import pprint
from datetime import datetime, timedelta
import pickle
import dateutil.parser
import socket
import struct
import logging
import calendar
import httplib
import os

class App():

  def wpm_query (self, apikey, apisecret, method, parameters=''):
    base_url = 'http://api.neustar.biz/performance'
    service = '/monitor'
    version = '/1.0'

    time.sleep(5)

    hash = hashlib.md5()

    # seconds since GMT Epoch
    timestamp = str(int(time.time()))

    hash.update(apikey + apisecret + timestamp)
    sig = hash.hexdigest()
    url = base_url + service + version + method + '?' + parameters + '&apikey=' + apikey + '&sig=' + sig

    data = dict()

    try:
    
      response = urllib2.urlopen(url)
      json_data = response.read()
      data = json.loads(json_data)
    
    except urllib2.HTTPError as e:
      logger.error("Received HTTPError: %s" % e.code)
      logger.error(e.read())

    except urllib2.URLError as e:
      logger.error("Received URLError: ")
      logger.error(e.args)
      
    except ValueError as e:
      logger.error("Received ValueError: ")
      logger.error(e)
    except httplib.IncompleteRead as e:
      logger.error("Received IncompleteRead: ")
      logger.error(e)

    return data

  def carbon_send (self, host, port, message):
    payload = pickle.dumps(message)
    header = struct.pack("!L", len(payload))
    message = header + payload
    try:
      sock = socket.socket()
      sock.connect((host, port))
      sock.sendall(message)
      sock.close()
    except:
      logger.error("Exception sending log to carbon")
    
  def run(self):
  
    logger.info("WPMPHITE " + __version__ + " started");

    apikey = os.environ['wpm_apikey']
    apisecret = os.environ['wpm_apisecret']
    frequency = int(os.environ['wpm_frequency'])
    carbon_host = os.environ['carbon_host']
    carbon_port = int(os.environ['carbon_port'])
    carbon_apikey = os.environ['carbon_apikey']

    monitors = os.environ['wpm_monitor']
    monitor_list = string.split(monitors, ',')

    if len(monitor_list) > 1:

      while 1:

        # Get list of monitors and their IDs
        wpm_monitors = self.wpm_query(apikey, apisecret, '')
        
        if wpm_monitors is not None and ('data' in wpm_monitors) and ('items' in wpm_monitors['data']):

          active_monitors = dict()

          for wpm_monitor in wpm_monitors['data']['items']:
            for monitor in monitor_list:
              monitor = monitor.strip()

              if wpm_monitor is not None and ('name' in wpm_monitor) and (wpm_monitor['name'] == monitor):
                active_monitors[monitor] = wpm_monitor['id']

          for active_monitor in active_monitors.keys():

            # Retrieve all samples for the past 2 * time
            logger.info("Retrieving data for monitor: " + active_monitor + "...")
            current_time = datetime.utcnow()
            start_time = current_time - timedelta(seconds=20*int(frequency))
            param_end = current_time.isoformat()
            param_start = start_time.isoformat()
            param_offset = 0
            done = 0

            while done == 0:
              
              wpm_samples = self.wpm_query(apikey, apisecret, '/' + active_monitors.get(active_monitor) + '/sample', 'startDate=' + param_start + '&endDate=' + param_end + '&offset=' + str(param_offset))

              if wpm_samples is not None and ('data' in wpm_samples) and ('count' in wpm_samples['data']):
              
                if wpm_samples['data']['count'] != 2000:
                  done = 1
                else:
                  param_offset += 2000
                  
                data = []
                
                if ('items' in wpm_samples['data']):

                  for wpm_sample in wpm_samples['data']['items']:
                  
                    if wpm_sample is not None and ('startTime' in wpm_sample) and ('status' in wpm_sample) and ('duration' in wpm_sample):
                  
                      sample_time = dateutil.parser.parse(wpm_sample['startTime'])
                      sample_status = wpm_sample['status']
                      sample_duration = wpm_sample['duration']
                      
                      if sample_status != "SUCCESS":
                        sample_duration = 999999
                      
                      data_time = int(calendar.timegm(sample_time.timetuple()))
                      data.append((carbon_apikey + '.' + 'wpm.stats.' + active_monitor.replace('.','_'), (data_time, sample_duration)))

                  self.carbon_send(carbon_host, carbon_port, data)
                  logger.info("Sent " + str(wpm_samples['data']['count']) + " items")
              
        logger.info("Sleeping for " + str(frequency) + " seconds")
        time.sleep(frequency)


logger = logging.getLogger("wpmphite")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logger.addHandler(handler)

app = App()
app.run()
