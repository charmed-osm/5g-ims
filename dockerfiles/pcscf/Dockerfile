# Copyright 2020 Tata Elxsi
#
# Licensed under the Apache License, Version 2.0 (the License); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an AS IS BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# For those usages not covered by the Apache License, Version 2.0 please
# contact: canonical@tataelxsi.onmicrosoft.com
#
# To get in touch with the maintainers, please contact:
# canonical@tataelxsi.onmicrosoft.com
##

FROM ims:base AS builder
FROM ubuntu:18.04

RUN apt-get update && apt-get install -y mysql-client-core-5.7 python3.8 python3-pip && python3 -m pip install kubernetes==12.0.1 


COPY --from=builder /usr/lib/x86_64-linux-gnu/libmysqlclient.so.20 /usr/lib/x86_64-linux-gnu/libmysqlclient.so.20
COPY --from=builder /usr/lib/x86_64-linux-gnu/libxml2.so.2 /usr/lib/x86_64-linux-gnu/libxml2.so.2
COPY --from=builder /lib/x86_64-linux-gnu/libmnl.so.0 /lib/x86_64-linux-gnu/libmnl.so.0
COPY --from=builder /usr/local/src/kamailio/misc/examples/ims/pcscf  /etc/kamailio_pcscf
COPY --from=builder /usr/local/sbin/  /usr/local/sbin/
COPY --from=builder /usr/local/etc/kamailio/kamctlrc  /etc/kamailio/
COPY --from=builder /usr/local/lib64/kamailio  /usr/local/lib64/kamailio
COPY --from=builder /usr/local/share/kamailio/mysql /usr/local/share/kamailio/mysql

RUN mkdir -p /var/run/kamailio \
    && mkdir -p /var/run/kamailio_pcscf \
    && chmod 777 /var/run/kamailio_pcscf \
    && chmod 777 /var/run/kamailio \
    && adduser --quiet --system --group --disabled-password \
        --shell /bin/false --gecos "Kamailio" \
        --home /var/run/kamailio kamailio
RUN chown kamailio:kamailio /var/run/kamailio

RUN echo "import sys\n\
import os\n\
from kubernetes import client, config\n\
config.load_incluster_config()\n\
c=client.CoreV1Api()\n\
result=c.list_namespaced_service(sys.argv[1])\n\
for ip in result.items:\n\
    if(ip.metadata.name == 'pcscf'):\n\
        lbip = ip.status.load_balancer.ingress[0]\n\
        print(lbip.ip)\n\
        cmd = 'sed -i \"s/lbip/{}/g\" /etc/kamailio_pcscf/pcscf.cfg'.format(lbip.ip)\n\
        os.system(cmd)"> fetchlbip.py
RUN chmod +x fetchlbip.py

SHELL ["/bin/bash", "-c"]
RUN echo $'#!/bin/bash\n\
MYSQL_HOST=$(echo $MYSQL_HOST)\n\
MYSQL_USER=$(echo $MYSQL_USER)\n\
MYSQL_PWD=$(echo $MYSQL_ROOT_PASSWORD)\n\
echo "DBHOST=$MYSQL_HOST"  >> /etc/kamailio/kamctlrc\n\
echo root | kamdbctl create\n\
mysql_pwd="/usr/local/share/kamailio/mysql"\n\
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD -e "create database pcscf"\n\
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD pcscf < ${mysql_pwd}/standard-create.sql\n\
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD pcscf < ${mysql_pwd}/presence-create.sql\n\
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD pcscf < ${mysql_pwd}/ims_usrloc_pcscf-create.sql\n\
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD pcscf < ${mysql_pwd}/ims_dialog-create.sql\n\
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD -e "grant delete,insert,select,update on pcscf.* to pcscf@localhost identified by \'pcscf\'"\n\
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD -e "GRANT ALL PRIVILEGES ON pcscf.* TO \'pcscf\'@\'%\' identified by \'heslo\'"\n\
lbip=$(echo $MODEL)\n\
python3 fetchlbip.py $lbip\n\
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 2\n\
kamailio -f /etc/kamailio_pcscf/kamailio.cfg -P /kamailio_pcscf.pid -DD -E -e > kamailio_pcscf.log 2>&1' > init_pcscf.sh
RUN chmod +x init_pcscf.sh
