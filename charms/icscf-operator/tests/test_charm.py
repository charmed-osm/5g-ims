# Copyright 2020 TataElxsi
# See LICENSE file for licensing details.
""" icscf test script for charm.py """

import unittest

# from unittest.mock import Mock
from typing import NoReturn
from ops.model import BlockedStatus
from ops.testing import Harness
from charm import IcscfCharm


class TestCharm(unittest.TestCase):
    """ Test script for checking relations """

    def setUp(self) -> NoReturn:
        """Test setup"""
        self.harness = Harness(IcscfCharm)
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
        """Test installation without any relation."""
        self.harness.charm.on.start.emit()
        expected_result = {
            "version": 3,
            "containers": [
                {
                    "name": "icscf",
                    "imageDetails": self.harness.charm.image.fetch(),
                    "imagePullPolicy": "Always",
                    "ports": [
                        {"name": "diaicscf", "containerPort": 3869, "protocol": "TCP"},
                        {"name": "icscf", "containerPort": 4060, "protocol": "TCP"},
                    ],
                    "envConfig": {
                        "MYSQL_HOST": "mysql-endpoints",
                        "MYSQL_USER": "root",
                        "MYSQL_ROOT_PASSWORD": "root",
                    },
                    "command": ["./init_icscf.sh", "&"],
                }
            ],
        }
        # Check if mysql is initialized
        self.assertIsNone(self.harness.charm.state.mysql)

        # Initializing mysql relation
        mysql_relation_id = self.harness.add_relation("mysql", "mysql")
        self.harness.add_relation_unit(mysql_relation_id, "mysql/0")
        self.harness.update_relation_data(
            mysql_relation_id, "mysql", {"hostname": "mysql"}
        )

        # Checking if nrf data is stored
        self.assertEqual(self.harness.charm.state.mysql, "mysql")

        # Verifying status
        self.assertNotIsInstance(self.harness.charm.unit.status, BlockedStatus)

        pod_spec, _ = self.harness.get_pod_spec()
        self.assertDictEqual(expected_result, pod_spec)

    def test_on_mysql_app_relation_changed(self) -> NoReturn:
        """Test to see if mysql app relation is updated."""
        self.harness.charm.on.start.emit()

        self.assertIsNone(self.harness.charm.state.mysql)

        relation_id = self.harness.add_relation("mysql", "mysql")
        self.harness.add_relation_unit(relation_id, "mysql/0")
        self.harness.update_relation_data(relation_id, "mysql", {"hostname": "mysql"})

        # Verifying status
        self.assertNotIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertFalse(
            self.harness.charm.unit.status.message.startswith("Waiting for ")
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
