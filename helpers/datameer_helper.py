__author__ = "Andrew Szymanski ()"
__version__ = "0.1.0"

"""
"""


import logging
import os
import inspect
import time
from array import *
import glob
from datetime import datetime

from restkit import *
from simplejson import load, loads, dumps

# constants
LOG_INDENT = "  "        # to prettify logs
# constants for config keys in cfg file / env vars
CONFIG_URI_ROOT="DATAMEER_URI"
CONFIG_USER_ID="DATAMEER_USER"
CONFIG_USER_PASSWORD="DATAMEER_PASSWORD"
CONFIG_EXPORT_FILE="DATAMEER_EXPORT_FILE"
CONFIG_EXPORT_DIR="DATAMEER_EXPORT_DIR"
CONFIG_EXPORTABLES_FOLDER="DATAMEER_EXPORTABLES_FOLDER"
# keys in cfg file / env variables
CONFIG_FILE_KEYS = [CONFIG_URI_ROOT, CONFIG_USER_ID, CONFIG_USER_PASSWORD,CONFIG_EXPORT_FILE,CONFIG_EXPORT_DIR,CONFIG_EXPORTABLES_FOLDER]

# constants for derived config keys  
CONFIG_APP_ROOT_DIR="APP_ROOT_DIR"
# keys in cfg file / env variables
CONFIG_APP_KEYS = [CONFIG_APP_ROOT_DIR]

# ARTIFACTS types to export - please note that this value is used to build API url
# so has to be exact as per API documentation (without slash)
ARTIFACTS_TYPES = ['import-job','workbook','export-job']

