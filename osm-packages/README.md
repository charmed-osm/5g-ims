<!--
Copyright 2020 Tata Elxsi

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

# To build charms

* Build the charms enter into 5g-ims

  run ./build_charms.sh

    The charms will be built, build and .charm can be located
    in respective operators inside charms directory.
Eg: build and dns.charm in 5g-ims/charms/dns-operator,
    similarly in all charms it can be found.

# Create and Onboard 5g-ims osm packages

> To create osm vnf and ns packages, use the following commands which will
generate a vnf package structure named ims_vnf and ns package structure named ims_ns

```bash
osm package-create vnf ims
osm package-create ns ims
```

> Copy the desriptor into corresponding directory

```bash
cp ims_vnfd.yaml ims_vnf/
cp ims_nsd.yaml ims_ns/
```

> Place charms in tha package,

```bash
mkdir -p "ims_vnf/charms/dns-operator" &&
cp -rf ../charms/dns-operator/build "ims_vnf/charms/dns-operator"
```

Similarly, Copy the remaining charms(hss-operator, icscf-operator,
mysql-operator, pcscf-operator, scscf-operator) aswell.

> Copy the bundle into package.

```bash
mkdir -p "ims_vnf/juju-bundles" && cp bundle.yaml "ims_vnf/juju-bundles"
```

> Package the descriptors

```bash
tar -cvzf ims_vnf.tar.gz ims_vnf/
tar -cvzf ims_ns.tar.gz ims_ns/
```

> To onboard packages into OSM, use the following commands

```bash
osm nfpkg-create ims_vnf.tar.gz
osm nspkg-create ims_ns.tar.gz
```

> Onboarded packages can be verified with the following commands

```bash
osm nfpkg-list
osm nspkg-list
```

# Adding vim-account and k8scluster to OSM

## Vim-Account

```bash
osm vim-create --name <vim_name> --user <username> --password <password> --auth_url
<openstack-url> --tenant <tenant_name> --account_type openstack
```

vim-create command helps to add vim to OSM where,

* "vim_name" is the name of the vim being created.
* "username"and "password" are the credentials of Openstack.
* "tenant_name" is the tenant to be associated to the user in the Openstack.
* "openstack-url" is the URL of Openstack which will be used as VIM

## K8sCluster

```bash
osm k8scluster-add --creds <kube.yaml> --version '1.19' --vim <vim_name>
--description "IMS Cluster" --k8s-nets '{"net1": "<network-name>"}' <cluster_name>
```

K8scluster add helps to attach a cluster with OSM which will be used for knf deployment.
where

* "kube.yaml" is the configuration of microk8s cluster obtained from "microk8s config>kube.yaml".

* "vim_name" is the vim created in the last setup.

* "cluster_name" a unique name to identify your cluster.

Note: [Prerequisites and microk8s setup for 5g-core](../README.md)

# Launching the ims

```bash
osm ns-create --ns_name ims --nsd_name ims_nsd --vim_account <vim_name>
```

> ns-create will instantiate the ims network service,
use "vim_name" thats added to osm.

## Verifying the services

```bash
osm ns-list
```

> Will display the ns-created with ns-id, with status active and configured
which means the service is up along with its day1 operations.

```bash
osm ns-show
```

> Will show detailed information of the network service.

```bash
microk8s kubectl get all –n ims-kdu-<ns-id>
```

> will display components deployed from bundle in vnfd.

* Once the deployment happens, the following change should be done in the
  cluster for ims domain.
  Obtain the ims dns service_ip that is launched as part of ims-kdu-<ns-id\>

```
Editing coredns:
microk8s.kubectl edit cm -n kube-system coredns
mnc001.mcc001.3gppnetwork.org:53 {
       errors
       cache 30
       forward . <ims dns service_ip>
    }

To check logs  in coredns:
microk8s.kubectl logs --namespace=kube-system -l k8s-app=kube-dns
```

## 5g-ims day2 operation

> To add user to ims

```
osm ns-action ims --vnf_name 1 --kdu_name ims-kdu --action_name add-user --params
'{application-name: hss,user: jack,
password: jack,
domain: mnc001.mcc001.3gppnetwork.org,
implicit: 3}'
```

where

* "ims" refers to the network service name,"1" points to vnf member index and
  "ims-kdu" is the kdu name used in package.
* Parameters values to be used are as follows,a user and
  password to be added to ims,domain is the default domain available in ims,
  implicit id should be given as unique per user.
> To delete user from ims

```
osm ns-action ims --vnf_name 1 --kdu_name ims-kdu --action_name delete-user --params
'{application-name: hss,user: jack,password: jack,domain: mnc001.mcc001.3gppnetwork.org}'
```

where

* "ims" refers to the network service name,"1" points to vnf member index
   and "ims-kdu" is the kdu name used in package.

* Parameters values to be used are as follows,
  a user and password to be deleted from ims,
  domain is the default domain available in ims

> To change logs

```
osm ns-action ims --vnf_name 1 --kdu_name ims-kdu
    --action_name log-level --params '{application-name: pcscf,debug: 3}'
osm ns-action ims --vnf_name 1 --kdu_name ims-kdu
    --action_name log-level --params '{application-name: icscf,debug: 3}'
osm ns-action ims --vnf_name 1 --kdu_name ims-kdu
    --action_name log-level --params '{application-name: scscf,debug: 3}'
```

where

* "ims" refers to the network service name,"1" points to vnf member index
   and "ims-kdu" is the kdu name used in package.

* Parameters values to be used are as follows,debug whose value can range from 2-5.
