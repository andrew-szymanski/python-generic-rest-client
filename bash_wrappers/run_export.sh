#!/bin/bash

#                      *************************
#                      **** 
#                      **** Script for local testing / debugging
#                      **** you must run this script specifying FULL path to it
#                      **** eg: /home/$USER/data/code/bitbucket/big/bigdata-datameer/rpm/datameer-python-rest-client/examples/run_export.sh
#                      **** 
#                      **** you will also need to create env file for yourself in 'examples' dir
#                      **** (where this script is)
#                      *************************

log() {
    date "+%m-%d:%H:%M:%S $*" 
}

virtualenv-recreate() {
   virtualenv -p /usr/bin/python ${VIRTUAL_ENV_DIR}
   RC=$?
   if [ $RC -ne 0 ]; then
      log "ERROR: creating virtualenv FAILED, exiting"
      exit 1
   fi
   source ${VIRTUAL_ENV_DIR}/bin/activate
   RC=$?
   if [ $RC -ne 0 ]; then
      log "ERROR: activating virtualenv [{VIRTUAL_ENV_DIR}] FAILED, exiting"
      exit 1
   fi   
   # change to root dir of python REST client
   # and install dependencies in virtualenv
   PYTHON_DEPENDENCIES_FILE=${REST_CLIENT_DIR}/datameer_python_rest_client.egg-info/requires.txt
   log "installing python dependencies listed in: [${PYTHON_DEPENDENCIES_FILE}]...."
   pip install -r ${PYTHON_DEPENDENCIES_FILE} -i https://pypi.unibet.com/root/pypi
   RC=$?
   if [ $RC -ne 0 ]; then
      log "ERROR: installing dependencies in: [${PYTHON_DEPENDENCIES_FILE}] FAILED, exiting"
      exit 1
   fi   
}


#                      *************************
#                      **** MAIN
#                      *************************
###
### 
###
log "$0 starting..."
ERRORS=0

# get directories
REST_CLIENT_DIR=$(dirname $(dirname ${BASH_SOURCE[0]}))
log "REST_CLIENT_DIR: [${REST_CLIENT_DIR}]"

# 
ENV_FILE=${REST_CLIENT_DIR}/examples/$USER.env
log "ENV_FILE: [${ENV_FILE}]"
if [ ! -f ${ENV_FILE} ]; then
  log "ERROR: ENV_FILE: [${ENV_FILE}] not found"
  exit 1
fi


log "sourcing [${ENV_FILE}] file..."
. ${ENV_FILE}
log "sourcing [${ENV_FILE}] DONE"


# validate env vars set
ENV_VARIABLES="DATAMEER_USER DATAMEER_PASSWORD VIRTUAL_ENV_DIR"
ERROR=0
for ENV_VAR in ${ENV_VARIABLES}; do
   VALUE=${!ENV_VAR}
   log "   $ENV_VAR: [$VALUE]"
   if [ -z "${VALUE}" ]; then
      log "ERROR: variable [$ENV_VAR] not defined, check [${ENV_FILE}] env file"
      ERROR=1
   fi
done
if [ $ERROR -ne 0 ]; then
   log "ERROR: some of required env variables not defined (see above)"
   exit 1
fi


log "                      *************************"
log "                      **** check virtualenv"
log "                      *************************"
log "checking virtualenv [${VIRTUAL_ENV_DIR}] exists"


# delete virtualenv if exists already (so we have clean setup)
if [ ! -d "${VIRTUAL_ENV_DIR}" ]; then
   log "WARNING: [${VIRTUAL_ENV_DIR}] DOES NOT exists - recreating"
   virtualenv-recreate
fi

log "activating virtualenv [${VIRTUAL_ENV_DIR}]"
source ${VIRTUAL_ENV_DIR}/bin/activate
RC=$?
if [ $RC -ne 0 ]; then
 log "ERROR: activating virtualenv [{VIRTUAL_ENV_DIR}] FAILED, exiting"
 exit 1
fi
which python


log "                      *************************"
log "                      **** run export"
log "                      *************************"
cd ${REST_CLIENT_DIR}
CMD="./cli/cli.py -d Y -x helpers/datameer_helper.DatameerClient.export_artifacts -c ./cli/datameer_client.cfg"
$CMD
RC=$?
if [ $RC -ne 0 ]; then
 log "ERROR: export command FAILED, exiting"
 exit 1
fi



