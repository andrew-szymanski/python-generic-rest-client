__author__ = "Andrew Szymanski ()"
__version__ = "0.1.0"

"""
"""


import logging
import os
import inspect
import time
from array import *

from restkit import *
from simplejson import load, loads, dumps

# constants
LOG_INDENT = "  "        # to prettify logs
# constants for config keys
CONFIG_URI_ROOT="DATAMEER_URI"
CONFIG_USER_ID="DATAMEER_USER"
CONFIG_USER_PASSWORD="DATAMEER_PASSWORD"
# keys in cfg file / env variables
CONFIG_KEYS = (CONFIG_URI_ROOT, CONFIG_USER_ID, CONFIG_USER_PASSWORD)

# restkit
# http://restkit.readthedocs.io/en/latest/api/client.html

class DatameerClient(object):
   """
   """    
   def __init__(self, *args, **kwargs):
      """Create an object and attach or initialize logger
      """
      self.logger = kwargs.get('logger',None)
      if ( self.logger is None ):
            # Get an instance of a logger
            console = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s: %(levelname)-8s %(message)s',"%Y-%m-%d %H:%M:%S")
            console.setFormatter(formatter)
            logging.getLogger('').addHandler(console)
            self.logger = logging.getLogger('')
            self.logger.setLevel(logging.INFO)
      # initial log entry
      self.logger.info("%s: %s version [%s]" % (self.__class__.__name__, inspect.getfile(inspect.currentframe()),__version__))
      
      # initialize variables - so all are listed here for convenience
      self.dict_config = {}    # config params
      for config_key in CONFIG_KEYS:
         self.dict_config[config_key] = None

   def configure(self, config_file):
      """ grab and validate config
      """
      self.logger.debug("%s::%s starting..." %  (self.__class__.__name__ , inspect.stack()[0][3]))         
      self.__readconfig__(config_file)

   def get_jobs(self, args, kwargs):
      """ 
      """
      self.logger.debug("%s::%s starting..." %  (self.__class__.__name__ , inspect.stack()[0][3]))
      config_file = kwargs.get('cfg',"")
      if not config_file:
         raise Exception("you must specify config file!")

      self.configure(config_file)

      # root url
      uri_root = self.dict_config[DATAMEER_URI]
      # authentication
      auth = BasicAuth(self.dict_config[CONFIG_USER_ID], self.dict_config[CONFIG_USER_PASSWORD])
      # list all jobs
      uri = uri_root + "/export-job"
      resource = Resource(uri,filters=[auth])
      self.logger.debug("getting list of all jobs...") 
      #print dumps(payload)
      timestamp = time.strftime("%m-%m-%d %H:%M")
      response = resource.get(headers={'Content-Type': 'application/json'})
      result_str = response.body_string()
      #self.logger.debug("%s response: %s" %  (LOG_INDENT, response.__dict__) )      
      self.logger.debug("%s response: %s" %  (LOG_INDENT, result_str) )      


   def __readconfig__(self, config_file):
      """ grab and validate config
      """
      self.logger.debug("%s::%s starting..." %  (self.__class__.__name__ , inspect.stack()[0][3]))         
      self.logger.debug("%s: [%s]" % ("config_file", config_file))

      self.logger.debug("%s reading config file: [%s]..." % (LOG_INDENT, config_file))
      

      # read config file
      try:
            with open(config_file) as f:
               for line in f:
                  line = line.strip()
                  if line.startswith("#"):           # comment line
                        continue
                  if not line:                       # empty line
                        continue
                  (key, val) = line.split('=')
                  key = key.strip()
                  val = val.strip()
                  self.dict_config[key] = val
                  self.logger.debug("%s [%s] = [%s]" % (LOG_INDENT, key, val))
      except Exception, e:
            raise Exception("Could not read config file: [%s], error: [%s]" % (config_file, e))

      # and check if env vars with the same name exist - and overwrite values from file if they do
      for key in CONFIG_KEYS:
         value = os.getenv(key, None)
         if value:
            self.logger.debug("%s env var [%s] found so it will be used instead, overridng value in conf file" % (LOG_INDENT, key))
            self.dict_config[key] = value

      # determine whether password is literal or password file (in which case get its content)
      password = self.__get_password__()
      self.dict_config[CONFIG_USER_PASSWORD] = password

      # validate all params
      for key in CONFIG_KEYS:
            value = self.dict_config.get(key, None)
            if not value:
               raise Exception("mandatory value for [%s] not defined in config file [%s] or as env variable. " % (key, config_file))

      self.logger.info("%s %s: [%s]" % (LOG_INDENT, CONFIG_URI_ROOT, self.dict_config[CONFIG_URI_ROOT]))
      self.logger.info("%s %s: [%s]" % (LOG_INDENT, CONFIG_USER_ID, self.dict_config[CONFIG_USER_ID]))               
  
   def __get_password__(self):     
      self.logger.debug("%s::%s starting..." %  (self.__class__.__name__ , inspect.stack()[0][3]))
      # check if value is a password file or not
      password_value = self.dict_config[CONFIG_USER_PASSWORD]
      password = None
      try:
            with open(password_value) as f:
               password=f.read()
               # we managed to read the file - so grab password
               password = password.replace('\n','')
               password = password.rstrip()
               self.logger.debug("%s password read in from: [%s]" % (LOG_INDENT, CONFIG_USER_PASSWORD))
               return password
      except Exception, e:
            pass

      password = password_value
      return password



      

