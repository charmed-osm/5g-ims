<!--
 Copyright 2020 Tata Elxsi

 Licensed under the Apache License, Version 2.0 (the License); you may
 not use this file except in compliance with the License. You may obtain
 a copy of the License at

         http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an AS IS BASIS, WITHOUT
 WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
 License for the specific language governing permissions and limitations
 under the License.

 For those usages not covered by the Apache License, Version 2.0 please
 contact: canonical@tataelxsi.onmicrosoft.com

 To get in touch with the maintainers, please contact:
 canonical@tataelxsi.onmicrosoft.com
-->

# HSS

## Description

Home Subscriber Subsystem maintains user profile and location details.

Contains action add-user to add an user to IMS.

## Prerequisite

a. Install Charmcraft

```bash
sudo snap install charmcraft --beta
```

## Usage

HSS is the application used to maintain the user profile and authentication
details. Other components in IMS connects with HSS if authentication details
needs to be verified.

### Deploy from local repository

```bash
charmcraft build
juju deploy ./hss.charm
```

NOTE: HSS can be deployed only after Mysql is up because of relations configured
between the two.

## Developing

To test add-user action,run the following command
COMMAND : sudo juju run-action hss/< UNIT-ID > add-user user=jack password=jack
domain=mnc001.mcc001.3gppnetwork.org implicit=3

Parameters values to be used are as follows,
user and password to be added to ims, domain is the default domain available in
ims and implicit id should be given as unique per user.

To check the status and output of the action ,use the following command

COMMAND:
juju show-action-status < ACTION-ID >
juju show-action-output < ACTION-ID >

Create and activate a virtualenv with the development requirements:

virtualenv -p python3 venv
source venv/bin/activate
pip install -r requirements-dev.txt

## Testing

The Python operator framework includes a very nice harness for testing
operator behaviour without full deployment. Just `run_tests`:

./run_tests
