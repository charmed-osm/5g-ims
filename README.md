# 5G IMS Operators

Contains charm folder consisting of 6 k8s charm applications


## Description

Consists of 6 applications
* pcscf
* icscf
* scscf
* hss
* dns
* mysql

## Usage
Build

sudo snap install charmcraft --beta

cd Application-operator

charmcraft build

Deploy

juju deploy ./juju-bundles/bundle.yaml

### Integration

IMS integration with 5g-core happens using the loadbalancer service in pcscf application for default pdn

