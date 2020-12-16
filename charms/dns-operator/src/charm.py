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
""" Defining dns charm events """
import logging
from typing import Any, Dict, NoReturn
from ops.charm import CharmBase, CharmEvents
from ops.main import main
from ops.framework import StoredState, EventBase, EventSource
from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus
from oci_image import OCIImageResource, OCIImageResourceError
from pod_spec import make_pod_spec

logger = logging.getLogger(__name__)


class ConfigurePodEvent(EventBase):
    """Configure Pod event"""


class DnsEvents(CharmEvents):
    """DNS Events"""

    configure_pod = EventSource(ConfigurePodEvent)


class DnsCharm(CharmBase):
    """ DNS charm events class definition """

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
        self.framework.observe(self.on.leader_elected, self.configure_pod)
        self.framework.observe(self.on.update_status, self.configure_pod)

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
            rel_id2 = self.model.relations.__getitem__("hssip")
            for i in rel_id2:
                relation = self.model.get_relation("hssip", i.id)
                parameter = relation.data[event.app].get("parameter")
                if parameter != "None":
                    self.state.hss = relation.data[event.app].get("parameter")
                    logger.info("global hss ip : %s", self.state.hss)
                    logger.info("Parameter hss received: %s", parameter)
                    self.unit.status = ActiveStatus(
                        "Parameter received: {}".format(parameter)
                    )
                    self.on.configure_pod.emit()
        except KeyError as err:
            logger.error("Key error in hss relation data: %s", str(err))
            self.unit.status = BlockedStatus("hss ip not obtained")
            return

    def _on_icscfip_relation_changed(self, event: EventBase) -> NoReturn:
        try:
            rel_id2 = self.model.relations.__getitem__("icscfip")
            for i in rel_id2:
                relation = self.model.get_relation("icscfip", i.id)
                parameter = relation.data[event.app].get("parameter")
                if parameter != "None":
                    self.state.icscf = relation.data[event.app].get("parameter")
                    logger.info("global icscf ip : %s", self.state.icscf)
                    logger.info("Parameter icscf received: %s", parameter)
                    self.unit.status = ActiveStatus(
                        "Parameter received: {}".format(parameter)
                    )
                    self.on.configure_pod.emit()
        except KeyError as err:
            logger.error("Key error in icscf relation data: %s", str(err))
            self.unit.status = BlockedStatus("icscf ip not obtained")
            return

    def _on_pcscfip_relation_changed(self, event: EventBase) -> NoReturn:
        try:
            rel_id2 = self.model.relations.__getitem__("pcscfip")
            for i in rel_id2:
                relation = self.model.get_relation("pcscfip", i.id)
                parameter = relation.data[event.app].get("parameter")
                if parameter != "None":
                    self.state.pcscf = relation.data[event.app].get("parameter")
                    logger.info("global pcscf ip : %s", self.state.pcscf)
                    logger.info("Parameter pcscf received: %s", parameter)
                    self.unit.status = ActiveStatus(
                        "Parameter received: {}".format(parameter)
                    )
                    self.on.configure_pod.emit()
        except KeyError as err:
            logger.error("Key error in pcscf relation data: %s", str(err))
            self.unit.status = BlockedStatus("pcscf ip not obtained")
            return

    def _on_scscfip_relation_changed(self, event: EventBase) -> NoReturn:
        try:
            rel_id2 = self.model.relations.__getitem__("scscfip")
            for i in rel_id2:
                relation = self.model.get_relation("scscfip", i.id)
                parameter = relation.data[event.app].get("parameter")
                if parameter != "None":
                    self.state.scscf = relation.data[event.app].get("parameter")
                    logger.info("global scscf ip : %s", self.state.scscf)
                    logger.info("Parameter scscf received: %s", parameter)
                    self.unit.status = ActiveStatus(
                        "Parameter received: {}".format(parameter)
                    )
                    self.on.configure_pod.emit()
        except KeyError as err:
            logger.error("Key error in scscf relation data: %s", str(err))
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
        """ Combined ip relations """
        ip_addresses = {
            "hss": self.state.hss,
            "icscf": self.state.icscf,
            "pcscf": self.state.pcscf,
            "scscf": self.state.scscf,
        }
        return ip_addresses

    def configure_pod(self, event: EventBase) -> NoReturn:
        """Assemble the pod spec and apply it, if possible.
        Args:
            event (EventBase): Hook or Relation event that started the
                               function.
        """
        logging.info(event)
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

        relation = self.combined_ip()
        logger.info("pod spec call.............")
        try:
            pod_spec = make_pod_spec(
                image_info,
                self.model.config,
                self.model.app.name,
                relation,
            )
        except ValueError as exc:
            logger.exception("Config/Relation data validation error")
            self.unit.status = BlockedStatus(str(exc))
            return

        if self.state.pod_spec != pod_spec:
            self.model.pod.set_spec(pod_spec)
            self.state.pod_spec = pod_spec

        self.unit.status = ActiveStatus("ready")


if __name__ == "__main__":
    main(DnsCharm)
