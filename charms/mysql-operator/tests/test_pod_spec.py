""" test script for pod spec.py """
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
        dictport = {"sql_port": 3306}
        # pylint:disable=W0212
        pod_ports = pod_spec._make_pod_ports(dictport)

        self.assertListEqual(expected_result, pod_ports)

    def test_make_pod_envconfig(self) -> NoReturn:
        """Testing make pod envconfig"""

        expected_result = {
            "MYSQL_ROOT_PASSWORD": "root",
        }
        # pylint:disable=W0212
        pod_envconfig = pod_spec._make_pod_envconfig()
        self.assertEqual(expected_result, pod_envconfig)

    def test_make_pod_spec(self) -> NoReturn:
        """Teting make pod spec"""
        image_info = {"upstream-source": "localhost:32000/mysql:5.7"}
        config = {
            "sql_port": 4567,
        }
        app_name = "mysql"
        with self.assertRaises(ValueError):
            pod_spec.make_pod_spec(image_info, config, app_name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
