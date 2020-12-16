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
# 5g-ims dockerfiles

The current directory holds the dockerfiles for IMS components

## description

consists of 2 base dockerfiles and 5 component dockerfiles

Base Dockerfiles:

* ims_base
* hss_base

Component Dockerfiles:

* pcscf
* icscf
* scscf
* hss
* dns

## Prerequisites

Build base images for ims and hss components with the given imagename and tag

sudo docker build -t ims:base -f ims_base
sudo docker build -t hss:base -f hss_base 

## Usage

Move into corresponding directory and build the images

Example:
   cd pcscf
   sudo docker build -t <image_name>:tag .

## Exposed Ports

----------------------------------------------------------
|     NF       |   Exposed Ports  | Dependencies         |        
----------------------------------------------------------
|   pcscf      |      4070        |   mysql              |
----------------------------------------------------------
|   icscf      |    4060,3869     |   mysql              |
----------------------------------------------------------
|   scscf      |    6060,3870     |   mysql              |
----------------------------------------------------------
|    hss       |    8080,3868     |   mysql              |
----------------------------------------------------------
|    dns       |       53         |pcscf,icscf,scscf,hss |
----------------------------------------------------------
