__author__ = "Andrew Szymanski ()"
__version__ = "0.1.0"

"""
"""


import logging
import os
import inspect

from restkit import *
from simplejson import loads, dumps

# constants
LOG_INDENT = "  "        # to prettify logs
# keys in cfg file
URI = "URI"

# restkit
# http://restkit.readthedocs.io/en/latest/api/client.html

class ServiceDiscoveryClient(object):
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


   def register(self, args, kwargs):
      """ grab and validate config
      """
      self.logger.debug("%s::%s starting..." %  (self.__class__.__name__ , inspect.stack()[0][3]))         
      config_file = kwargs.get('cfg',"YOU_MUST_SPECIFY_CONFIG_FILE")
      self.configure(config_file)
      
      # restkit playgound
      uri_root = self.dict_config[URI]
      uri = uri_root + "/groups"
      
      
      self.logger.debug("playing with URI: [%s]" % (uri))
      c = Client()
      r = c.request(uri)
      print r.status
      print r.body_string()

      self.logger.debug("tyring POST URI: [%s]" % (uri))
      res = Resource(uri)
      data = dict(code="asz-code", name="asz-name", description="andrew test",meta="andrew meta" or None)
      response = res.post(payload=dumps(data), headers={'Content-Type': 'application/json'})
      print response    
      



   def __readconfig__(self, config_file):
      """ grab and validate config
      """
      self.logger.debug("%s::%s starting..." %  (self.__class__.__name__ , inspect.stack()[0][3]))         
      self.logger.debug("%s: [%s]" % ("config_file", config_file))

      self.logger.debug("%s reading config file: [%s]..." % (LOG_INDENT, config_file))
      
      new_dict = {}
      # read Cloudera Manager config
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
      keys = [URI]
      for key in keys:
            value = new_dict.get(key, None)
            if not value:
               raise Exception("'%s' not defined in config file: [%s]" % (key, cfg))
      
      self.dict_config = new_dict
      self.logger.info("%s URI: [%s]" % (LOG_INDENT, self.dict_config[URI]))
      


