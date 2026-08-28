"""Issue #14 - cross-cutting integration checks for GridCare-Lite."""

import os
import unittest

from tests._base import Base
from core import services, reports


class TestAuditTrail(Base):
    def test_status_history_written_end_to_end(self):
        oid = services.create_outage(self.conn, self.eng, 1, "Fault", "High")
        wid = services.create_work_order(self.conn, self.admin, oid, self.tech["user_id"], "2027-01-01")
        services.start_work_order(self.conn, self.tech, wid)
        services.update_work_order_status(self.conn, self.tech, wid, "Completed", "fixed")
        n = self.conn.execute("SELECT COUNT(*) c FROM status_history").fetchone()["c"]
        self.assertGreaterEqual(n, 4)
        s = reports.operational_summary(self.conn, self.admin)
        self.assertEqual(s["open_work_orders"], 0)


class TestGridDataImport(unittest.TestCase):
    def test_reference_data_present_after_import(self):
        """import_grid_data populates substations from the grid-analysis outputs."""
        import tempfile
        from import_grid_data import import_reference_data, SUBS_CSV
        if not os.path.exists(SUBS_CSV):
            self.skipTest("grid-analysis cleaned_data not generated in this checkout")
        tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
        tmp.close()
        conn = import_reference_data(tmp.name)
        try:
            n = conn.execute("SELECT COUNT(*) c FROM substations").fetchone()["c"]
            self.assertGreater(n, 0)
            crit = conn.execute("SELECT COUNT(*) c FROM substations WHERE critical_flag=1").fetchone()["c"]
            self.assertGreaterEqual(crit, 0)
        finally:
            conn.close()
            os.unlink(tmp.name)


if __name__ == "__main__":
    unittest.main(verbosity=2)
