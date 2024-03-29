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
"""Defining hss charm events"""
import logging
from typing import Any, Dict, NoReturn
from ops.charm import CharmBase
from ops.main import main
from ops.framework import StoredState, EventBase
from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus
from pod_spec import make_pod_spec

logger = logging.getLogger(__name__)


class HssCharm(CharmBase):
    """hss charm."""

    state = StoredState()

    def __init__(self, *args) -> NoReturn:
        "HSS charm constructor." ""
        super().__init__(*args)
        # Internal state initialization
        self.state.set_default(pod_spec=None)

        # Registering regular events
        self.framework.observe(self.on.config_changed, self.configure_pod)

        # Registering required relation changed events
        self.framework.observe(
            self.on.mysql_relation_changed, self._on_mysql_relation_changed
        )
        self.framework.observe(
            self.on.dns_source_relation_joined, self.publish_hss_info
        )

        # -- initialize states --
        self.state.set_default(mysql=None)
        self.state.set_default(user=None)
        self.state.set_default(pwd=None)

    def publish_hss_info(self, event: EventBase) -> NoReturn:
        """Publishes Hss information."""
        if self.unit.is_leader():
            try:
                private_address = self.model.get_binding(
                    event.relation
                ).network.bind_address
                if private_address:
                    event.relation.data[self.app]["private-address"] = str(
                        private_address
                    )
                    event.relation.data[self.app]["hostname"] = self.app.name
                else:
                    event.defer()
            except TypeError as err:
                logger.error("Error in hss relation data: %s", str(err))
                event.defer()
                self.unit.status = BlockedStatus("Ip not yet fetched")
                return

    def _on_mysql_relation_changed(self, event: EventBase) -> NoReturn:
        """Reads information about the MYSQL relation.

        Args:
           event (EventBase): mysql relation event.
        """
        if event.app not in event.relation.data:
            return

        mysql = event.relation.data[event.app].get("hostname")
        user = event.relation.data[event.app].get("mysql_user")
        pwd = event.relation.data[event.app].get("mysql_pwd")
        if mysql and self.state.mysql != mysql:
            self.state.mysql = mysql
            self.state.user = user
            self.state.pwd = pwd
            self.configure_pod()

    def _missing_relations(self) -> str:
        """Checks if there missing relations.

        Returns:
            str: string with missing relations.
        """
        data_status = {"mysql": self.state.mysql}
        missing_relations = [k for k, v in data_status.items() if not v]
        return ", ".join(missing_relations)

    @property
    def relation_state(self) -> Dict[str, Any]:
        """Collects relation state configuration for pod spec assembly.

        Returns:
            Dict[str, Any]: relation state information.
        """
        relation_state = {
            "db": self.state.mysql,
            "user": self.state.user,
            "pwd": self.state.pwd,
        }
        return relation_state

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
        try:
            pod_spec = make_pod_spec(
                image_info,
                self.model.config,
                self.model.app.name,
                self.relation_state,
            )
        except ValueError as exc:
            logger.exception("Config data validation error")
            self.unit.status = BlockedStatus(str(exc))
            return

        if self.state.pod_spec != pod_spec:
            self.model.pod.set_spec(pod_spec)
            self.state.pod_spec = pod_spec

        self.unit.status = ActiveStatus("ready")


if __name__ == "__main__":
    main(HssCharm)
