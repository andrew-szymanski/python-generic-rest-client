datameer-rest-client
=============

Wrapper for Datameer REST APIs, currently focusing on export / import of artifacts (jobs etc)


Config file
==============
See [cli/datameer_client.cfg](../cli/datameer_client.cfg) for more info


Usage examples
==============
./cli/cli.py -d true -c ~/data/configs/service-discovery-client.cfg -j ~/data/configs/register.json -x helpers/service_discovery_helper.ServiceDiscoveryClient.register

./cli/cli.py -d Y -x helpers/datameer_helper.DatameerClient.export_artifacts -c ./cli/datameer_client.cfg


create egg-info
=============
cd $mycode

python setup.py bdist_egg


restkit 
==============
https://github.com/benoitc/restkit
http://restkit.readthedocs.io/en/latest/index.html
