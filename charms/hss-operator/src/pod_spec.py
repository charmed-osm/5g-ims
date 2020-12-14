#!/usr/bin/env python3
# Copyright 2020 TataElxsi
# See LICENSE file for licensing details.
""" Pod spec for hss charm """

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)

HSS_PORT = 8080


def _make_pod_ports(config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate pod ports details.
    Args:
        config Dict[str,Any]: Config details.
    Returns:
        List[Dict[str, Any]]: pod port details.
    """
    if config["diameter_port"] == 3868:
        return [
            {
                "name": "diahss",
                "containerPort": config["diameter_port"],
                "protocol": "TCP",
            },
            {"name": "hss", "containerPort": HSS_PORT, "protocol": "TCP"},
        ]
    raise ValueError("Invalid diameter_port")


def _make_pod_envconfig() -> Dict[str, Any]:
    """Generate pod environment configuration.
    Returns:
        Dict[str, Any]: pod environment configuration.
    """
    envconfig = {
        # General configuration
        "MYSQL_HOST": "mysql-endpoints",
        "MYSQL_USER": "root",
        "MYSQL_ROOT_PASSWORD": "root",
    }

    return envconfig


def _make_pod_command() -> List[str]:
    return ["./init_hss.sh", "&"]


def make_pod_spec(
    image_info: Dict[str, str],
    config: Dict[str, str],
    app_name: str,
) -> Dict[str, Any]:
    """Generate the pod spec information.
    Args:
        image_info (Dict[str, str]): Object provided by
                                     OCIImageResource("image").fetch().
        config (Dict[str, Any]): Configuration information.
        app_name (str, optional): Application name. Defaults to "hss".
    Returns:
        Dict[str, Any]: Pod spec dictionary for the charm.
    """
    if not image_info:
        return None

    ports = _make_pod_ports(config)
    env_config = _make_pod_envconfig()
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
