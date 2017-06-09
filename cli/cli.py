#!/usr/bin/env python

__author__ = "Andrew Szymanski ()"
__version__ = "0.1"

""" main script
"""
import sys
import logging
import os
import inspect
import imp

# import helpers.cdh_aws_helper
# import /home/madpole/data/code/github/python-generic-rest-client/helpers/boto_helper.py


LOG_INDENT = "  "
console = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s: %(levelname)-8s %(message)s',"%Y-%m-%d %H:%M:%S")
console.setFormatter(formatter)
logging.getLogger(__name__).addHandler(console)
logger = logging.getLogger(__name__)

def importFromURI(uri):
   """ import module
   """
   mod = None
   mname = os.path.basename(uri)
   print uri
   print mname

   if os.path.exists(uri+'.pyc'):
      try:
            return imp.load_compiled(mname, uri+'.pyc')
      except:
            pass
   if os.path.exists(uri+'.py'):
      try:
            return imp.load_source(mname, uri+'.py')
      except:
            pass

   return mod


 

class Helper_Manager(object):
   """ Main class which does the whole workflow
   """
   def __init__(self, *args, **kwargs):
      """Create an object and attach or initialize logger
      """
      self.logger = kwargs.get('logger',None)
      if ( self.logger is None ):
            # Get an instance of a logger
            self.logger = logger
      # initial log entry
      self.logger.setLevel(logger.getEffectiveLevel())
      self.logger.debug("%s: %s version [%s]" % (self.__class__.__name__, inspect.getfile(inspect.currentframe()),__version__))
      
      # initialize all vars to avoid "undeclared"
      # and to have a nice neat list of all member vars
      # self.cdh_aws_helper = None

      


   def configure(self, *args, **kwargs):
      """ Grab and validate all input params
      Will throw Exception on error(s)
      """
      self.logger.debug("%s::%s starting..." %  (self.__class__.__name__ , inspect.stack()[0][3])) 


      # read in configuration file
      config_file = kwargs.get('cfg', None)
      self.logger.info("reading in configuration file [%s]..." % config_file)
      
      # import specified helper module
      helper_module_arg = kwargs.get('exec')
      #helper_module,helper_method = helper_module_arg.split(".")
      self.logger.info("importing helper module [%s]..." % helper_module_arg)
      
      klass = self.import_class("helpers/service_discovery_helper.Helper")
      print klass
      #import_class("helpers/service_discovery_helper.Helper")

      
      #import helpers.boto_helper
      # klass = import_class(helper_module_arg)

      # helper_module_imported = importFromURI("/home/madpole/data/code/github/python-generic-rest-client/helpers/boto_helper", True)
      
      
      #helper_module_imported = imp.load_source("service_discovery_helper", "/home/madpole/data/code/github/python-generic-rest-client/helpers/service_discovery_helper.py")
      #print helper_module_imported
      #my_class = getattr(helper_module_imported, 'Helper')
      #my_instance = my_class()
      #print my_instance
      

      
      
      
      # Composite Cloudera Helper_Manager API / AWS boto helper
      #self.cdh_aws_helper = helpers.cdh_aws_helper.CdhAwsHelper(logger=self.logger)
      #try:
            #self.cdh_aws_helper.configure(cfg=config_file)
      #except Exception, e:
            #raise Exception("error while trying to configure CdhAwsHelper: [%s]" % e)
      
      
      ## Check connection to CDH CM
      #self.logger.info("testing connection to CDH CM...")
      #try:
            #self.cdh_aws_helper.cm_connect()
      #except Exception, e:
            #raise Exception("error while trying to configure CdhAwsHelper: [%s]" % e)
      
      
      ## Check connection to CDH CM
      #self.logger.info("testing connection to AWS boto...")
      #try:
            #self.cdh_aws_helper.boto_connect()
      #except Exception, e:
            #raise Exception("error while trying to configure CdhAwsHelper: [%s]" % e)
      
   def import_class(self, cl):
      """ dot notation for relative
      """
      
      # get root dir of this app
      this_module_fullpath = os.path.realpath(__file__)
      this_module_dir = os.path.dirname(this_module_fullpath)
      this_project_dir = os.path.dirname(this_module_dir)
      self.logger.debug("  project dir: [%s]" % this_project_dir)
      
      # split path to the module from class name
      module_path,class_name = cl.split(".")
      module_full_path = "%s/%s" % (this_project_dir,module_path)
      self.logger.debug("  module: [%s], class: [%s]" % (module_full_path,class_name))
      
      # import module
      helper_module_imported = importFromURI(module_full_path)
      print helper_module_imported
      
      #print cl
      #d = cl.rfind(".")
      #classname = cl[d+1:len(cl)]
      #m = __import__(cl[0:d], globals(), locals(), [classname])
      #return getattr(m, classname)


#                      **********************************************************
#                      **** mainRun - parse args and decide what to do
#                      **********************************************************
def mainRun(opts, parser):
    # set log level - we might control it by some option in the future
    if ( opts.debug ):
        logger.setLevel("DEBUG")
        logger.debug("logging level activated: [DEBUG]")
    else:
        logger.setLevel("INFO")
    logger.info("%s starting..." % inspect.stack()[0][3])
    
    logger.debug("creating Helper_Manager object...") 
    mngr = Helper_Manager(logger=logger)
    logger.debug("setting up Helper_Manager...") 

    try:
        mngr.configure(**opts.__dict__)
    except Exception, e:
        logger.error("%s" % e)
        parser.print_help()
        sys.exit(1)
    

    logger.info("all done")   



# manual testing min setup:

# tested / use cases:
# ./cli.py
# ./cli.py  --debug=Y
# alias d='cli/cli.py -d Y -c $HOME/.passwords/cdh-manager.cip.prod.eu-west-1.cfg';alias a='cli/cli.py  -c $HOME/.passwords/cdh-manager.cip.prod.eu-west-1.cfg'

def main(argv=None):
    from optparse import OptionParser, OptionGroup
    logger.debug("main starting...")

    argv = argv or sys.argv
    parser = OptionParser(description="python extendable REST client (based on restkit)",
                      version=__version__,
                      usage="usage: %prog [options]")
    # cat options
    cat_options = OptionGroup(parser, "options")
    cat_options.add_option("-d", "--debug", help="debug logging, specify any value to enable debug, omit this param to disable, example: --debug=False", default=False)
    cat_options.add_option("-c", "--cfg", help="configuration required by helper, KEY=VALUE format, example: -c $HOME/configs/service_discovery.cfg", default=None)
    cat_options.add_option("-x", "--exec", help="execute helper command, in format 'helpers/my_helper.my_method.  Method must always take only json file as argument / input", default="NOT_SPECIFIED")
    parser.add_option_group(cat_options)

    try: 
        opts, args = parser.parse_args(argv[1:])
    except Exception, e:
        sys.exit("ERROR: [%s]" % e)

    try:
        mainRun(opts, parser)
    except Exception, e:
        sys.exit("ERROR: [%s]" % e)


if __name__ == "__main__":
    logger.info("__main__ starting...")
    try:
        main()
    except Exception, e:
        sys.exit("ERROR: [%s]" % e)    