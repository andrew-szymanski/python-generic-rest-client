python-rest-clients
=============

Collection of python REST clients for PoCs.  The idea is that they are all in the same repo, share the same cli and each client is just an additional py module.  This is just for quick turn around PoCs.

UNDER CONSTRUCTION


install from source
=============
cd $SOURCE;sudo pip install -e .


Config file
==============


Usage examples
==============
./cli/cli.py -d true -c ~/data/configs/service-discovery-client.cfg -j ~/data/configs/register.json -x helpers/service_discovery_helper.ServiceDiscoveryClient.register
./cli/cli.py -d Y -x helpers/datameer_helper.DatameerClient.get_jobs -c ./cli/datameer_client.cfg


create egg-info
=============
cd $mycode
python setup.py bdist_egg


restkit 
==============
https://github.com/benoitc/restkit
http://restkit.readthedocs.io/en/latest/index.html
