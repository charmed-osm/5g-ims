FROM ims:base AS builder
FROM ubuntu:18.04

RUN apt-get update && apt-get install -y bind9
COPY --from=builder /usr/local/src/kamailio/misc/examples/ims/ims_dnszone/mnc001.mcc001.3gppnetwork.org  /etc/bind/mnc001.mcc001.3gppnetwork.org

SHELL ["/bin/bash", "-c"]
RUN echo $'zone "mnc001.mcc001.3gppnetwork.org" {\n\
                 type master;\n\
                 file "/etc/bind/mnc001.mcc001.3gppnetwork.org";\n\
};' >> /etc/bind/named.conf.local

RUN echo $'#!/bin/bash\n\
find /etc/bind/mnc001.mcc001.3gppnetwork.org -type f -exec sed -i "s/5060/4070/g" {} \;\n\
sed -i \'/_sip._udp.ims/d\' /etc/bind/mnc001.mcc001.3gppnetwork.org\n\
sed -i \'/_sip._tcp.ims/d\' /etc/bind/mnc001.mcc001.3gppnetwork.org\n\
nsip=$(hostname -i|cut -f2 -d " ")\n\
pcscfip=$(echo $PCSCF)\n\
icscfip=$(echo $ICSCF)\n\
scscfip=$(echo $SCSCF)\n\
hssip=$(echo $HSS)\n\
sed  -i "/ns/ s/127.0.0.1/$nsip/; /pcscf/ s/127.0.0.1/$pcscfip/; /icscf/ s/127.0.0.1/$icscfip/; /scscf/ s/127.0.0.1/$scscfip/; /hss/ s/127.0.0.1/$hssip/;" /etc/bind/mnc001.mcc001.3gppnetwork.org \n\
/usr/sbin/named -u bind -g -d 1 > dns.log 2>&1' > init_dns.sh
RUN chmod +x init_dns.sh
EXPOSE 53
