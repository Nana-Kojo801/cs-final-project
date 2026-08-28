"""Issue #8 - operational reporting."""

import unittest

from tests._base import Base
from core import auth, services, reports


class TestReports(Base):
    def test_permission(self):
        with self.assertRaises(auth.AuthError):
            reports.operational_summary(self.conn, self.tech)
        with self.assertRaises(auth.AuthError):
            reports.operational_summary(self.conn, self.csr)

    def test_shape_and_counts(self):
        services.create_outage(self.conn, self.eng, 1, "Fault A", "High")
        services.create_outage(self.conn, self.eng, 2, "Fault B", "Low")
        s = reports.operational_summary(self.conn, self.admin)
        self.assertEqual(s["total_outages"], 2)
        self.assertEqual(s["outages_by_status"].get("Open"), 2)
        self.assertIn("Greater Accra", s["outages_by_region"])
        self.assertIn("High", s["outages_by_severity"])
        self.assertIsNone(s["avg_resolution_hours"])  # nothing resolved yet

    def test_avg_resolution_populates_after_resolution(self):
        oid = services.create_outage(self.conn, self.eng, 1, "Fault", "High")
        wid = services.create_work_order(self.conn, self.admin, oid, self.tech["user_id"], "2027-01-01")
        services.update_work_order_status(self.conn, self.tech, wid, "Completed", "fixed")
        s = reports.operational_summary(self.conn, self.admin)
        self.assertIsNotNone(s["avg_resolution_hours"])
        self.assertEqual(s["outages_by_status"].get("Resolved"), 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
