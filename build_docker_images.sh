#!/bin/bash
# Copyright 2020 Tata Elxsi
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# For those usages not covered by the Apache License, Version 2.0 please
# contact: canonical@tataelxsi.onmicrosoft.com
#
# To get in touch with the maintainers, please contact:
# canonical@tataelxsi.onmicrosoft.com
ims_components="dns hss icscf pcscf scscf"
dir=dockerfiles
if [ -z `which docker` ]; then
    sudo apt-get update
    sudo apt-get install -y docker.io
fi
cd $dir
echo "Building base images for IMS"
sudo docker build -t ims:base -f ims_base .
sudo docker build -t hss:base -f hss_base .
for component in $ims_components; do
    echo "Building image for $component..."
    cd $component
    sudo docker build -t localhost:32000/ims_$component:1.0 .
    cd ..
done
sudo docker images | grep "localhost:32000/ims_"
