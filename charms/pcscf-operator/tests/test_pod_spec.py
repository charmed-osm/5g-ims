""" test script for pod spec.py """
from typing import NoReturn
import unittest
import pod_spec


class TestPodSpec(unittest.TestCase):
    """Pod spec unit tests."""

    def test_make_pod_ports(self) -> NoReturn:
        """Testing make pod ports."""
        port = 4070

        expected_result = [
            {
                "name": "pcscf",
                "containerPort": port,
                "protocol": "TCP",
            }
        ]
        dictport = {"pcscf_port": 4070}
        # pylint:disable=W0212
        pod_ports = pod_spec._make_pod_ports(dictport)

        self.assertListEqual(expected_result, pod_ports)

    def test_make_pod_command(self) -> NoReturn:
        """Testing make pod command"""

        expected_result = ["./init_pcscf.sh", "&"]
        # pylint:disable=W0212
        pod_command = pod_spec._make_pod_command()
        self.assertEqual(expected_result, pod_command)

    def test_make_pod_envconfig(self) -> NoReturn:
        """Testing make pod envconfig"""

        expected_result = {
            "MODEL": "pcscf",
            "MYSQL_HOST": "mysql-endpoints",
            "MYSQL_USER": "root",
            "MYSQL_ROOT_PASSWORD": "root",
        }
        model = "pcscf"
        # pylint:disable=W0212
        pod_envconfig = pod_spec._make_pod_envconfig(model)
        self.assertEqual(expected_result, pod_envconfig)

    def test_make_pod_services(self) -> NoReturn:
        """Teting make pod envconfig configuration."""
        expected_result = [
            {
                "rules": [
                    {
                        "apiGroups": [""],
                        "resources": ["services"],
                        "verbs": ["get", "watch", "list"],
                    }
                ]
            }
        ]
        # pylint:disable=W0212
        pod_services = pod_spec._make_pod_services()
        self.assertEqual(expected_result, pod_services)

    def test_make_pod_spec(self) -> NoReturn:
        """Teting make pod spec"""
        image_info = {"upstream-source": "localhost:32000/ims_pcscf:1.0"}
        config = {
            "pcscf_port": 9999,
        }
        model_name = "pcscf"
        app_name = "pcscf"
        with self.assertRaises(ValueError):
            pod_spec.make_pod_spec(image_info, model_name, config, app_name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
