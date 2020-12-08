#!/usr/bin/env python3
# Copyright 2020 TataElxsi
# See LICENSE file for licensing details.

import logging
from pydantic import BaseModel, validator, PositiveInt
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class ConfigData(BaseModel):
    """Configuration data model."""

    pcscfport: PositiveInt = 4070

    @validator("pcscfport")
    def validate_pcscfport(cls, value: int) -> Any:
        if value == 4070:
            return value
        raise ValueError("Invalid port number")


def _make_pod_ports(config: ConfigData) -> List[Dict[str, Any]]:
    """Generate pod ports details.
    Args:
        Config[str, Any]: Configuration details
    Returns:
        List[Dict[str, Any]]: pod port details.
    """
    return [{"name": "pcscf", "containerPort": config["pcscfport"], "protocol": "TCP"}]


def _make_pod_envconfig(model_name: str) -> Dict[str, Any]:
    """Generate pod environment configuration.
    Args:
        model_name (str): model name.
    Returns:
        Dict[str, Any]: pod environment configuration.
    """
    envconfig = {
        # General configuration
        "MODEL": model_name,
        "MYSQL_HOST": "mysql-endpoints",
        "MYSQL_USER": "root",
        "MYSQL_ROOT_PASSWORD": "root",
    }

    return envconfig


def _make_pod_command() -> List[str]:
    return ["./init_pcscf.sh", "&"]


def _make_pod_services():
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


def make_pod_spec(
    image_info: Dict[str, str],
    model_name: str,
    config: Dict[str, Any],
    app_name: str,
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
    ConfigData(**config)

    ports = _make_pod_ports(config)
    env_config = _make_pod_envconfig(model_name)
    command = _make_pod_command()
    services = _make_pod_services()

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
        "serviceAccount": {"automountServiceAccountToken": True, "roles": services},
    }
