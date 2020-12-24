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
"""Pod spec for mysql charm"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)
SQL_PORT = 3306


def _make_pod_ports(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate pod ports details.

    Args:
        config (Dict[str, Any]): configuration information.

    Returns:
        List[Dict[str, Any]]: pod port details.
    """
    return [{"name": "sql", "containerPort": config["sql_port"], "protocol": "TCP"}]


def _make_pod_envconfig() -> Dict[str, Any]:
    """Generate pod environment configuration.

    Returns:
        Dict[str, Any]: pod environment configuration.
    """
    return {
        # General configuration
        "MYSQL_ROOT_PASSWORD": "root"
    }


def _validate_config(config: Dict[str, Any]):
    """validate config data.

    Args:
        config Dict[str,Any]: Config details.
    """
    if config.get("sql_port") != SQL_PORT:
        raise ValueError("Invalid mysql port")


def make_pod_spec(
    image_info: Dict[str, str],
    config: Dict[str, str],
    app_name: str = "mysql",
) -> Dict[str, Any]:
    """Generate the pod spec information.

    Args:
        image_info (Dict[str, str]): Object provided by
                                     OCIImageResource("image").fetch().
        config (Dict[str, Any]): Configuration information.
        app_name (str, optional): Application name. Defaults to "pol".

    Returns:
        Dict[str, Any]: Pod spec dictionary for the charm.
    """
    if not image_info:
        return None

    _validate_config(config)
    ports = _make_pod_ports(config)
    env_config = _make_pod_envconfig()
    return {
        "version": 3,
        "containers": [
            {
                "name": app_name,
                "image": image_info,
                "imagePullPolicy": "Always",
                "ports": ports,
                "envConfig": env_config,
            }
        ],
    }
