# Copyright 2020 TataElxsi
# See LICENSE file for licensing details.

import unittest
# from unittest.mock import Mock
from typing import NoReturn
from ops.model import BlockedStatus
from ops.testing import Harness
from charm import MysqlCharm


class TestCharm(unittest.TestCase):
    def setUp(self) -> NoReturn:
        """Test setup"""
        self.harness = Harness(MysqlCharm)
        self.harness.set_leader(is_leader=True)
        self.harness.begin()

    def test_config_changed(self):
        self.harness.charm.on.start.emit()
        expected_result = {
            "version": 3,
            "containers": [
                {
                    "name": "mysql",
                    "imageDetails": self.harness.charm.image.fetch(),
                    "imagePullPolicy": "Always",
                    "ports": [{"name": "sql", "containerPort": 3306, "protocol": "TCP"}],
                    "envConfig": {
                        "MYSQL_ROOT_PASSWORD": "root",
                    }
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


if __name__ == "__main__":
    unittest.main(verbosity=2)
