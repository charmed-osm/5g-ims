#!/usr/bin/env python3
# Copyright 2020 Tata Elxsi
#
# Licensed under the Apache License, Version 2.0 (the License); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an AS IS BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# For those usages not covered by the Apache License, Version 2.0 please
# contact: canonical@tataelxsi.onmicrosoft.com
#
# To get in touch with the maintainers, please contact:
# canonical@tataelxsi.onmicrosoft.com
##
"""test script for pod spec.py"""
from typing import NoReturn
import unittest
import pod_spec


class TestPodSpec(unittest.TestCase):
    """Pod spec unit tests."""

    def test_make_pod_ports(self) -> NoReturn:
        """Testing make pod ports."""
        port = 6060
        diaport = 3870

        expected_result = [
            {
                "name": "diascscf",
                "containerPort": diaport,
                "protocol": "TCP",
            },
            {
                "name": "scscf",
                "containerPort": port,
                "protocol": "TCP",
            },
        ]
        portdict = {"diameter_port": 3870}
        pod_ports = pod_spec._make_pod_ports(portdict)

        self.assertListEqual(expected_result, pod_ports)

    def test_make_pod_command(self) -> NoReturn:
        """Testing make pod command."""

        expected_result = ["./init_scscf.sh", "&"]
        pod_command = pod_spec._make_pod_command()
        self.assertEqual(expected_result, pod_command)

    def test_make_pod_envconfig(self) -> NoReturn:
        """Testing make pod envconfig."""

        expected_result = {
            "MYSQL_HOST": "mysql-endpoints",
            "MYSQL_USER": "root",
            "MYSQL_ROOT_PASSWORD": "root",
        }
        relation_state = {
            "db": "mysql",
            "user": "root",
            "pwd": "root",
        }
        pod_envconfig = pod_spec._make_pod_envconfig(relation_state)
        self.assertEqual(expected_result, pod_envconfig)

    def test_validate_config(self) -> NoReturn:
        """Testing config data exception scenario."""
        config = {"diameter_port": 1234}
        with self.assertRaises(ValueError):
            pod_spec._validate_config(config)

    def test_validate_relation(self) -> NoReturn:
        """Testing relation data scenario."""
        relation_state = {"user": "xyz"}
        with self.assertRaises(ValueError):
            pod_spec._validate_relation_state(relation_state)

    def test_make_pod_spec(self) -> NoReturn:
        """Teting make pod spec."""
        image_info = {"upstream-source": "localhost:32000/ims_scscf:1.0"}
        config = {"diameter_port": 3877}
        app_name = "scscf"
        relation_state = {
            "db": "mysql",
            "user": "root",
            "pwd": "root",
        }
        with self.assertRaises(ValueError):
            pod_spec.make_pod_spec(image_info, config, app_name, relation_state)


if __name__ == "__main__":
    unittest.main(verbosity=2)
