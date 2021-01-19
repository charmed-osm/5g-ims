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
"""pcscf test script for charm.py"""

import unittest

# from unittest.mock import Mock
from typing import NoReturn
from ops.model import BlockedStatus
from ops.testing import Harness
from charm import PcscfCharm


class TestCharm(unittest.TestCase):
    """Test script for checking relations."""

    def setUp(self) -> NoReturn:
        """Test setup."""
        self.harness = Harness(PcscfCharm)
        self.harness.set_leader(is_leader=True)
        self.harness.begin()

    def test_on_start_without_relations(self) -> NoReturn:
        """Test installation without any relation."""
        self.harness.charm.on.config_changed.emit()

        # Verifying status
        self.assertIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertTrue(
            self.harness.charm.unit.status.message.startswith("Waiting for ")
        )

    def test_on_start_with_relations(self) -> NoReturn:
        """Test installation with any relation."""
        expected_result = {
            "version": 3,
            "containers": [
                {
                    "name": "pcscf",
                    "image": "localhost:32000/ims_pcscf:v7.0",
                    "imagePullPolicy": "Always",
                    "ports": [
                        {"name": "pcscf", "containerPort": 4070, "protocol": "TCP"}
                    ],
                    "envConfig": {
                        "MODEL": None,
                        "MYSQL_HOST": "mysql-endpoints",
                        "MYSQL_USER": "root",
                        "MYSQL_ROOT_PASSWORD": "root",
                    },
                    "command": ["./init_pcscf.sh", "&"],
                    "kubernetes": {"startupProbe": {"tcpSocket": {"port": 4070}}},
                }
            ],
            "serviceAccount": {
                "automountServiceAccountToken": True,
                "roles": [
                    {
                        "rules": [
                            {
                                "apiGroups": [""],
                                "resources": ["services"],
                                "verbs": ["get", "watch", "list"],
                            }
                        ]
                    }
                ],
            },
        }
        # Check if mysql is initialized
        self.assertIsNone(self.harness.charm.state.mysql)

        # Initializing mysql relation
        mysql_relation_id = self.harness.add_relation("mysql", "mysql")
        self.harness.add_relation_unit(mysql_relation_id, "mysql/0")
        self.harness.update_relation_data(
            mysql_relation_id,
            "mysql",
            {"hostname": "mysql", "mysql_user": "root", "mysql_pwd": "root"},
        )

        # Checking if nrf data is stored
        self.assertEqual(self.harness.charm.state.mysql, "mysql")

        # Verifying status
        self.assertNotIsInstance(self.harness.charm.unit.status, BlockedStatus)

        pod_spec, _ = self.harness.get_pod_spec()
        self.assertDictEqual(expected_result, pod_spec)

    def test_on_mysql_app_relation_changed(self) -> NoReturn:
        """Test to see if mysql app relation is updated."""

        self.assertIsNone(self.harness.charm.state.mysql)

        relation_id = self.harness.add_relation("mysql", "mysql")
        self.harness.add_relation_unit(relation_id, "mysql/0")
        self.harness.update_relation_data(
            relation_id,
            "mysql",
            {"hostname": "mysql", "mysql_user": "root", "mysql_pwd": "root"},
        )

        # Verifying status
        self.assertNotIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertFalse(
            self.harness.charm.unit.status.message.startswith("Waiting for ")
        )

    def test_publish_pcscf_info(self) -> NoReturn:
        """Test to see if pcscf relation is updated."""
        expected_result = {
            "private-address": "127.1.1.1",
            "hostname": "pcscf"
        }
        relation_id = self.harness.add_relation("dns-source", "dns_source")
        relation_data = {"private-address": "127.1.1.1", "hostname": "pcscf"}
        self.harness.update_relation_data(relation_id, "dns_source", relation_data)
        relation_data = self.harness.get_relation_data(relation_id, "dns_source")
        self.assertDictEqual(expected_result, relation_data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
