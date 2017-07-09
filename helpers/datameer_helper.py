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
# keys in cfg file
URI = "root_url"
USER_ID="user_id"
USER_PASSWORD_FILE="user_password_file"

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
      uri_root = self.dict_config[URI]
      # authentication
      auth = BasicAuth(self.dict_config[USER_ID], self.__get_password__())
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
      
      new_dict = {}
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
                  new_dict[key] = val
      except Exception, e:
            raise Exception("Could not read config file: [%s], error: [%s]" % (config_file, e))
         
      # validate all params
      keys = [URI,USER_ID,USER_PASSWORD_FILE]
      for key in keys:
            value = new_dict.get(key, None)
            if not value:
               raise Exception("'%s' not defined in config file: [%s]" % (key, config_file))
      
      self.dict_config = new_dict
      self.logger.info("%s %s: [%s]" % (LOG_INDENT, URI, self.dict_config[URI]))
      self.logger.info("%s %s: [%s]" % (LOG_INDENT, USER_ID, self.dict_config[USER_ID]))               
  
   def __get_password__(self):     
      self.logger.debug("%s::%s starting..." %  (self.__class__.__name__ , inspect.stack()[0][3]))
      # read password file
      password_file = self.dict_config[USER_PASSWORD_FILE]
      password = None
      try:
            with open(password_file) as f:
               password=f.read()
      except Exception, e:
            raise Exception("Could not read password file: [%s], error: [%s]" % (password_file, e))
      password = password.replace('\n','')
      password = password.rstrip()
      return password   



      

