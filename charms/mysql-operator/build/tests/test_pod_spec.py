from pydantic import ValidationError
from typing import NoReturn
import unittest
import pod_spec


class TestPodSpec(unittest.TestCase):
    """Pod spec unit tests."""

    def test_make_pod_ports(self) -> NoReturn:
        """Testing make pod ports."""
        port = 3306

        expected_result = [
            {
                "name": "sql",
                "containerPort": port,
                "protocol": "TCP",
            },
        ]
        portdict = {
            "sqlport": 3306,
        }
        pod_ports = pod_spec._make_pod_ports(portdict)

        self.assertListEqual(expected_result, pod_ports)

    def test_make_pod_envconfig(self) -> NoReturn:
        """Testing make pod envconfig"""

        expected_result = {
            "MYSQL_ROOT_PASSWORD": "root",
        }
        pod_envconfig = pod_spec._make_pod_envconfig()
        self.assertEqual(expected_result, pod_envconfig)

    def test_make_pod_spec(self) -> NoReturn:
        """Teting make pod spec"""
        image_info = {"upstream-source": "10.45.5.100:4200/canonical/mysql:5.7"}
        config = {
            "sqlport": 4567,

        }
        app_name = "mysql"
        with self.assertRaises(ValidationError):
            pod_spec.make_pod_spec(image_info, config, app_name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
