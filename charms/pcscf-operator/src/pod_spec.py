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
"""Pod spec for pcscf charm"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
PCSCF_PORT = 4070


def _make_pod_ports(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate pod ports details.

    Args:
        Config[str, Any]: Configuration details.

    Returns:
        List[Dict[str, Any]]: pod port details.
    """
    return [{"name": "pcscf", "containerPort": config["pcscf_port"], "protocol": "TCP"}]


def _make_pod_envconfig(
    model_name: str, relation_state: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate pod environment configuration.

    Args:
        model_name (str): model name.

    Returns:
        Dict[str, Any]: pod environment configuration.
    """
    mysql_db = relation_state["db"]
    endpoints = f"{mysql_db}-endpoints"
    return {
        # General configuration
        "MODEL": model_name,
        "MYSQL_HOST": endpoints,
        "MYSQL_USER": relation_state["user"],
        "MYSQL_ROOT_PASSWORD": relation_state["pwd"],
    }


def _make_pod_command() -> List[str]:
    """Generate pod command.

    Returns:
        List[str]: pod command.
    """
    return ["./init_pcscf.sh", "&"]


def _make_pod_services():
    """Generate pod services."""
    return [
        {
            "rules": [
                {
                    "apiGroups": [""],
                    "resources": ["services"],
                    "verbs": ["get", "watch", "list"],
                }
            ]
        }
    ]


def _validate_config(config: Dict[str, Any]):
    """validate config data.

    Args:
        config Dict[str,Any]: Config details.
    """
    if config.get("pcscf_port") != PCSCF_PORT:
        raise ValueError("Invalid pcscf port")


def _validate_relation_state(relation_state: Dict[str, Any]):
    """Validate relation data.

    Args:
        relation (Dict[str, Any]): relation state information.
    """
    app = relation_state.get("db")
    user = relation_state.get("user")
    password = relation_state.get("pwd")
    if not app or not user.__eq__("root") or not password.__eq__("root"):
        raise ValueError("Value error in mysql relations")


def make_pod_spec(
    image_info: Dict[str, str],
    model_name: str,
    config: Dict[str, str],
    app_name: str,
    relation_state: Dict[str, Any],
) -> Dict[str, Any]:
    """Generate the pod spec information.

    Args:
        image_info (Dict[str, str]): Object provided by
                                     OCIImageResource("image").fetch().
        config (Dict[str, Any]): Configuration information.
        model_name (str): Model name.
        app_name (str, optional): Application name. Defaults to "pol".

    Returns:
        Dict[str, Any]: Pod spec dictionary for the charm.
    """
    if not image_info:
        return None
    logger.info("Pcscf pod spec")

    _validate_config(config)
    _validate_relation_state(relation_state)
    ports = _make_pod_ports(config)
    env_config = _make_pod_envconfig(model_name, relation_state)
    command = _make_pod_command()
    services = _make_pod_services()

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
        "serviceAccount": {"automountServiceAccountToken": True, "roles": services},
    }
