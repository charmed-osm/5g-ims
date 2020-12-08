from pydantic import ValidationError
from typing import NoReturn
import unittest
import pod_spec


class TestPodSpec(unittest.TestCase):
    """Pod spec unit tests."""

    def test_make_pod_ports(self) -> NoReturn:
        """Testing make pod ports."""
        port = 4060
        diaport = 3869

        expected_result = [
            {
                "name": "diaicscf",
                "containerPort": diaport,
                "protocol": "TCP",
            },
            {
                "name": "icscf",
                "containerPort": port,
                "protocol": "TCP",
            },
        ]
        portdict = {
            "icscfport": 4060,
            "diaport": 3869
        }
        pod_ports = pod_spec._make_pod_ports(portdict)

        self.assertListEqual(expected_result, pod_ports)

    def test_make_pod_command(self) -> NoReturn:
        """Testing make pod command"""

        expected_result = ["./init_icscf.sh", "&"]

        pod_command = pod_spec._make_pod_command()
        self.assertEqual(expected_result, pod_command)

    def test_make_pod_envconfig(self) -> NoReturn:
        """Testing make pod envconfig"""

        expected_result = {
            "MYSQL_HOST": "mysql-endpoints",
            "MYSQL_USER": "root",
            "MYSQL_ROOT_PASSWORD": "root",
        }
        pod_envconfig = pod_spec._make_pod_envconfig()
        self.assertEqual(expected_result, pod_envconfig)

    def test_make_pod_spec(self) -> NoReturn:
        """Teting make pod spec"""
        image_info = {"upstream-source": "10.45.5.100:4200/canonical/ims_icscf:v4.0"}
        config = {
            "icscfport": 4060,
            "diaport": 3999

        }
        app_name = "icscf"
        with self.assertRaises(ValidationError):
            pod_spec.make_pod_spec(image_info, config, app_name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
