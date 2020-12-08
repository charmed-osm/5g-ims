# Copyright 2020 TataElxsi
# See LICENSE file for licensing details.

import unittest
# from unittest.mock import Mock
from typing import NoReturn
from ops.model import BlockedStatus
from ops.testing import Harness
from charm import PcscfCharm


class TestCharm(unittest.TestCase):
    def setUp(self) -> NoReturn:
        """Test setup"""
        self.harness = Harness(PcscfCharm)
        self.harness.set_leader(is_leader=True)
        self.harness.begin()

    def test_config_changed(self):
        self.harness.charm.on.start.emit()
        expected_result = {
            "version": 3,
            "containers": [
                {
                    "name": "pcscf",
                    "imageDetails": self.harness.charm.image.fetch(),
                    "imagePullPolicy": "Always",
                    "ports": [{"name": "pcscf", "containerPort": 4070, "protocol": "TCP"}],
                    "envConfig": {
                        "MODEL": None,
                        "MYSQL_HOST": "mysql-endpoints",
                        "MYSQL_USER": "root",
                        "MYSQL_ROOT_PASSWORD": "root",
                    },
                    "command": ["./init_pcscf.sh", "&"],
                }
            ],
            "serviceAccount": {
                "automountServiceAccountToken": True,
                "roles": [{"rules": [{
                    "apiGroups": [""],
                    "resources": ["services"],
                    "verbs": ["get", "watch", "list"],
                }]}]
            },
        }
        pod_spec, serviceAccount = self.harness.get_pod_spec()
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
