python-rest-clients
=============

Collection of python REST clients for PoCs.  The idea is that they are all in the same repo, share the same cli and each client is just an additional py module.  This is just for quick turn around PoCs.

UNDER CONSTRUCTION

[README - datameer](../master/helpers/README-datameer.md)

run from source
=============
* checkout the code (say to path "$mycode")
* export PYTHONPATH=$mycode
* cd $mycode
* cli/cli.py

example:
```shell
export PYTHONPATH=~/data/code/github/python-rest-clients
cd ~/data/code/github/python-rest-clients
./cli/cli.py 
```


install from source
=============
instructions below purely as a guidelines - you may need to adjust for your case
```shell
git clone https://github.com/andrew-szymanski/python-rest-clients.git
virtualenv -p /usr/bin/python python-rest-clients
source python-rest-clients/bin/activate
cd python-rest-clients
pip install -e .
# use
# then deactivate virtualenv 
deactivate

```


Config file
==============


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
