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
"""mysql test script for charm.py"""

import unittest

# from unittest.mock import Mock
from typing import NoReturn
from ops.model import BlockedStatus
from ops.testing import Harness
from charm import MysqlCharm


class TestCharm(unittest.TestCase):
    """Test script for checking relations"""

    def setUp(self) -> NoReturn:
        """Test setup."""
        self.harness = Harness(MysqlCharm)
        self.harness.set_leader(is_leader=True)
        self.harness.begin()

    def test_config_changed(self):
        """Test script for pod spec."""
        self.harness.charm.on.config_changed.emit()
        expected_result = {
            "version": 3,
            "containers": [
                {
                    "name": "mysql",
                    "image": "mysql:5.7",
                    "imagePullPolicy": "Always",
                    "ports": [
                        {"name": "sql", "containerPort": 3306, "protocol": "TCP"}
                    ],
                    "envConfig": {
                        "MYSQL_ROOT_PASSWORD": "root",
                    },
                }
            ],
        }
        pod_spec, _ = self.harness.get_pod_spec()

        self.assertDictEqual(expected_result, pod_spec)
        # Verifying status
        self.assertNotIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertFalse(
            self.harness.charm.unit.status.message.startswith("Waiting for ")
        )

    def test_publish_pcscf_mysql_info(self) -> NoReturn:
        """Test to see if mysql relation is updated."""
        expected_result = {
            "hostname": "mysql",
            "mysql_user": "root",
            "mysql_pwd": "root",
        }
        relation_id = self.harness.add_relation("mysql", "pcscf")
        self.harness.add_relation_unit(relation_id, "pcscf/0")
        relation_data = self.harness.get_relation_data(relation_id, "mysql")
        self.assertDictEqual(expected_result, relation_data)

    def test_publish_icscf_mysql_info(self) -> NoReturn:
        """Test to see if mysql relation is updated."""
        expected_result = {
            "hostname": "mysql",
            "mysql_user": "root",
            "mysql_pwd": "root",
        }
        relation_id = self.harness.add_relation("mysql", "icscf")
        self.harness.add_relation_unit(relation_id, "icscf/0")
        relation_data = self.harness.get_relation_data(relation_id, "mysql")
        self.assertDictEqual(expected_result, relation_data)

    def test_publish_scscf_mysql_info(self) -> NoReturn:
        """Test to see if mysql relation is updated."""
        expected_result = {
            "hostname": "mysql",
            "mysql_user": "root",
            "mysql_pwd": "root",
        }
        relation_id = self.harness.add_relation("mysql", "scscf")
        self.harness.add_relation_unit(relation_id, "scscf/0")
        relation_data = self.harness.get_relation_data(relation_id, "mysql")
        self.assertDictEqual(expected_result, relation_data)

    def test_publish_hss_mysql_info(self) -> NoReturn:
        """Test to see if mysql relation is updated."""
        expected_result = {
            "hostname": "mysql",
            "mysql_user": "root",
            "mysql_pwd": "root",
        }
        relation_id = self.harness.add_relation("mysql", "hss")
        self.harness.add_relation_unit(relation_id, "hss/0")
        relation_data = self.harness.get_relation_data(relation_id, "mysql")
        self.assertDictEqual(expected_result, relation_data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
