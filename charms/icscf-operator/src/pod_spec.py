#!/usr/bin/env python3
# Copyright 2020 TataElxsi
# See LICENSE file for licensing details.

import logging
from pydantic import BaseModel, validator, PositiveInt
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class ConfigData(BaseModel):
    """Configuration data model."""

    diaport: PositiveInt = 3869
    icscfport: PositiveInt = 4060

    @validator("diaport")
    def validate_diaport(cls, value: int) -> Any:
        if value == 3869:
            return value
        raise ValueError("Invalid port number")

    @validator("icscfport")
    def validate_icscfport(cls, value: int) -> Any:
        if value == 4060:
            return value
        raise ValueError("Invalid port number")


def _make_pod_ports(config: ConfigData) -> List[Dict[str, Any]]:
    """Generate pod ports details.
    Args:
        config (Dict[str, Any]): configuration information.
    Returns:
        List[Dict[str, Any]]: pod port details.
    """
    return [
        {"name": "diaicscf", "containerPort": config["diaport"], "protocol": "TCP"},
        {"name": "icscf", "containerPort": config["icscfport"], "protocol": "TCP"},
    ]


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
    return ["./init_icscf.sh", "&"]


def make_pod_spec(
    image_info: Dict[str, str],
    config: Dict[str, Any],
    app_name: str = "icscf",
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

    ConfigData(**config)

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
