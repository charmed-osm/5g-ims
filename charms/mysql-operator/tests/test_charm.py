# Copyright 2020 TataElxsi
# See LICENSE file for licensing details.
""" mysql test script for charm.py """

import unittest

# from unittest.mock import Mock
from typing import NoReturn
from ops.model import BlockedStatus
from ops.testing import Harness
from charm import MysqlCharm


class TestCharm(unittest.TestCase):
    """ Test script for checking relations """

    def setUp(self) -> NoReturn:
        """Test setup"""
        self.harness = Harness(MysqlCharm)
        self.harness.set_leader(is_leader=True)
        self.harness.begin()

    def test_config_changed(self):
        """ Test script for pod spec """
        self.harness.charm.on.start.emit()
        expected_result = {
            "version": 3,
            "containers": [
                {
                    "name": "mysql",
                    "imageDetails": self.harness.charm.image.fetch(),
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
        expected_result = {"hostname": "mysql"}
        self.harness.charm.on.start.emit()
        relation_id = self.harness.add_relation("mysql", "pcscf")
        self.harness.add_relation_unit(relation_id, "pcscf/0")
        relation_data = self.harness.get_relation_data(relation_id, "mysql")
        self.assertDictEqual(expected_result, relation_data)

    def test_publish_icscf_mysql_info(self) -> NoReturn:
        """Test to see if mysql relation is updated."""
        expected_result = {"hostname": "mysql"}
        self.harness.charm.on.start.emit()
        relation_id = self.harness.add_relation("mysql", "icscf")
        self.harness.add_relation_unit(relation_id, "icscf/0")
        relation_data = self.harness.get_relation_data(relation_id, "mysql")
        self.assertDictEqual(expected_result, relation_data)

    def test_publish_scscf_mysql_info(self) -> NoReturn:
        """Test to see if mysql relation is updated."""
        expected_result = {"hostname": "mysql"}
        self.harness.charm.on.start.emit()
        relation_id = self.harness.add_relation("mysql", "scscf")
        self.harness.add_relation_unit(relation_id, "scscf/0")
        relation_data = self.harness.get_relation_data(relation_id, "mysql")
        self.assertDictEqual(expected_result, relation_data)

    def test_publish_hss_mysql_info(self) -> NoReturn:
        """Test to see if mysql relation is updated."""
        expected_result = {"hostname": "mysql"}
        self.harness.charm.on.start.emit()
        relation_id = self.harness.add_relation("mysql", "hss")
        self.harness.add_relation_unit(relation_id, "hss/0")
        relation_data = self.harness.get_relation_data(relation_id, "mysql")
        self.assertDictEqual(expected_result, relation_data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
