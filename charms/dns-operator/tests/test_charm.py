# Copyright 2020 TataElxsi
# See LICENSE file for licensing details.

import unittest
# from unittest.mock import Mock
from typing import NoReturn
from ops.model import BlockedStatus
from ops.testing import Harness
from charm import DnsCharm


class TestCharm(unittest.TestCase):
    def setUp(self) -> NoReturn:
        """Test setup"""
        self.harness = Harness(DnsCharm)
        self.harness.set_leader(is_leader=True)
        self.harness.begin()

    def test_on_start_without_relations(self) -> NoReturn:
        """Test installation without any relation."""
        self.harness.charm.on.start.emit()

        # Verifying status
        self.assertIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertTrue(
            self.harness.charm.unit.status.message.startswith("Waiting for ")
        )

    def test_on_start_with_relations(self) -> NoReturn:
        """Test installation with any relation."""
        self.harness.charm.on.start.emit()
        # Check if pcscf,icscf,scscf,hss is initialized
        self.assertIsNone(self.harness.charm.state.pcscf)
        self.assertIsNone(self.harness.charm.state.icscf)
        self.assertIsNone(self.harness.charm.state.scscf)
        self.assertIsNone(self.harness.charm.state.hss)

        # Initializing pcscf relation
        pcscf_relation_id = self.harness.add_relation("pcscfip", "pcscfip")
        self.harness.add_relation_unit(pcscf_relation_id, "pcscfip/0")
        self.harness.update_relation_data(
            pcscf_relation_id, "pcscfip/0", {"parameter": "pcscfip", "port": 4070}
        )

        # Initializing icscf relation
        icscf_relation_id = self.harness.add_relation("icscfip", "icscfip")
        self.harness.add_relation_unit(icscf_relation_id, "icscfip/0")
        self.harness.update_relation_data(
            icscf_relation_id, "icscfip/0", {"parameter": "icscfip", "port": 4060}
        )

        # Initializing scscf relation
        scscf_relation_id = self.harness.add_relation("scscfip", "scscfip")
        self.harness.add_relation_unit(scscf_relation_id, "scscfip/0")
        self.harness.update_relation_data(
            scscf_relation_id, "scscfip/0", {"parameter": "scscfip", "port": 6060}
        )

        # Initializing hss relation
        hss_relation_id = self.harness.add_relation("hssip", "hssip")
        self.harness.add_relation_unit(hss_relation_id, "hssip/0")
        self.harness.update_relation_data(
            hss_relation_id, "hssip/0", {"parameter": "hssip", "port": 8080}
        )

    def test_on_pcscf_app_relation_changed(self) -> NoReturn:
        """Test to see if pcscf app relation is updated."""
        self.harness.charm.on.start.emit()

        self.assertIsNone(self.harness.charm.state.pcscf)

        relation_id = self.harness.add_relation("pcscfip", "pcscfip")
        self.harness.add_relation_unit(relation_id, "pcscfip/0")
        self.harness.update_relation_data(
            relation_id, "pcscfip", {"host": "pcscfip"}
        )

        # Verifying status
        self.assertIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertTrue(
            self.harness.charm.unit.status.message.startswith("Waiting for ")
        )

    def test_on_icscf_app_relation_changed(self) -> NoReturn:
        """Test to see if icscf app relation is updated."""
        self.harness.charm.on.start.emit()

        self.assertIsNone(self.harness.charm.state.pcscf)

        relation_id = self.harness.add_relation("icscfip", "icscfip")
        self.harness.add_relation_unit(relation_id, "icscfip/0")
        self.harness.update_relation_data(
            relation_id, "icscfip", {"host": "icscfip"}
        )

        # Verifying status
        self.assertIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertTrue(
            self.harness.charm.unit.status.message.startswith("Waiting for ")
        )

    def test_on_scscf_app_relation_changed(self) -> NoReturn:
        """Test to see if scscf app relation is updated."""
        self.harness.charm.on.start.emit()

        self.assertIsNone(self.harness.charm.state.pcscf)

        relation_id = self.harness.add_relation("scscfip", "scscfip")
        self.harness.add_relation_unit(relation_id, "scscfip/0")
        self.harness.update_relation_data(
            relation_id, "scscfip", {"host": "scscfip"}
        )

        # Verifying status
        self.assertIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertTrue(
            self.harness.charm.unit.status.message.startswith("Waiting for ")
        )

    def test_on_hss_app_relation_changed(self) -> NoReturn:
        """Test to see if hss app relation is updated."""
        self.harness.charm.on.start.emit()

        self.assertIsNone(self.harness.charm.state.pcscf)

        relation_id = self.harness.add_relation("hssip", "hssip")
        self.harness.add_relation_unit(relation_id, "hssip/0")
        self.harness.update_relation_data(
            relation_id, "hssip", {"host": "hssip"}
        )

        # Verifying status
        self.assertIsInstance(self.harness.charm.unit.status, BlockedStatus)

        # Verifying status message
        self.assertGreater(len(self.harness.charm.unit.status.message), 0)
        self.assertTrue(
            self.harness.charm.unit.status.message.startswith("Waiting for ")
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
