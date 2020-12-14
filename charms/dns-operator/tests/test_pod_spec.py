""" test script for pod spec.py """
from typing import NoReturn
import unittest
import pod_spec


class TestPodSpec(unittest.TestCase):
    """Pod spec unit tests."""

    def test_make_pod_ports(self) -> NoReturn:
        """Testing make pod ports."""
        port = 53

        expected_result = [
            {
                "name": "dnstcp",
                "containerPort": port,
                "protocol": "TCP",
            },
            {
                "name": "dnsudp",
                "containerPort": port,
                "protocol": "UDP",
            },
        ]
        portdict = {
            "dns_port": 53,
        }
        # pylint:disable=W0212
        pod_ports = pod_spec._make_pod_ports(portdict)

        self.assertListEqual(expected_result, pod_ports)

    def test_make_pod_command(self) -> NoReturn:
        """Testing make pod command"""

        expected_result = ["./init_dns.sh", "&"]
        # pylint:disable=W0212
        pod_command = pod_spec._make_pod_command()
        self.assertEqual(expected_result, pod_command)

    def test_validate_relation_data(self) -> NoReturn:
        """Testing validation of relation data"""
        expected_result = True
        relation = {
            "pcscf": "127.0.0.1",
            "icscf": "127.0.0.1",
            "scscf": "127.0.0.1",
            "hss": "127.0.0.1",
        }
        # pylint:disable=W0212
        result = pod_spec._validate_relation_data(relation)
        self.assertEqual(expected_result, result)

    def test_make_pod_envconfig(self) -> NoReturn:
        """Testing make pod envconfig"""

        expected_result = {
            "PCSCF": "127.0.0.1",
            "ICSCF": "127.0.0.1",
            "SCSCF": "127.0.0.1",
            "HSS": "127.0.0.1",
        }
        ipadd = {
            "pcscf": "127.0.0.1",
            "icscf": "127.0.0.1",
            "scscf": "127.0.0.1",
            "hss": "127.0.0.1",
        }
        # pylint:disable=W0212
        pod_envconfig = pod_spec._make_pod_envconfig(ipadd)
        self.assertEqual(expected_result, pod_envconfig)

    def test_make_pod_spec(self) -> NoReturn:
        """Teting make pod spec"""
        image_info = {"upstream-source": "localhost:32000/ims_dns:1.0"}
        config = {
            "dns_port": 9999,
        }
        app_name = "dns"
        relation = {
            "pcscf": "127.0.0.1",
            "icscf": "127.0.0.1",
            "scscf": "127.0.0.1",
            "hss": "127.0.0.1",
        }
        with self.assertRaises(ValueError):
            pod_spec.make_pod_spec(image_info, config, app_name, relation)


if __name__ == "__main__":
    unittest.main(verbosity=2)
