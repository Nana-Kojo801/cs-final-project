"""Shared test fixture: a fresh in-memory-ish DB with demo users and 2 substations."""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import auth  # noqa: E402
from core.db import init_db  # noqa: E402


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        self.tmp.close()
        self.conn = init_db(self.tmp.name)
        self.conn.execute(
            "INSERT INTO substations (substation_id, name, short_name, region, voltage_kv, capacity_mva)"
            " VALUES (1,'Alpha Substation','Alpha','Greater Accra',161,120.0),"
            "        (2,'Beta Substation','Beta','Ashanti',33,25.0)")
        self.conn.commit()
        self.admin = self._u("admin1", "admin")
        self.eng = self._u("eng1", "engineer")
        self.tech = self._u("tech1", "technician")
        self.tech2 = self._u("tech2", "technician")
        self.csr = self._u("csr1", "customer_service")

    def _u(self, name, role):
        auth.create_user(self.conn, name, "Passw0rd1", name.title(), role)
        return auth.authenticate(self.conn, name, "Passw0rd1")

    def tearDown(self):
        self.conn.close()
        os.unlink(self.tmp.name)
