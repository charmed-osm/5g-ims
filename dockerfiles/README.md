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

# 5g-ims Dockerfiles

The current directory holds the dockerfiles for IMS components

## Description

Consists of 2 base dockerfiles and 5 component dockerfiles

### Base Dockerfiles

Used to build the ims base images. These image would be used as base images to
build all the IMS components.

* ims_base
* hss_base

Component Dockerfiles:

* pcscf
* icscf
* scscf
* hss
* dns

## Usage

To build images of all the 5G IMS Components,

```bash
cd ..
./build_docker_images.sh
```

To push the built images to registry,

```bash
docker push localhost:32000/ims_pcscf:1.0
docker push localhost:32000/ims_scscf:1.0
docker push localhost:32000/ims_icscf:1.0
docker push localhost:32000/ims_hss:1.0
docker push localhost:32000/ims_dns:1.0
```

## Exposed Ports

---

## | NF | Exposed Ports | Dependencies |

## | pcscf | 4070 | mysql |

## | icscf | 4060,3869 | mysql |

## | scscf | 6060,3870 | mysql |

## | hss | 8080,3868 | mysql |

## | dns | 53 |pcscf,icscf,scscf,hss |
