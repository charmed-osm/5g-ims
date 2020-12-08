from pydantic import ValidationError
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
            "port": 53,
        }
        pod_ports = pod_spec._make_pod_ports(portdict)

        self.assertListEqual(expected_result, pod_ports)

    def test_make_pod_command(self) -> NoReturn:
        """Testing make pod command"""

        expected_result = ["./init_dns.sh", "&"]

        pod_command = pod_spec._make_pod_command()
        self.assertEqual(expected_result, pod_command)

    def test_make_pod_envconfig(self) -> NoReturn:
        """Testing make pod envconfig"""

        expected_result = {
            "PCSCF": "pcscf",
            "ICSCF": "icscf",
            "SCSCF": "scscf",
            "HSS": "hss",
        }
        ipadd = {
            "pcscf": "pcscf",
            "icscf": "icscf",
            "scscf": "scscf",
            "hss": "hss",
        }
        pod_envconfig = pod_spec._make_pod_envconfig(ipadd)
        self.assertEqual(expected_result, pod_envconfig)

    def test_make_pod_spec(self) -> NoReturn:
        """Teting make pod spec"""
        image_info = {"upstream-source": "10.45.5.100:4200/canonical/ims_dns:v4.0"}
        config = {
            "port": 9999,

        }
        app_name = "dns"
        relation = {
            "pcscf": "pcscf",
            "icscf": "icscf",
            "scscf": "scscf",
            "hss": "hss",
        }
        with self.assertRaises(ValidationError):
            pod_spec.make_pod_spec(image_info, config, app_name, relation)


if __name__ == "__main__":
    unittest.main(verbosity=2)
