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

      # read in json file
      json_file = kwargs.get('json',"YOU_MUST_SPECIFY_JSON_FILE")
      self.logger.info("json file: [%s]" %  json_file)
      payload = None
      with open(json_file) as json_data:
        payload = load(json_data)

      # root url
      uri_root = self.dict_config[URI]
      # get key values info variables
      component = payload["component"]["code"]
      namespace = payload["namespace"]["code"]
      group = payload["group"]["code"]
      self.logger.info("%s component: [%s]" %  (LOG_INDENT, component))
      self.logger.info("%s namespace: [%s]" %  (LOG_INDENT, namespace))
      self.logger.info("%s group: [%s]" %  (LOG_INDENT, group))
      
      ## (re)register group
      #uri = uri_root + "/groups"
      #self.register_group(uri, group, "ASZ GROUP NAME")
      
      ## (re)register component
      #uri = uri_root + "/components"
      #self.register_component(uri, component, group, "ASZ COMPONENT NAME")           
      
      # register instance
      uri = uri_root + "/instances"
      resource = Resource(uri)
      self.logger.debug("registering instance...") 
      #print dumps(payload)
      timestamp = time.strftime("%m-%m-%d %H:%M")
      response = resource.post(payload=dumps(payload), headers={'Content-Type': 'application/json'})
      self.logger.debug("%s response: %s" %  (LOG_INDENT, response.__dict__) )
      
      return

   
   
   def register_group(self, uri, code, name):
      """ (re)register group
      """
      self.logger.debug("%s::%s starting..." %  (self.__class__.__name__ , inspect.stack()[0][3]))
      
      self.logger.debug("uri: [%s],code: [%s],name: [%s]" % (uri, code, name))

      resource = Resource(uri)
      # check if record already exists
      query = dict(code=code)
      response = resource.get(params_dict=query)
      result_str = response.body_string()
      result_list = loads(result_str)
      entry_exists = False
      if result_list:
         entry_exists = True
      self.logger.debug("entry exists: [%s]" % (entry_exists))  
      timestamp = time.strftime("%Y-%m-%d %H:%M")

      # if entry exists - delete so we can recreate it
      if entry_exists:
         self.logger.debug("group already exists, nothing to do")
         return

      # entry does not exist - create it
      self.logger.debug("registering group...")
      meta_data = "updated by andrew: %s" % timestamp
      data = dict(code=code, name=name, description="andrew test",meta=meta_data or None)
      response = resource.post(payload=dumps(data), headers={'Content-Type': 'application/json'})
      self.logger.debug("%s response: %s" %  (LOG_INDENT, response.__dict__) )    
      
      
      
   def register_component(self, uri, component, group, name):
      """ (re)register group
      """
      self.logger.debug("%s::%s starting..." %  (self.__class__.__name__ , inspect.stack()[0][3]))
      
      self.logger.debug("uri: [%s],component: [%s],group: [%s],name: [%s]" % (uri, component, group, name))

      resource = Resource(uri)

      # check if record already exists
      query = dict(code=group)
      response = resource.get(params_dict=query)
      result_str = response.body_string()
      result_list = loads(result_str)
      entry_exists = False
      if result_list:
         entry_exists = True
      self.logger.debug("entry exists: [%s]" % (entry_exists))  
      timestamp = time.strftime("%Y-%m-%d %H:%M")

      # if entry exists - delete so we can recreate it
      if entry_exists:
         self.logger.debug("group already exists, nothing to do")
         return

      # entry does not exist - create it
      self.logger.debug("registering component...")
      meta_data = "updated by andrew: %s" % timestamp
      data = dict(group=dict(code=group),code=group,name=name)
      print dumps(data)
      response = resource.post(payload=dumps(data), headers={'Content-Type': 'application/json'})
      self.logger.debug("%s response: %s" %  (LOG_INDENT, response.__dict__) )      


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
      

