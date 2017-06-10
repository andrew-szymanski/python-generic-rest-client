__author__ = "Andrew Szymanski ()"
__version__ = "0.1.0"

"""
"""


import logging
import os
import inspect

# constants
LOG_INDENT = "  "        # to prettify logs


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
        self.uri = None

    def configure(self, *args, **kwargs):
        """ grab and validate config
        """
        self.logger.debug("%s::%s starting..." %  (self.__class__.__name__ , inspect.stack()[0][3]))         
        config_file = kwargs.get('cfg',None)
        self.logger.debug("%s: [%s]" % ("config_file", config_file))





        


