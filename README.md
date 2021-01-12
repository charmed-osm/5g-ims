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

- pcscf: Proxy-Call Session Control Function stands as the entry and exit to any
  request to IMS
- icscf: Interrogating Call Session Control Function is the entity that selects
  the appropriate SCSCF during registration
- scscf: Serving-Call Session Control Function checks for the authentication
  data of UE
- hss: Home subscriber server maintains user profile and location details
- dns: Domain Name Service is a custom dns server for communication between IMS
  components
- mysql: Database of IMS for storing user profile and location data

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
```

#### B. Install Juju

a. Install Juju with the following commands,

```bash
sudo snap install juju --classic --channel 2.8/stable
juju bootstrap microk8s
```

### Deploy

To deploy 5G IMS from Charmstore, use the following command

```bash
juju deploy cs:~tata-charmers/ims
```

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
docker push localhost:32000/ims_pcscf:1.0
docker push localhost:32000/ims_scscf:1.0
docker push localhost:32000/ims_icscf:1.0
docker push localhost:32000/ims_hss:1.0
docker push localhost:32000/ims_dns:1.0
```

e. Check image reference in IMS charms

The following steps have to performed in all IMS charms to ensure that the
charms have the right image reference. The following is an example to check in
pcscf-operator charm.

```bash
//open config.yaml file
vi charms/pcscf-operator/config.yaml
```

Ensure that the image referred in the config.yaml is same as the one
pushed in last step.

f. Execute the following script to build all the 5G IMS charms using Charmcraft,

```bash
./build_charms.sh
```

g. Create a model in Juju and deploy 5G IMS,

```bash
juju add-model 5g-ims
juju deploy ./bundle.yaml
```

### Integration

5G IMS exposes its following services as loadbalancer services in order to
facilitate IMS SIP calls.

- PCSCF TCP Service - To enable reachability to PCSCF service from extenal.
- HSS Service - To enable HSS GUI

In order to achieve this, 5G IMS needs 2 Loadbalancer services to be exposed
and published. This is done using,

```bash
microk8s.enable metallb
```

NOTE: 5G IMS requires 2 loadbalancer IP addresses mandatorily.

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
