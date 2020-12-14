FROM ims:base AS builder
FROM ubuntu:18.04

COPY --from=builder /usr/lib/x86_64-linux-gnu/libmysqlclient.so.20 /usr/lib/x86_64-linux-gnu/libmysqlclient.so.20
COPY --from=builder /usr/lib/x86_64-linux-gnu/libxml2.so.2 /usr/lib/x86_64-linux-gnu/libxml2.so.2
COPY --from=builder /usr/lib/x86_64-linux-gnu/libicuuc.so.60 /usr/lib/x86_64-linux-gnu/libicuuc.so.60
COPY --from=builder /usr/lib/x86_64-linux-gnu/libicudata.so.60 /usr/lib/x86_64-linux-gnu/libicudata.so.60
COPY --from=builder /usr/lib/x86_64-linux-gnu/libssl.so.1.1 /usr/lib/x86_64-linux-gnu/libssl.so.1.1
COPY --from=builder /usr/lib/x86_64-linux-gnu/libcrypto.so.1.1 /usr/lib/x86_64-linux-gnu/libcrypto.so.1.1
COPY --from=builder /usr/local/src/kamailio/misc/examples/ims/scscf  /etc/kamailio_scscf
COPY --from=builder /usr/local/sbin/  /usr/local/sbin/
COPY --from=builder /usr/local/lib64/kamailio  /usr/local/lib64/kamailio
COPY --from=builder /usr/local/share/kamailio/mysql /usr/local/share/kamailio/mysql

RUN apt-get update && apt-get install -y mysql-client-core-5.7 python3.8\
    && mkdir -p /var/run/kamailio \
    && mkdir -p /var/run/kamailio_scscf \
    && chmod 777 /var/run/kamailio_scscf \
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
mysql_pwd="/usr/local/share/kamailio/mysql"\n\
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD -e "create database scscf"\n\
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD scscf < ${mysql_pwd}/standard-create.sql\n\
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD scscf < ${mysql_pwd}/presence-create.sql\n\
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD scscf < ${mysql_pwd}/ims_usrloc_scscf-create.sql\n\
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD scscf < ${mysql_pwd}/ims_dialog-create.sql\n\
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD scscf < ${mysql_pwd}/ims_charging-create.sql\n\
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD -e "grant delete,insert,select,update on scscf.* to scscf@localhost identified by \'heslo\'"\n\
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD -e "GRANT ALL PRIVILEGES ON scscf.* TO \'scscf\'@\'%\' identified by \'heslo\'"\n\
mysql -h $MYSQL_HOST -u $MYSQL_USER -p$MYSQL_PWD -e "FLUSH PRIVILEGES"\n\
ipa=$(hostname -i|cut -f2 -d " ")\n\
find /etc/kamailio_scscf/scscf.xml -type f -exec sed -i "s/11.22.33.44/$ipa/g" {} \;\n\
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 2\n\
kamailio -f /etc/kamailio_scscf/kamailio.cfg -P /kamailio_scscf.pid -DD -E -e > kamailio_scscf.log 2>&1'> init_scscf.sh
RUN chmod +x init_scscf.sh

