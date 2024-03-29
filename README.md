<!-- Copyright 2020 Tata Elxsi

 Licensed under the Apache License, Version 2.0 (the "License"); you may
 not use this file except in compliance with the License. You may obtain
 a copy of the License at

         http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
 WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 License for the specific language governing permissions and limitations
 under the License.

 For those usages not covered by the Apache License, Version 2.0 please
 contact: canonical@tataelxsi.onmicrosoft.com

 To get in touch with the maintainers, please contact:
 canonical@tataelxsi.onmicrosoft.com
-->

# 5G IMS Operators

5G IMS is used to deploy a standalone working 5G IMS setup. It is implemented
as microk8s applications using Juju Charms and Microk8s. It consists of the
following 6 IMS components as charms,

* pcscf: Proxy-Call Session Control Function stands as the entry and exit to any
  request to IMS
* icscf: Interrogating Call Session Control Function is the entity that selects
  the appropriate SCSCF during registration
* scscf: Serving-Call Session Control Function checks for the authentication
  data of UE
* hss: Home subscriber server maintains user profile and location details
* dns: Domain Name Service is a custom dns server for communication between IMS
  components
* mysql: Database of IMS for storing user profile and location data

## Usage

### Prepare environment

#### A. Install Microk8s

a. Install Microk8s using the following commands,

```bash
sudo snap install microk8s --classic --channel 1.19/stable
sudo usermod -a -G microk8s `whoami`
newgrp microk8s
microk8s.status --wait-ready
```

The ouput "microk8s is running" signifies that Microk8s is successfully installed.

b. Enable the following required addons for Microk8s to deploy 5G IMS

```bash
microk8s.enable storage dns
microk8s.enable multus
microk8s.enable rbac
microk8s.enable metallb
```

NOTE: 5G IMS requires 2 loadbalancer IP addresses mandatorily. So allocate 2
IP addresses while enabling metallb.

#### B. Install Juju

a. Install Juju with the following commands,

```bash
sudo snap install juju --classic --channel 2.8/stable
juju bootstrap microk8s
```

### Deploy

#### Deploy from local repository

a. Clone the 5G-IMS repository

```bash
git clone https://github.com/charmed-osm/5g-ims.git
cd 5g-ims/
```

b. Enable Microk8s registry for storing images
 
```bash
microk8s.enable registry
```

c. Build 5G IMS images

```bash
./build_docker_images.sh
```

d. Push built images to registry

```bash
sudo docker push localhost:32000/ims_pcscf:1.0
sudo docker push localhost:32000/ims_scscf:1.0
sudo docker push localhost:32000/ims_icscf:1.0
sudo docker push localhost:32000/ims_hss:1.0
sudo docker push localhost:32000/ims_dns:1.0
```

f. Execute the following script to build all the 5G IMS charms using Charmcraft,

```bash
./build_charms.sh
```

g. Create a model in Juju and deploy 5G IMS,

```bash
juju add-model ims
juju deploy ./bundle.yaml
```

h. Editing coredns,

```bash
microk8s.kubectl edit cm -n kube-system coredns
```

Add the following content in to coredns,

```bash
mnc001.mcc001.3gppnetwork.org:53 {
errors
cache 30
forward . <ims_dns_service_ip>
}
```

where ims_dns_service_ip is the Cluster service IP of DNS application.

To check logs in coredns,

```bash
microk8s.kubectl logs --namespace=kube-system -l k8s-app=kube-dns
```

Once the changes are updated successfully, “Reloading complete” can be seen in the logs.

### Integration

5G IMS exposes its following services as loadbalancer services in order to
facilitate IMS SIP calls.

* PCSCF TCP Service - To enable reachability to PCSCF service from extenal.
* HSS Service - To enable HSS GUI

In order to achieve this, 5G IMS needs 2 Loadbalancer services to be exposed
and published. This is done using,

```bash
microk8s.enable metallb
```

NOTE: 5G IMS requires 2 loadbalancer IP addresses mandatorily. Ignore this
step if already done in pre-requisites.

#### Juju Actions:

a. Action "add-user" is used to add users to ims,

```bash
juju run-action hss/0 add-user user=jack password=jack domain=mnc001.mcc001.3gppnetwork.org implicit=3 --wait
```

Where unit-id is the unit number, user and password can be given to be added to
ims, domain is the default domain available in ims, implicit id should be given
as unique per user.

b. Action "log-level", is used to change the log-levels. Debug-values can be
given from 2-5,

```bash
juju run-action pcscf/0 log-level debug=3 --wait
juju run-action scscf/0 log-level debug=3 --wait
juju run-action icscf/0 log-level debug=3 --wait
```

