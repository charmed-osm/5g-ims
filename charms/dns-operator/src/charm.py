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

    def __init__(self, *args) -> NoReturn:
        super().__init__(*args)
        # Internal state initialization
        self.state.set_default(pod_spec=None)

        self.image = OCIImageResource(self, "image")

        # Registering regular events
        self.framework.observe(self.on.config_changed, self.configure_pod)

        # Registering required relation changed events
        self.framework.observe(
            self.on.hosts_relation_changed,
            self._on_hosts_relation_changed,
        )

        # -- initialize states --
        self.state.set_default(installed=False)
        self.state.set_default(configured=False)
        self.state.set_default(started=False)

    def _on_hosts_relation_changed(self, event: EventBase) -> NoReturn:
        self.configure_pod()

    def get_hosts(self):
        # For reference. Check that it works.
        hosts = []
        relations = self.model.relations.__getitem__("hosts")
        for r in relations:
            relation = self.model.get_relation("hosts", r.id)
            for unit_data, values in relation.data.items():
                for unit in unit_data.relation.units:
                    if unit == unit_data:
                        host = values["private-address"]
                        hosts.append(host)
                        break
        return hosts

    def configure_pod(self, _=None) -> NoReturn:
        """Assemble the pod spec and apply it, if possible.
        Args:
            event (EventBase): Hook or Relation event that started the
                               function.
        """
        if not self.unit.is_leader():
            self.unit.status = ActiveStatus("ready")
            return

        dns_hosts = self.get_hosts()
        try:
            image_info = self.image.fetch()
        except OCIImageResourceError:
            self.unit.status = BlockedStatus("Error fetching image information")
            return

        try:
            pod_spec = make_pod_spec(
                image_info,
                self.model.config,
                self.model.app.name,
                dns_hosts,
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
