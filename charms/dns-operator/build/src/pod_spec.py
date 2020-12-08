#!/usr/bin/env python3
# Copyright 2020 TataElxsi
# See LICENSE file for licensing details.

import logging
from pydantic import BaseModel, IPvAnyAddress, validator, PositiveInt
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class ConfigData(BaseModel):
    """Configuration data model."""

    port: PositiveInt = 53

    @validator("port")
    def validate_port(cls, value: int) -> Any:
        if value == 53:
            return value
        raise ValueError("Invalid port number")


class RelationData(BaseModel):
    """Relation data model."""

    pcscf: IPvAnyAddress
    icscf: IPvAnyAddress
    scscf: IPvAnyAddress
    hss: IPvAnyAddress


def _make_pod_ports(config: ConfigData) -> List[Dict[str, Any]]:
    """Generate pod ports details.
    Args:
        config Dict[str,Any]: Config details.
    Returns:
        List[Dict[str, Any]]: pod port details.
    """
    return [
        {"name": "dnstcp", "containerPort": config["port"], "protocol": "TCP"},
        {"name": "dnsudp", "containerPort": config["port"], "protocol": "UDP"},
    ]


def _make_pod_envconfig(
    relation: RelationData,
) -> Dict[str, Any]:
    """Generate pod environment configuration.
    Args:
        config (Dict[str, Any]): configuration information.
        relation (Dict[str, Any]): relation state information.
    Returns:
        Dict[str, Any]: pod environment configuration.
    """
    envconfig = {
        # General configuration
        "PCSCF": relation["pcscf"],
        "ICSCF": relation["icscf"],
        "SCSCF": relation["scscf"],
        "HSS": relation["hss"],
    }

    return envconfig


def _make_pod_command() -> List[str]:
    return ["./init_dns.sh", "&"]


def make_pod_spec(
    image_info: Dict[str, str],
    config: Dict[str, Any],
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

    ConfigData(**config)
    RelationData(**(relation))

    logger.info("*******Check in pod_spec*********")
    ports = _make_pod_ports(config)
    env_config = _make_pod_envconfig(relation)
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
