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

FROM hss:base AS builder
FROM ubuntu:18.04
RUN  apt-get update && apt install -y mysql-client-core-5.7 openjdk-8-jdk python3.8 && mkdir -p /usr/lib/jvm
WORKDIR /opt/OpenIMSCore/FHoSS
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
COPY --from=builder /opt/OpenIMSCore/FHoSS  ./
WORKDIR /opt/OpenIMSCore/FHoSS/deploy

SHELL ["/bin/bash","-c"]
RUN echo $'#!/bin/bash\n\
MYSQL_HOST=$(echo $MYSQL_HOST)\n\
MYSQL_USER=$(echo $MYSQL_USER)\n\
MYSQL_PWD=$(echo $MYSQL_ROOT_PASSWORD)\n\
ipa=$(hostname -i|cut -f2 -d " ")\n\
find /opt/OpenIMSCore/FHoSS/deploy/DiameterPeerHSS.xml -type f -exec sed -i "s/127.0.0.1/$ipa/g" {} \;\n\
find /opt/OpenIMSCore/FHoSS/ -type f -exec sed -i "s/"open-ims.test"/"mnc001.mcc001.3gppnetwork.org"/g" {} \;\n\
find /opt/OpenIMSCore/FHoSS/ -type f -exec sed -i "s/"open-ims.org"/"mnc001.mcc001.3gppnetwork.org"/g" {} \;\n\
find /opt/OpenIMSCore/FHoSS/deploy/hibernate.properties -type f -exec sed -i "s/127.0.0.1/"mysql-endpoints"/g" {} \;\n\
find /opt/OpenIMSCore/FHoSS/deploy/hss.properties -type f -exec sed -i "s/127.0.0.1/0.0.0.0/g" {} \;\n\
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD -e "create database hss_db"\n\
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD hss_db < /opt/OpenIMSCore/FHoSS/scripts/hss_db.sql\n\
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD hss_db < /opt/OpenIMSCore/FHoSS/scripts/userdata.sql\n\
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD -e "grant delete,insert,select,update on hss_db.* to hss@localhost identified by \'hss\'"\n\
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD -e "grant delete,insert,select,update on hss_db.* to \'hss\'@\'%\' identified by \'hss\'"\n\
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 2\n\
cd /opt/OpenIMSCore/FHoSS/deploy \n\
./startup.sh > /var/log/hss.log 2>&1\n\
while true; do sleep 1000; done' > /init_hss.sh
RUN chmod +x startup.sh && chmod +x /init_hss.sh
WORKDIR /


EXPOSE 8080


