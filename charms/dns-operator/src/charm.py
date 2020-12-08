#!/usr/bin/env python3
# Copyright 2020 TataElxsi
# See LICENSE file for licensing details.

import logging
from ops.charm import CharmBase, CharmEvents
from ops.main import main
from ops.framework import StoredState, EventBase, EventSource
from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus
from oci_image import OCIImageResource, OCIImageResourceError
from pydantic import ValidationError
from typing import Any, Dict, NoReturn
from pod_spec import make_pod_spec

logger = logging.getLogger(__name__)


class ConfigurePodEvent(EventBase):
    """Configure Pod event"""

    pass


class DnsEvents(CharmEvents):
    """DNS Events"""

    configure_pod = EventSource(ConfigurePodEvent)


class DnsCharm(CharmBase):
    state = StoredState()
    on = DnsEvents()

    def __init__(self, *args) -> NoReturn:
        super().__init__(*args)
        # Internal state initialization
        self.state.set_default(pod_spec=None)

        self.image = OCIImageResource(self, "image")

        # Registering regular events
        self.framework.observe(self.on.start, self.configure_pod)
        self.framework.observe(self.on.config_changed, self.configure_pod)
        self.framework.observe(self.on.upgrade_charm, self.configure_pod)

        # Registering custom internal events
        self.framework.observe(self.on.configure_pod, self.configure_pod)

        # Registering required relation changed events
        self.framework.observe(
            self.on.hssip_relation_changed, self._on_hssip_relation_changed
        )
        self.framework.observe(
            self.on.icscfip_relation_changed, self._on_icscfip_relation_changed
        )
        self.framework.observe(
            self.on.pcscfip_relation_changed, self._on_pcscfip_relation_changed
        )
        self.framework.observe(
            self.on.scscfip_relation_changed, self._on_scscfip_relation_changed
        )

        # -- initialize states --
        self.state.set_default(installed=False)
        self.state.set_default(configured=False)
        self.state.set_default(started=False)
        self.state.set_default(hss=None)
        self.state.set_default(icscf=None)
        self.state.set_default(pcscf=None)
        self.state.set_default(scscf=None)

    def _on_hssip_relation_changed(self, event: EventBase) -> NoReturn:
        try:
            logger.info(
                "RELATION DATA: {}".format(dict(event.relation.data[event.app]))
            )
            parameter = event.relation.data[event.app].get("parameter")
            self.state.hss = event.relation.data[event.app].get("parameter")
            logger.info("global hss ip : {}".format(self.state.hss))
            if parameter is not None:
                logger.info("Parameter hss received: {}".format(parameter))
                self.unit.status = ActiveStatus(
                    "Parameter received: {}".format(parameter)
                )
                self.on.configure_pod.emit()
        except KeyError as err:
            logger.error("Key error in hss relation data: {}".format(str(err)))
            self.unit.status = BlockedStatus("hss ip not obtained")
            return

    def _on_icscfip_relation_changed(self, event: EventBase) -> NoReturn:
        try:
            logger.info(
                "RELATION DATA: {}".format(dict(event.relation.data[event.app]))
            )
            parameter = event.relation.data[event.app].get("parameter")
            self.state.icscf = event.relation.data[event.app].get("parameter")
            logger.info("global icscf ip : {}".format(self.state.icscf))
            if parameter is not None:
                logger.info("Parameter icscf received: {}".format(parameter))
                self.unit.status = ActiveStatus(
                    "Parameter received: {}".format(parameter)
                )
                self.on.configure_pod.emit()
        except KeyError as err:
            logger.error("Key error in icscf relation data: {}".format(str(err)))
            self.unit.status = BlockedStatus("icscf ip not obtained")
            return

    def _on_pcscfip_relation_changed(self, event: EventBase) -> NoReturn:
        try:
            logger.info(
                "RELATION DATA: {}".format(dict(event.relation.data[event.app]))
            )
            parameter = event.relation.data[event.app].get("parameter")
            self.state.pcscf = event.relation.data[event.app].get("parameter")
            logger.info("global pcscf ip : {}".format(self.state.pcscf))
            if parameter is not None:
                logger.info("Parameter pcscf received: {}".format(parameter))
                self.unit.status = ActiveStatus(
                    "Parameter received: {}".format(parameter)
                )
                self.on.configure_pod.emit()
        except KeyError as err:
            logger.error("Key error in pcscf relation data: {}".format(str(err)))
            self.unit.status = BlockedStatus("pcscf ip not obtained")
            return

    def _on_scscfip_relation_changed(self, event: EventBase) -> NoReturn:
        try:
            logger.info(
                "RELATION DATA: {}".format(dict(event.relation.data[event.app]))
            )
            parameter = event.relation.data[event.app].get("parameter")
            self.state.scscf = event.relation.data[event.app].get("parameter")
            logger.info("global scscf ip : {}".format(self.state.scscf))
            if parameter is not None:
                logger.info("Parameter scscf received: {}".format(parameter))
                self.unit.status = ActiveStatus(
                    "Parameter received: {}".format(parameter)
                )
                self.on.configure_pod.emit()
        except KeyError as err:
            logger.error("Key error in scscf relation data: {}".format(str(err)))
            self.unit.status = BlockedStatus("scscf ip not obtained")
            return

    def _missing_relations(self) -> str:
        """Checks if there missing relations.

        Returns:
            str: string with missing relations
        """
        data_status = {
            "hss": self.state.hss,
            "icscf": self.state.icscf,
            "pcscf": self.state.pcscf,
            "scscf": self.state.scscf,
        }
        missing_relations = [k for k, v in data_status.items() if not v]
        return ", ".join(missing_relations)

    def combined_ip(self) -> Dict[str, Any]:
        logger.info("Combined ip relations...................")
        ip_addresses = {
            "hss": self.state.hss,
            "icscf": self.state.icscf,
            "pcscf": self.state.pcscf,
            "scscf": self.state.scscf,
        }
        return ip_addresses

    def configure_pod(self, event: EventBase) -> NoReturn:
        missing = self._missing_relations()
        if missing:
            self.unit.status = BlockedStatus(
                "Waiting for {0} relation{1}".format(
                    missing, "s" if "," in missing else ""
                )
            )
            return

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
            relation = self.combined_ip()
            logger.info("pod spec call.............")
            pod_spec = make_pod_spec(
                image_info,
                self.model.config,
                self.model.app.name,
                relation,
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
    main(DnsCharm)
