#!/usr/bin/env python3
# Copyright 2020 Tata Elxsi
#
# Licensed under the Apache License, Version 2.0 (the License); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an AS IS BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# For those usages not covered by the Apache License, Version 2.0 please
# contact: canonical@tataelxsi.onmicrosoft.com
#
# To get in touch with the maintainers, please contact:
# canonical@tataelxsi.onmicrosoft.com
##
""" Pod spec for dns charm """
import logging
from typing import Any, Dict, List
from IPy import IP

logger = logging.getLogger(__name__)


def _make_pod_ports(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate pod ports details.
    Args:
        config Dict[str,Any]: Config details.
    Returns:
        List[Dict[str, Any]]: pod port details.
    """
    if config["dns_port"] == 53:
        return [
            {"name": "dnstcp", "containerPort": config["dns_port"], "protocol": "TCP"},
            {"name": "dnsudp", "containerPort": config["dns_port"], "protocol": "UDP"},
        ]
    raise ValueError("Invalid dns_port")


def _validate_relation_data(relation_state: Dict[str, Any]) -> bool:
    """Validate relation data.
    Args:
        relation (Dict[str, Any]): relation state information.
    Returns:
        bool: True or False
    """
    if IP(relation_state["pcscf"]):
        if IP(relation_state["icscf"]):
            if IP(relation_state["scscf"]):
                if IP(relation_state["hss"]):
                    return True
    return False


def _make_pod_envconfig(
    hosts: List[str],
) -> Dict[str, Any]:
    """Generate pod environment configuration.
    Args:
        config (Dict[str, Any]): configuration information.
        relation (Dict[str, Any]): relation state information.
    Returns:
        Dict[str, Any]: pod environment configuration.
    """
    return {
        "HOSTS": ",".join(hosts),
    }


def _make_pod_command() -> List[str]:
    return ["./init_dns.sh", "&"]


def make_pod_spec(
    image_info: Dict[str, str],
    config: Dict[str, str],
    app_name: str,
    hosts: List[str],
) -> Dict[str, Any]:
    """Generate the pod spec information.
    Args:
        image_info (Dict[str, str]): Object provided by
                                     OCIImageResource("image").fetch().
        config (Dict[str, Any]): Configuration information.
        relation (Dict[str, Any]): Relation state information.
        app_name (str, optional): Application name.
    Returns:
        Dict[str, Any]: Pod spec dictionary for the charm.
    """
    logger.info("*******Check in pod_spec*********")
    # ADD VALIDATION
    ports = _make_pod_ports(config)
    env_config = _make_pod_envconfig(hosts)
    command = _make_pod_command()
    return {
        "version": 3,
        "containers": [
            {
                "name": app_name,
                "imageDetails": image_info,
                "imagePullPolicy": "Always",
                "ports": ports,
                "envConfig": env_config,
                "command": command,
            }
        ],
    }
