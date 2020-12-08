#!/usr/bin/env python3
# Copyright 2020 TataElxsi
# See LICENSE file for licensing details.

import logging

from ops.charm import CharmBase, CharmEvents
from ops.main import main
from ops.framework import StoredState, EventSource, EventBase
from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus
from oci_image import OCIImageResource, OCIImageResourceError
from pydantic import ValidationError
from typing import NoReturn
from pod_spec import make_pod_spec

logger = logging.getLogger(__name__)


class ConfigurePodEvent(EventBase):
    """Configure Pod event"""

    pass


class IcscfEvents(CharmEvents):
    """ICSCF Events"""

    configure_pod = EventSource(ConfigurePodEvent)


class IcscfCharm(CharmBase):
    state = StoredState()
    on = IcscfEvents()

    def __init__(self, *args) -> NoReturn:
        super().__init__(*args)
        # Internal state initialization
        self.state.set_default(pod_spec=None)

        self.image = OCIImageResource(self, "image")

        # Registering regular events
        self.framework.observe(self.on.start, self.configure_pod)
        self.framework.observe(self.on.config_changed, self.configure_pod)
        self.framework.observe(self.on.upgrade_charm, self.configure_pod)
        self.framework.observe(self.on.leader_elected, self.configure_pod)
        self.framework.observe(self.on.update_status, self.configure_pod)

        # Registering custom internal events
        self.framework.observe(self.on.configure_pod, self.configure_pod)

        # Registering required relation changed events
        self.framework.observe(
            self.on.icscfip_relation_joined, self._publish_icscf_info
        )

        # -- initialize states --
        self.state.set_default(installed=False)
        self.state.set_default(configured=False)
        self.state.set_default(started=False)

    def _publish_icscf_info(self, event: EventBase) -> NoReturn:
        logger.info("ICSCF Provides")
        logger.info("***************************************")
        if self.unit.is_leader():
            logger.info("ICSCF IP")
            parameter = str(self.model.get_binding(event.relation).network.bind_address)
            logger.info(parameter)
            if parameter is not None:
                event.relation.data[self.model.app]["parameter"] = parameter
                self.model.unit.status = ActiveStatus(
                    "Parameter sent: {}".format(parameter)
                )

    def configure_pod(self, event: EventBase) -> NoReturn:
        if not self.unit.is_leader():
            self.unit.status = ActiveStatus("ready")
            return

        self.unit.status = MaintenanceStatus("Assembling pod spec")

        # Fetch image information
        try:
            self.unit.status = MaintenanceStatus("Fetching image information")
            image_info = self.image.fetch()
        except OCIImageResourceError:
            self.unit.status = BlockedStatus("Error fetching image information")
            return

        try:
            pod_spec = make_pod_spec(
                image_info,
                self.model.config,
                self.model.app.name,
            )
        except ValidationError as exc:
            logger.exception("Config/Relation data validation error")
            self.unit.status = BlockedStatus(str(exc))
            return

        if self.state.pod_spec != pod_spec:
            self.model.pod.set_spec(pod_spec)
            self.state.pod_spec = pod_spec

        self.unit.status = ActiveStatus("ready")


if __name__ == "__main__":
    main(IcscfCharm)
