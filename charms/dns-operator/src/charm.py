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
"""Defining dns charm events"""
import logging
from typing import Any, Dict, NoReturn
from ops.charm import CharmBase
from ops.main import main
from ops.framework import StoredState, EventBase
from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus
from pod_spec import make_pod_spec

logger = logging.getLogger(__name__)


class DnsCharm(CharmBase):
    """DNS charm events class definition"""

    state = StoredState()

    def __init__(self, *args) -> NoReturn:
        """DNS charm constructor."""
        super().__init__(*args)
        # Internal state initialization
        self.state.set_default(pod_spec=None)

        # Registering regular events
        self.framework.observe(self.on.config_changed, self.configure_pod)

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
        self.state.set_default(hss=None)
        self.state.set_default(icscf=None)
        self.state.set_default(pcscf=None)
        self.state.set_default(scscf=None)

    def _on_hssip_relation_changed(self, event: EventBase) -> NoReturn:
        """hss ip relation changed.

        Args:
            event (EventBase):hss ip relation changed.
        """

        if event.unit not in event.relation.data:
            return
        try:
            parameter = event.relation.data[event.unit].get("parameter")
            if parameter and self.state.hss != parameter:
                self.state.hss = parameter
                self.configure_pod()
        except KeyError as err:
            logger.error("Key error in hss relation data: %s", str(err))
            self.unit.status = BlockedStatus("hss ip not obtained")
            return

    def _on_icscfip_relation_changed(self, event: EventBase) -> NoReturn:
        """icscfip relation changed.

        Args:
            event (EventBase): icscfip relation changed.
        """
        if event.unit not in event.relation.data:
            return
        try:
            parameter = event.relation.data[event.unit].get("parameter")
            if parameter and self.state.icscf != parameter:
                self.state.icscf = parameter
                self.configure_pod()
        except KeyError as err:
            logger.error("Key error in icscf relation data: %s", str(err))
            self.unit.status = BlockedStatus("icscf ip not obtained")
            return

    def _on_pcscfip_relation_changed(self, event: EventBase) -> NoReturn:
        """pcscf ip relation changed.

        Args:
            event (EventBase):pcscs ip relation changed.
        """
        if event.unit not in event.relation.data:
            return
        try:
            parameter = event.relation.data[event.unit].get("parameter")
            if parameter and self.state.pcscf != parameter:
                self.state.pcscf = parameter
                self.configure_pod()
        except KeyError as err:
            logger.error("Key error in pcscf relation data: %s", str(err))
            self.unit.status = BlockedStatus("pcscf ip not obtained")
            return

    def _on_scscfip_relation_changed(self, event: EventBase) -> NoReturn:
        """scscf ip relation changed.

        Args:
            event (EventBase):pcscs ip relation changed.
        """
        if event.unit not in event.relation.data:
            return
        try:
            parameter = event.relation.data[event.unit].get("parameter")
            if parameter and self.state.scscf != parameter:
                self.state.scscf = parameter
                self.configure_pod()
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

    def configure_pod(self, _=None) -> NoReturn:
        """Assemble the pod spec and apply it, if possible."""
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
        image_info = self.config["image"]
        relation = self.combined_ip()
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
