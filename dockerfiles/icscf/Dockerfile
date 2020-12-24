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

COPY --from=builder /usr/lib/x86_64-linux-gnu/libicudata.so.60 /usr/lib/x86_64-linux-gnu/libicudata.so.60
COPY --from=builder /usr/lib/x86_64-linux-gnu/libicuuc.so.60 /usr/lib/x86_64-linux-gnu/libicuuc.so.60
COPY --from=builder /usr/lib/x86_64-linux-gnu/libmysqlclient.so.20 /usr/lib/x86_64-linux-gnu/libmysqlclient.so.20
COPY --from=builder /usr/lib/x86_64-linux-gnu/libxml2.so.2 /usr/lib/x86_64-linux-gnu/libxml2.so.2
COPY --from=builder /usr/lib/x86_64-linux-gnu/libssl.so.1.1 /usr/lib/x86_64-linux-gnu/libssl.so.1.1
COPY --from=builder /usr/lib/x86_64-linux-gnu/libcrypto.so.1.1 /usr/lib/x86_64-linux-gnu/libcrypto.so.1.1
COPY --from=builder /usr/local/src/kamailio/misc/examples/ims/icscf  /etc/kamailio_icscf
COPY --from=builder /usr/local/sbin/  /usr/local/sbin/
COPY --from=builder /usr/local/etc/kamailio/kamctlrc  /etc
COPY --from=builder /usr/local/lib64/kamailio  /usr/local/lib64/kamailio
COPY --from=builder /usr/local/share/kamailio/mysql /usr/local/share/kamailio/mysql

RUN apt-get update && apt-get install -y mysql-client-core-5.7 python3.8\
    && mkdir -p /var/run/kamailio \
    && mkdir -p /var/run/kamailio_icscf \
    && chmod 777 /var/run/kamailio_icscf \
    && chmod 777 /var/run/kamailio \
    && adduser --quiet --system --group --disabled-password \
        --shell /bin/false --gecos "Kamailio" \
        --home /var/run/kamailio kamailio
RUN chown kamailio:kamailio /var/run/kamailio

SHELL ["/bin/bash", "-c"]
RUN echo $'#!/bin/bash\n\
MYSQL_HOST=$(echo $MYSQL_HOST)\n\
MYSQL_USER=$(echo $MYSQL_USER)\n\
MYSQL_PWD=$(echo $MYSQL_ROOT_PASSWORD)\n\
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD -e "create database icscf"\n\
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD icscf < /etc/kamailio_icscf/icscf.sql\n\
mysql -D icscf -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD -e "INSERT INTO nds_trusted_domains VALUES (1,\'mnc001.mcc001.3gppnetwork.org\')"\n\
mysql -D icscf -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD -e "INSERT INTO s_cscf VALUES (1,\'First and only S-CSCF\',\'sip:scscf.mnc001.mcc001.3gppnetwork.org:6060\')"\n\
mysql -D icscf -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD -e "INSERT INTO s_cscf_capabilities VALUES (1,1,0),(2,1,1)"\n\
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD -e "grant delete,insert,select,update on icscf.* to icscf@localhost identified by \'heslo\'"\n\
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD -e "GRANT ALL PRIVILEGES ON icscf.* TO \'icscf\'@\'%\' identified by \'heslo\'"\n\
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD -e "grant delete,insert,select,update on icscf.* to provisioning@localhost identified by \'provi\'"\n\
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD -e "GRANT ALL PRIVILEGES ON icscf.* TO \'provisioning\'@\'%\' identified by \'provi\'"\n\
ipa=$(hostname -i|cut -f2 -d " ")\n\
find /etc/kamailio_icscf/icscf.xml -type f -exec sed -i "s/11.22.33.44/$ipa/g" {} \;\n\
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 2\n\
kamailio -f /etc/kamailio_icscf/kamailio.cfg -P /kamailio_icscf.pid -DD -E -e > kamailio_icscf.log 2>&1'> init_icscf.sh
RUN chmod +x init_icscf.sh