Where unit-id is the unit number of the respective unit and debug is the log
level that has to be set for PCSCF, SCSCF and ICSCF respectively.

Check for the status of the action in the output which should be "completed".

#### Actions Verification

a. Action “add-user” can be verified in MySQL application with the following,

Login to Mysql pod and execute the following commands,

```bash
mysql -u root -p root
use hss_db;
select * from impi;
```

Verify that the users added from actions are listed in the impi table.

b. Action "log-level" can be verified in ICSCF, SCSCF and PCSCF as follows,

Login to PCSCF/SCSCF/ICSCF pod, open the kamailio_pcscf.log or
kamailio_scscf.log or kamailio_pcscf.log file and check for the following line,

> “core.debug has been changed to 3"

Verify that the log-level given from action and the log level shown in the
above line are the same.

### 5G Scenarios

#### 5G User Registration

After 5G-Core(https://github.com/charmed-osm/5g-core) and
5G-RAN(https://github.com/charmed-osm/5g-ran) are deployed and
actions are completed, the user registration can be triggered through the
following rest API call with POST method,

```bash
http://ran-loadbalancerip:8081/attachtrigger/1
```

> Sample response for successful attach,
> Response Message: "Triggered Attach for the requested UE!"
> Response Code: 200 OK

#### Internet Traffic Flow

Once registration is successful, 5G-RAN's UE application would be enabled to
access the data network. Test the following in UE application,

a. ICMP TRAFFIC

```bash
ping 8.8.8.8
```

b. TCP TRAFFIC

```bash
wget google.com
```

c. UDP TRAFFIC

```bash
nc -u <netcat server-ip> port
```

where netcat server-ip is the IP address of the server where netcat server is
running.
Note: for UDP traffic netcat server should be running in another server. To do
that use the following commands in another server.

```bash
apt-get install netcat
nc -u -l -p <any unused port>
```

#### Voice Traffic Flow

Voice traffic flow can be tested once
5G-Core(https://github.com/charmed-osm/5g-core),
5G-RAN(https://github.com/charmed-osm/5g-ran) and 5G-IMS are deployed and
actions are completed. To test voice traffic flows, a SIP client called PJSIP is
already installed in the UE application. Follow the below steps in UE
application,

a. Traverse to /pjproject directory in the UE pod.

b. alice.cfg is configured for an user named alice which is already available
in IMS by default.

Note: The username, password and id can be changed to any user added from day-2
action of IMS as well.

c. Add the following content to /etc/hosts file,

> <PCSCF_LB_IP> mnc001.mcc001.3gppnetwork.org
> <PCSCF-LB_IP> pcscf.mnc001.mcc001.3gppnetwork.org

Where <PCSCF-LB_IP> is the loadbalancer IP of PCSCF application and
mnc001.mcc001.3gppnetwork.org is the domain added in coredns of IMS cluster.

d. Execute the following command to register the user alice with IMS,

```bash
pjsua --config-file alice.cfg --log-level=3
```

Note: Peform the above steps to register another user say bob with IMS so that SIP calls
can be tested between the two users. This has to be done in another UE pod. You can scale the
ue charm in RAN, enter to the pod, and in the alice.cfg file, replace "alice" with "bob".

e. After registration of both users, press ‘m’ from UE application's alice
and then press enter to initiate a SIP call.

f. Give bob’s id and then press enter. The message “Calling”
can be observed in alice’s UE pod.

g. Then in bob’s server, the following message can be seen,

> Press ‘a’ to answer or ‘h’ to hangup

h. Press a and then enter. Then the following message will be displayed,

> Answer with code:

i. Type 200 and enter.

j. After this “Confirmed” message can be seen in both alice and bob
indicating that the call between alice and bob is successful and that RTP
packets are being sent between alice and bob. The same can be verified by
capturing SIP packets using ngrep, tcpdump or wireshark.

k. Then to end/hangup the call, press h and then enter from alice. Verify the
“Disconnected” message in both alice and bob.

## Testing

Run Integration and Unit tests to test and verify the 5G IMS Charms.

### Integration tests

Functional tests for 5G IMS were created using zaza.

#### Install tox

```bash
apt-get install tox
```

#### Run Integration Test

To run zaza integration test,

```bash
tox -e func_test
```

This command will create a model, deploy the charms, run tests and destroy the
model

### Unit tests

Unit tests has to be executed in all the 5G IMS components/charms.
The following commands show how to perform unit test in PCSCF,

```bash
cd charms/pcscf-operator
./run_tests
```

Similarly, unit tests can be run for all the other components/charms.

## Get in touch

Found a bug?: <https://github.com/charmed-osm/5g-ims/issues>
Email: canonical@tataelxsi.onmicrosoft.com
