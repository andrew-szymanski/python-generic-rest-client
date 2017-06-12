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
      
      # (re)register group
      uri = uri_root + "/groups"
      self.register_group(uri, group, "ASZ GROUP NAME")
      
      # (re)register component
      uri = uri_root + "/components"
      self.register_component(uri, component, group, "ASZ COMPONENT NAME")           
      
      
      return
   
   
   
   
   
   
   
   
   
   
   
   
      # 
      # get key values info variables
      component = payload["component"]["code"]
      namespace = payload["namespace"]["code"]
      group = payload["group"]["code"]
      self.logger.info("%s component: [%s]" %  (LOG_INDENT, component))
      self.logger.info("%s namespace: [%s]" %  (LOG_INDENT, namespace))
      self.logger.info("%s group: [%s]" %  (LOG_INDENT, group))

      instances_dict = payload["instances"][0]
      hostname = instances_dict["hostname"]
      protocol = instances_dict["protocol"]
      ipv4 = instances_dict["ipv4"]
      transport = instances_dict["transport"]
      port = instances_dict["port"]
      self.logger.info("%s hostname: [%s]" %  (LOG_INDENT, hostname))
      self.logger.info("%s protocol: [%s]" %  (LOG_INDENT, protocol))
      self.logger.info("%s ipv4: [%s]" %  (LOG_INDENT, ipv4))
      self.logger.info("%s transport: [%s]" %  (LOG_INDENT, transport))
      self.logger.info("%s port: [%s]" %  (LOG_INDENT, port))

      # from now on we are using "groups" because "instances" not ready yet
      # so everything below needs to change when instances are ready
      # but the logic should be more less the same...maybe... 

      uri_root = self.dict_config[URI]
      
      # (re)register group
      uri = uri_root + "/group"
      self.register_group(uri, group, namespace)

      # (re)register component
      uri = uri_root + "/group"
      self.register_group(uri, group, namespace)      
      
      
      return
      
      # (re)register component
      uri = uri_root + "/components"
      self.logger.debug("resource URI: [%s]" % (uri))
      c = Client()
      resource = Resource(uri)
      self.logger.debug("registering component")
      component_dict = dict(code=component,name="andrew component name")
      group_dict = dict(code=group)
      component_array = array(group_dict, component_dict)
      print dumps(component_array)
      
      return
      response = resource.post(payload=dumps(component_dict), headers={'Content-Type': 'application/json'})
      self.logger.debug("%s response: %s" %  (LOG_INDENT, response.__dict__) )      

      return
      # 
      self.logger.debug("registering...")      
      response = resource.post(payload=dumps(payload), headers={'Content-Type': 'application/json'})
      self.logger.debug("%s response: %s" %  (LOG_INDENT, response.__dict__) )
      
      return

      # check if record already exists
      query = dict(code=component)
      response = resource.get(params_dict=query)
      result_str = response.body_string()
      result_list = loads(result_str)
      entry_exists = False
      if result_list:
         entry_exists = True
      self.logger.debug("entry exists: [%s]" % (entry_exists))  

      # if entry exists - delete so we can recreate it
      if entry_exists:
         result_dict = result_list[0]
         uuid = result_dict["uuid"]
         self.logger.debug("%s deleting uuid: [%s]" % (LOG_INDENT, uuid))
         response = resource.delete(uuid)

      # entry does not exist - create it
      self.logger.debug("registering...")
      timestamp = time.strftime("%Y-%m-%d %H:%M")
      meta_data = timestamp
      data = dict(code=component, name=namespace, description="andrew test",meta=meta_data or None)
      response = resource.post(payload=dumps(data), headers={'Content-Type': 'application/json'})
      self.logger.debug("%s response: %s" %  (LOG_INDENT, response) )


      return


      

      
      self.logger.debug("playing with URI: [%s]" % (uri))
      c = Client()
      #r = c.request(uri)
      #print r.status
      #print r.body_string()

      res = Resource(uri)
      # Query
      code="ASZ-CODE"
      query = dict(code=code)
      response = res.get(params_dict=query)
      #print response.status
      result_str = response.body_string()
      result_list = loads(result_str)
      if not result_list:
         print "   doesnt exist"
         self.logger.debug("tyring POST URI: [%s]" % (uri))
         data = dict(code="ASZ-CODE", name="asz-name", description="andrew test",meta="andrew meta" or None)
         response = res.post(payload=dumps(data), headers={'Content-Type': 'application/json'})
         print response.__dict__    
      else:
         print "   exist"
         result_dict = result_list[0]
         uuid = result_dict["uuid"]
         self.logger.debug("%suuid: [%s]" % (LOG_INDENT, uuid))
         response = res.delete(uuid)

      #print response.__dict__


      # query = "?code=%s" % code
      # query_uri = "%s%s" % (uri,query)
      # self.logger.debug("QUERY: [%s]" % (query_uri))
      # r = c.request(query_uri)
      # print r.status
      # result_str = r.body_string()
      # result_list = loads(result_str)
      # result_dict = result_list[0]
      # uuid = result_dict["uuid"]
      # self.logger.debug("%suuid: [%s]" % (LOG_INDENT, uuid))

      # DELETE
      #delete_uri = "%s/%s" % (uri, uuid)
      # response = res.delete(uuid)
      # print response.__dict__

 


      # POST
      #self.logger.debug("tyring POST URI: [%s]" % (uri))
      # data = dict(code="asz-code", name="asz-name", description="andrew test",meta="andrew meta" or None)
      # response = res.post(payload=dumps(data), headers={'Content-Type': 'application/json'})
      # print response    
   
   
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
      

# Register json
  # POST /v1/instances
  # {
  #   "group": {
  #     "code": "POC-V1"
  #   },
  #   "component": {
  #     "code": "mysql"
  #   },
  #   "namespace": {
  #     "code": "DEV"
  #   },
  #   "instances": [
  #     {
  #       "transport": "TCP",
  #       "protocol": "mysql",
  #       "hostname": "blah.com",
  #       "ipv4": "10.1.1.1",
  #       "port": 3306
  #     }
  #   ]
  # }

