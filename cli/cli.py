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
   mname = mname.replace('.py','')
   

   if os.path.exists(uri):
      try:
            return imp.load_source(mname, uri)
      except Exception, e:
            raise Exception("ERROR: failed to load module: [%s] from file: [%s], error: [%s]" % (mname,uri,e))

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
      

      


   def execute(self, *args, **kwargs):
      """ Grab and validate all input params
      Will throw Exception on error(s)
      """
      self.logger.debug("%s::%s starting..." %  (self.__class__.__name__ , inspect.stack()[0][3])) 
      
      # import specified helper module
      helper_module_arg = kwargs.get('exec')
 
      # split method from module.class
      helper_class,helper_method = helper_module_arg.rsplit(".",1)
      self.logger.debug("importing class: [%s], method: [%s]" % (helper_class,helper_method))

      klass = self.import_class(helper_class)
      my_instance = klass(logger=self.logger)
      
      # execute specified method
      getattr(my_instance, helper_method)(args, kwargs)


      
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
      module_full_path = "%s/%s.py" % (this_project_dir,module_path)
      self.logger.debug("  module: [%s], class: [%s]" % (module_full_path,class_name))
      
      # import module
      helper_module_imported = importFromURI(module_full_path)
      if not helper_module_imported:
         raise Exception("ERROR: Failed to dynamically load module [%s], error: [%s]" % (module_full_path,e))
 
      # and import class
      my_class = getattr(helper_module_imported, class_name)
      return my_class
      #d = class_name.rfind(".")
      #classname = class_name[d+1:len(class_name)]
      #m = __import__(class_name[0:d], globals(), locals(), [classname])
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
        # execute specified class method
        mngr.execute(**opts.__dict__)   
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
# 
# ./cli/cli.py -d true -c /Users/andszy/data/configs/service-discovery-client.cfg -x helpers/service_discovery_helper.ServiceDiscoveryClient.register

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