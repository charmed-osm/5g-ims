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
"""dns test script for charm.py"""
import unittest

# from unittest.mock import Mock
from typing import NoReturn
from ops.model import BlockedStatus
from ops.testing import Harness

from charm import DnsCharm


class TestCharm(unittest.TestCase):
    """Test script for checking relations"""

    def setUp(self) -> NoReturn:
        """Test setup."""
        self.harness = Harness(DnsCharm)
        self.harness.set_leader(is_leader=True)
        self.harness.begin()

    def test_on_start_without_relations(self) -> NoReturn:
        """Test installation without any relation."""
        self.harness.charm.on.start.emit()

        # Verifying status
        self.assertIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertTrue(
            self.harness.charm.unit.status.message.startswith("Waiting for ")
        )

    def test_on_start_with_relations(self) -> NoReturn:
        """Test installation with any relation."""
        self.harness.charm.on.start.emit()
        expected_result = {
            "version": 3,
            "containers": [
                {
                    "name": "dns",
                    "image": "localhost:32000/ims_dns:v7.0",
                    "imagePullPolicy": "Always",
                    "ports": [
                        {
                            "name": "dnstcp",
                            "containerPort": 53,
                            "protocol": "TCP",
                        },
                        {
                            "name": "dnsudp",
                            "containerPort": 53,
                            "protocol": "UDP",
                        },
                    ],
                    "envConfig": {
                        "PCSCF": "10.45.30.27",
                        "ICSCF": "10.45.30.28",
                        "SCSCF": "10.45.30.29",
                        "HSS": "10.45.30.30",
                    },
                    "command": ["./init_dns.sh", "&"],
                }
            ],
        }

        self.assertIsNone(self.harness.charm.state.pcscf)
        self.assertIsNone(self.harness.charm.state.icscf)
        self.assertIsNone(self.harness.charm.state.scscf)
        self.assertIsNone(self.harness.charm.state.hss)

        # Initializing pcscf relation
        pcscf_relation_id = self.harness.add_relation("pcscfip", "pcscfip")
        self.harness.add_relation_unit(pcscf_relation_id, "pcscfip/0")
        self.harness.update_relation_data(
            pcscf_relation_id, "pcscfip/0", {"parameter": "10.45.30.27"}
        )

        # Initializing icscf relation
        icscf_relation_id = self.harness.add_relation("icscfip", "icscfip")
        self.harness.add_relation_unit(icscf_relation_id, "icscfip/0")
        self.harness.update_relation_data(
            icscf_relation_id, "icscfip/0", {"parameter": "10.45.30.28"}
        )

        # Initializing scscf relation
        scscf_relation_id = self.harness.add_relation("scscfip", "scscfip")
        self.harness.add_relation_unit(scscf_relation_id, "scscfip/0")
        self.harness.update_relation_data(
            scscf_relation_id, "scscfip/0", {"parameter": "10.45.30.29"}
        )

        # Initializing hss relation
        hss_relation_id = self.harness.add_relation("hssip", "hssip")
        self.harness.add_relation_unit(hss_relation_id, "hssip/0")
        self.harness.update_relation_data(
            hss_relation_id, "hssip/0", {"parameter": "10.45.30.30"}
        )

        # Checking if nrf data is stored
        self.assertEqual(self.harness.charm.state.pcscf, "10.45.30.27")
        self.assertEqual(self.harness.charm.state.icscf, "10.45.30.28")
        self.assertEqual(self.harness.charm.state.scscf, "10.45.30.29")
        self.assertEqual(self.harness.charm.state.hss, "10.45.30.30")

        # Verifying status
        self.assertNotIsInstance(self.harness.charm.unit.status, BlockedStatus)

        pod_spec, _ = self.harness.get_pod_spec()
        self.assertDictEqual(expected_result, pod_spec)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertFalse(
            self.harness.charm.unit.status.message.startswith("Waiting for ")
        )

    def test_on_pcscf_app_relation_changed(self) -> NoReturn:
        """Test to see if pcscf app relation is updated."""
        self.harness.charm.on.start.emit()

        self.assertIsNone(self.harness.charm.state.pcscf)

        relation_id = self.harness.add_relation("pcscfip", "pcscfip")
        self.harness.add_relation_unit(relation_id, "pcscfip/0")
        self.harness.update_relation_data(
            relation_id, "pcscfip/0", {"parameter": "10.45.30.27"}
        )

        # Verifying status
        self.assertIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertTrue(
            self.harness.charm.unit.status.message.startswith("Waiting for ")
        )

    def test_on_icscf_app_relation_changed(self) -> NoReturn:
        """Test to see if icscf app relation is updated."""
        self.harness.charm.on.start.emit()

        self.assertIsNone(self.harness.charm.state.pcscf)

        relation_id = self.harness.add_relation("icscfip", "icscfip")
        self.harness.add_relation_unit(relation_id, "icscfip/0")
        self.harness.update_relation_data(
            relation_id, "icscfip/0", {"parameter": "10.45.30.28"}
        )

        # Verifying status
        self.assertIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertTrue(
            self.harness.charm.unit.status.message.startswith("Waiting for ")
        )

    def test_on_scscf_app_relation_changed(self) -> NoReturn:
        """Test to see if scscf app relation is updated."""
        self.harness.charm.on.start.emit()

        self.assertIsNone(self.harness.charm.state.pcscf)

        relation_id = self.harness.add_relation("scscfip", "scscfip")
        self.harness.add_relation_unit(relation_id, "scscfip/0")
        self.harness.update_relation_data(
            relation_id, "scscfip/0", {"parameter": "10.45.30.29"}
        )

        # Verifying status
        self.assertIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertTrue(
            self.harness.charm.unit.status.message.startswith("Waiting for ")
        )

    def test_on_hss_app_relation_changed(self) -> NoReturn:
        """Test to see if hss app relation is updated."""
        self.harness.charm.on.start.emit()

        self.assertIsNone(self.harness.charm.state.pcscf)

        relation_id = self.harness.add_relation("hssip", "hssip")
        self.harness.add_relation_unit(relation_id, "hssip/0")
        self.harness.update_relation_data(
            relation_id, "hssip/0", {"parameter": "10.45.30.30"}
        )

        # Verifying status
        self.assertIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertTrue(
            self.harness.charm.unit.status.message.startswith("Waiting for ")
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
