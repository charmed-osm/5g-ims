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
""" Defining scscf charm events """

import logging
from typing import NoReturn
from ops.charm import CharmBase, CharmEvents
from ops.main import main
from ops.framework import StoredState, EventSource, EventBase
from ops.model import ActiveStatus, BlockedStatus, MaintenanceStatus
from oci_image import OCIImageResource, OCIImageResourceError
from pod_spec import make_pod_spec

logger = logging.getLogger(__name__)


class ConfigurePodEvent(EventBase):
    """Configure Pod event"""


class PublishScscfEvent(EventBase):
    """Publish Scscf event"""


class ScscfEvents(CharmEvents):
    """SCSCF Events"""

    configure_pod = EventSource(ConfigurePodEvent)
    publish_scscf_info = EventSource(PublishScscfEvent)


class ScscfCharm(CharmBase):
    """ scscf charm events class definition """

    state = StoredState()
    on = ScscfEvents()

    def __init__(self, *args):
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
        self.framework.observe(self.on.publish_scscf_info, self.publish_scscf_info)

        # Registering required relation changed events
        self.framework.observe(
            self.on.mysql_relation_changed, self._on_mysql_relation_changed
        )

        # Registering required relation changed events
        # self.framework.observe(
        #     self.on.scscfip_relation_joined, self._publish_scscf_info
        # )

        # -- initialize states --
        self.state.set_default(installed=False)
        self.state.set_default(configured=False)
        self.state.set_default(started=False)
        self.state.set_default(mysql=None)

    def publish_scscf_info(self, event: EventBase) -> NoReturn:
        """Publishes SCSCF information"""
        logging.info(event)
        if not self.unit.is_leader():
            return

        try:
            rel_id2 = self.model.relations.__getitem__("scscfip")
            for i in rel_id2:
                relation = self.model.get_relation("scscfip", i.id)
                parameter = str(self.model.get_binding(relation).network.bind_address)
                logger.info(parameter)
                if parameter != "None":
                    relation.data[self.model.app]["parameter"] = parameter
                    self.model.unit.status = ActiveStatus(
                        "Parameter sent: {}".format(parameter)
                    )
        except Exception as err:
            logger.error("Error in scscf relation data: %s", str(err))
            self.unit.status = BlockedStatus("Ip could not be obtained")
            return

    def _on_mysql_relation_changed(self, event: EventBase) -> NoReturn:
        """Reads information about the MYSQL relation.

        Args:
           event (EventBase): MYSQL relation event.
        """
        if event.app not in event.relation.data:
            return

        mysql = event.relation.data[event.app].get("hostname")
        logging.info("SCSCF Requires from MYSQL")
        logging.info(mysql)
        if mysql and self.state.mysql != mysql:
            self.state.mysql = mysql
            self.on.publish_scscf_info.emit()
            self.on.configure_pod.emit()

    def _missing_relations(self) -> str:
        """Checks if there missing relations.

        Returns:
            str: string with missing relations
        """
        data_status = {"mysql": self.state.mysql}
        missing_relations = [k for k, v in data_status.items() if not v]
        return ", ".join(missing_relations)

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
        logging.info("Configure pod")
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
        except ValueError as exc:
            logger.exception("Config data validation error")
            self.unit.status = BlockedStatus(str(exc))
            return

        if self.state.pod_spec != pod_spec:
            self.model.pod.set_spec(pod_spec)
            self.state.pod_spec = pod_spec

        self.unit.status = ActiveStatus("ready")
        self.on.publish_scscf_info.emit()


if __name__ == "__main__":
    main(ScscfCharm)