# artifact export output filename prefix
EXPORT_FILENAME_PREFIX = "datameer-export"




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
      self.artifacts_list = None    # list of datameer jobs
      for config_key in CONFIG_FILE_KEYS:
         self.dict_config[config_key] = None

   def configure(self, config_file):
      """ grab and validate config
      """
      self.logger.debug("%s::%s starting..." %  (self.__class__.__name__ , inspect.stack()[0][3]))         
      self.__readconfig__(config_file)

      # get root dir of this app
      this_module_fullpath = os.path.realpath(__file__)
      this_module_dir = os.path.dirname(this_module_fullpath)
      this_project_dir = os.path.dirname(this_module_dir)
      self.dict_config[CONFIG_APP_ROOT_DIR] = this_project_dir

      # validate and print all derived config
      for key in CONFIG_APP_KEYS:
            value = self.dict_config.get(key, None)
            if not value:
               raise Exception("value for [%s] is NULL" % (key))
            else:
               self.logger.debug("%s [%s] = [%s]" % (LOG_INDENT,key, self.dict_config[key]))

      # a dictionary for all exportable artifacts
      self.all_exportable_artifacts_dict = None
      # a dictionary for all artifacts we want to export (will contain artifacts in json string)
      self.artifacts_to_export_json_dict = None
      # a dictionary of artifacts we specified in artifacts_to_export.list.txt:
      #  key = artifact name, value = 'action' (UPDATE or DELETE)
      self.artifacts_from_list_file_dict = None

   def export_artifacts(self, args, kwargs):
      """ Main method for job export
      """
      self.logger.debug("%s::%s starting..." %  (self.__class__.__name__ , inspect.stack()[0][3]))
      config_file = kwargs.get('cfg',"")
      if not config_file:
         raise Exception("you must specify config file!")

      self.configure(config_file)

      # read in artifacts to export - into dictionary - key is an artifact name, value is an "action"
      self.artifacts_from_list_file_dict = self.__read_export_list__(self.dict_config[CONFIG_EXPORT_FILE])
      if not self.artifacts_from_list_file_dict:
         raise Exception("Could not find any artifacts to export in file: [%s]" % (self.dict_config[CONFIG_EXPORT_FILE]))

      # get list of all exportable artifacts in datameer
      self.all_exportable_artifacts_dict = self.get_artifacts()
      count_total = 0
      for key in self.all_exportable_artifacts_dict:
         count_total = count_total + len(self.all_exportable_artifacts_dict[key])
      self.logger.info("%s total exportable artifacts found: [%s]..." % (LOG_INDENT, count_total))


      # get articacts to export - again, dict, key is artifact type, value is a list of artifacts for that type
      self.logger.info("%s selecting artifacts specified in [%s] file..." % (LOG_INDENT, self.dict_config[CONFIG_EXPORT_FILE]))
      self.artifacts_to_export_json_dict = self.__get_artifacts_to_export__(self.artifacts_from_list_file_dict)

      # write out artifacts in json so we can import them
      self.__write_out_artifacts__()


   def get_artifacts(self):
      """ Get a list of all artifacts, i.e  import jobs, export jobs and workbooks,
      but only if they are in CONFIG_EXPORTABLES_FOLDER or its subfolders
      """ 
      self.logger.debug("%s::%s starting..." %  (self.__class__.__name__ , inspect.stack()[0][3]))

      # root url
      uri_root = self.dict_config[CONFIG_URI_ROOT]
      # authentication
      auth = BasicAuth(self.dict_config[CONFIG_USER_ID], self.dict_config[CONFIG_USER_PASSWORD])

      # dictionary - each key is url for artifact type - and value will be a list of all artifacts for that type
      ret_dict = {}
      ignored_count = 0           # count all artifacts that matched but were in different folder

      for artifact_url in ARTIFACTS_TYPES:
         uri = "%s/%s" % (uri_root,artifact_url)
         resource = Resource(uri,filters=[auth])
         self.logger.debug("%s getting artifacts of [%s] (%s)..." % (LOG_INDENT, artifact_url, uri)) 
         timestamp = time.strftime("%m-%m-%d %H:%M")
         response = resource.get(headers={'Content-Type': 'application/json'})
         result_str = response.body_string()
         result_list = loads(result_str)
         clean_list = []
         
         # exclude all artifacts which are not in CONFIG_EXPORTABLES_FOLDER
         for artifact in result_list:
           artifact_path = artifact['path']
           if artifact_path.startswith(self.dict_config[CONFIG_EXPORTABLES_FOLDER]) == False:
               ignored_count = ignored_count + 1
               continue
           clean_list.append(artifact)
         
         ret_dict[artifact_url] = clean_list
         self.logger.debug("%s %s [%s] --> [%s] artifacts loaded" % (LOG_INDENT, LOG_INDENT, artifact_url, len(ret_dict[artifact_url]))) 

      if ignored_count > 0:
         self.logger.warn("[%s] artifacts were ignored because they weren't in [%s] folder" % (ignored_count, self.dict_config[CONFIG_EXPORTABLES_FOLDER]))
 
      return ret_dict

   def __get_artifacts_to_export__(self, artifacts_name_dict):
      """ extract artifacts we actually want to export
      artifacts_name_list is dictionary, key is an artifact name, value is an "action"
      """ 
      self.logger.debug("%s::%s starting..." %  (self.__class__.__name__ , inspect.stack()[0][3]))

      result_dict = {}

      # iterate through all exportable artifacts - trying to match them (by name) to artifacts specified for export
      for artifact_type in self.all_exportable_artifacts_dict:
         all_artifacts_for_type_list = self.all_exportable_artifacts_dict[artifact_type]
         self.logger.debug("%s ------  artifact type: [%s], total: [%s]  ------" % (LOG_INDENT, artifact_type, len(all_artifacts_for_type_list)))
         # initialise output list
         output_json_list = []
         # all_artifacts_for_type_list is a list of dictionaries, we want to match on entry with key 'name'
         for item_dict in all_artifacts_for_type_list:
            # check if it is on our list of artifacts to export
           if item_dict['name'] in artifacts_name_dict:
               # we found artifact to export - we now need to get full json for it
               uri = "%s/%s/%s" % (self.dict_config[CONFIG_URI_ROOT], artifact_type,item_dict['id'])
               auth = BasicAuth(self.dict_config[CONFIG_USER_ID], self.dict_config[CONFIG_USER_PASSWORD])
               resource = Resource(uri,filters=[auth])
               self.logger.debug("%s getting artifact [%s], [%s]..." % (LOG_INDENT, item_dict['name'], uri)) 
               response = resource.get(headers={'Content-Type': 'application/json'})
               result_json = response.body_string()
               # print result_json
               # we now have json to import to another env... store it 
               output_json_list.append(result_json)
         # we finished iterating through all artifacts of that type - so add list to our return dictionary
         result_dict[artifact_type] = output_json_list

      # finished all loops
      return result_dict



   def __write_out_artifacts__(self):
      """ write out artifacts to export to a file
      """
      self.logger.debug("%s::%s starting..." %  (self.__class__.__name__ , inspect.stack()[0][3]))

      # create dir if it does not exist
      self.logger.debug("%s making sure dir exists: [%s]..." % (LOG_INDENT, self.dict_config[CONFIG_EXPORT_DIR]))
      if not os.path.exists(self.dict_config[CONFIG_EXPORT_DIR]):
         try:
            os.makedirs(self.dict_config[CONFIG_EXPORT_DIR])
         except Exception, e:
            raise Exception("Could not create dir: [%s], error: [%s]" % (self.dict_config[CONFIG_EXPORT_DIR], e))

      # delete all files by extension - noddy but safer than using * wildcard or deleting whole dir
      files_path = "%s/*.json" % self.dict_config[CONFIG_EXPORT_DIR]
      self.logger.debug("%s deleting all files: [%s]..." % (LOG_INDENT, files_path))
      files = glob.glob(files_path)
      for f in files:
         os.remove(f)
      

      # self.artifacts_from_list_file_dict

      # OK - now iterate through all artifacts to export and write a separate json file for each
      self.logger.debug("%s starting to write out json files..." % (LOG_INDENT))
      for artifact_type in self.artifacts_to_export_json_dict:
         for artifact_json in self.artifacts_to_export_json_dict[artifact_type]:
            # noddy - load json so we can determine some properties... you may ask why not load json to start with 
            # and write it out here, rather than doing both?  Well - this is extra safety net - so we write json EXACTLY
            # how we got it from datameer
            artifact_dict = {}
            artifact_dict = loads(artifact_json)
            artifact_name = artifact_dict['file']['name']
            artifact_uuid = artifact_dict['file']['uuid']
            artifact_action = self.artifacts_from_list_file_dict[artifact_name]
            artifact_action = artifact_action.upper()

            # and now write out
            now = datetime.now()
            timestamp = now.strftime("%y-%m-%d.%H%M.%f")
            output_filename = "%s/%s.%s.%s.%s.%s.%s.json" % (
               self.dict_config[CONFIG_EXPORT_DIR],
               EXPORT_FILENAME_PREFIX,
               artifact_type,
               artifact_action,
               artifact_name,
               artifact_uuid,
               timestamp)
            with open(output_filename, "w") as text_file:
               text_file.write(artifact_json)
            self.logger.debug("%s %s [%s] done" % (LOG_INDENT,LOG_INDENT,output_filename))
 


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
      except Exception, e:
            raise Exception("Could not read config file: [%s], error: [%s]" % (config_file, e))

      # and check if env vars with the same name exist - and overwrite values from file if they do
      for key in CONFIG_FILE_KEYS:
         value = os.getenv(key, None)
         if value:
            self.logger.debug("%s env var [%s] found so it will be used instead, overridng value in conf file" % (LOG_INDENT, key))
            self.dict_config[key] = value

      # determine whether password is literal or password file (in which case get its content)
      password = self.__get_password__()
      self.dict_config[CONFIG_USER_PASSWORD] = password

      # validate all params
      for key in CONFIG_FILE_KEYS:
            value = self.dict_config.get(key, None)
            if not value:
               raise Exception("mandatory value for [%s] not defined in config file [%s] or as env variable. " % (key, config_file))

      self.logger.info("%s %s: [%s]" % (LOG_INDENT, CONFIG_URI_ROOT, self.dict_config[CONFIG_URI_ROOT]))
      self.logger.info("%s %s: [%s]" % (LOG_INDENT, CONFIG_USER_ID, self.dict_config[CONFIG_USER_ID]))               
      self.logger.info("%s %s: [%s]" % (LOG_INDENT, CONFIG_EXPORT_FILE, self.dict_config[CONFIG_EXPORT_FILE]))               
      self.logger.info("%s %s: [%s]" % (LOG_INDENT, CONFIG_EXPORT_DIR, self.dict_config[CONFIG_EXPORT_DIR]))
      self.logger.info("%s %s: [%s]" % (LOG_INDENT, CONFIG_EXPORTABLES_FOLDER, self.dict_config[CONFIG_EXPORTABLES_FOLDER]))      

      # self.logger.info("%s %s: [%s]" % (LOG_INDENT, CONFIG_USER_PASSWORD, self.dict_config[CONFIG_USER_PASSWORD]))                    
  
   def __get_password__(self):     
      self.logger.debug("%s %s::%s starting..." %  (LOG_INDENT,self.__class__.__name__ , inspect.stack()[0][3]))
      # check if value is a password file or not
      password_value = self.dict_config[CONFIG_USER_PASSWORD]
      password = None
      try:
            with open(password_value) as f:
               password=f.read()
               # we managed to read the file - so grab password
               password = password.replace('\n','')
               password = password.rstrip()
               self.logger.debug("%s %s password read in from: [%s]" % (LOG_INDENT, LOG_INDENT, CONFIG_USER_PASSWORD))
               return password
      except Exception, e:
            pass

      self.logger.debug("%s %s password taken as literal value" % (LOG_INDENT, LOG_INDENT))
      password = password_value
      return password

   def __read_export_list__(self, job_list_file):
      """ read in file specifying artifacts to export
      """
      self.logger.debug("%s::%s starting..." %  (self.__class__.__name__ , inspect.stack()[0][3]))         
      artifacts_to_export_dict = {}

      try:
         with open(job_list_file) as f:
            for line in f:
               line = line.strip()
               if line.startswith("#"):           # comment line
                  continue
               if not line:                       # empty line
                  continue
               # split into tuple - 1st element is "action", 2nd is a job name
               (action, artifact_name) = line.split(":",1)
               artifacts_to_export_dict[artifact_name] = action
 
      except Exception, e:
         raise Exception("Could not read jobs to export file: [%s], error: [%s]" % (job_list_file, e))

      self.logger.info("%s number of jobs to export: [%s]" % (LOG_INDENT, len(artifacts_to_export_dict)))
      return artifacts_to_export_dict
      


