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
"""Pod spec for dns charm"""
import logging
from typing import Any, Dict, List
from IPy import IP

logger = logging.getLogger(__name__)

DNS_PORT = 53


def _make_pod_ports(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate pod ports details.

    Args:
        config Dict[str,Any]: Config details.

    Returns:
        List[Dict[str, Any]]: pod port details.
    """
    return [
        {"name": "dnstcp", "containerPort": config["dns_port"], "protocol": "TCP"},
        {"name": "dnsudp", "containerPort": config["dns_port"], "protocol": "UDP"},
    ]


def _make_pod_envconfig(
    relation: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate pod environment configuration.

    Args:
        config (Dict[str, Any]): configuration information.
        relation (Dict[str, Any]): relation state information.

    Returns:
        Dict[str, Any]: pod environment configuration.
    """
    return {
        # General configuration
        "PCSCF": relation["pcscf"],
        "ICSCF": relation["icscf"],
        "SCSCF": relation["scscf"],
        "HSS": relation["hss"],
    }


def _make_pod_command() -> List[str]:
    """Generate pod command.

    Returns:
        List[str]:pod command.
    """
    return ["./init_dns.sh", "&"]


def _validate_relation_state(relation_state: Dict[str, Any]):
    """Validate relation data.

    Args:
        relation (Dict[str, Any]): relation state information.
    """
    pcscf = relation_state.get("pcscf")
    icscf = relation_state.get("icscf")
    scscf = relation_state.get("scscf")
    hss = relation_state.get("hss")
    for host in pcscf, icscf, scscf, hss:
        if not IP(host):
            raise ValueError("Value error in host ip")


def _validate_config(config: Dict[str, Any]):
    """Validate config data.

    Args:
        config (Dict[str, Any]): configuration information.
    """
    if config.get("dns_port") != DNS_PORT:
        raise ValueError("Invalid dns port")


def make_pod_spec(
    image_info: Dict[str, str],
    config: Dict[str, str],
    app_name: str,
    relation: Dict[str, Any],
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
    if not image_info:
        return None

    _validate_config(config)
    _validate_relation_state(relation)
    ports = _make_pod_ports(config)
    env_config = _make_pod_envconfig(relation)
    command = _make_pod_command()
    return {
        "version": 3,
        "containers": [
            {
                "name": app_name,
                "image": image_info,
                "imagePullPolicy": "Always",
                "ports": ports,
                "envConfig": env_config,
                "command": command,
            }
        ],
    }
