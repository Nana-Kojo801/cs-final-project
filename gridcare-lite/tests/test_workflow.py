"""Issue #7 - outage-to-resolution workflow, work orders, complaints."""

import unittest

from tests._base import Base
from core import auth, services


class TestOutageWorkflow(Base):
    def test_engineer_can_log_csr_cannot(self):
        oid = services.create_outage(self.conn, self.eng, 1, "Feeder tripped", "High")
        self.assertIsInstance(oid, int)
        with self.assertRaises(auth.AuthError):
            services.create_outage(self.conn, self.csr, 1, "x", "Low")

    def test_bad_substation_and_severity(self):
        with self.assertRaises(services.WorkflowError):
            services.create_outage(self.conn, self.eng, 999, "nowhere", "High")
        with self.assertRaises(services.WorkflowError):
            services.create_outage(self.conn, self.eng, 1, "bad sev", "Catastrophic")

    def test_duplicate_open_outage_rejected(self):
        services.create_outage(self.conn, self.eng, 1, "Same text", "Medium")
        with self.assertRaises(services.WorkflowError):
            services.create_outage(self.conn, self.eng, 1, "Same text", "Medium")

    def test_invalid_status_transition(self):
        oid = services.create_outage(self.conn, self.eng, 1, "Feeder", "High")
        with self.assertRaises(services.WorkflowError):
            services.set_outage_status(self.conn, self.admin, oid, "Resolved")


class TestWorkOrders(Base):
    def _outage(self):
        return services.create_outage(self.conn, self.eng, 1, "Transformer fault", "High")

    def test_only_admin_creates_wo(self):
        oid = self._outage()
        with self.assertRaises(auth.AuthError):
            services.create_work_order(self.conn, self.eng, oid)
        self.assertIsInstance(services.create_work_order(self.conn, self.admin, oid), int)

    def test_no_duplicate_wo(self):
        oid = self._outage()
        services.create_work_order(self.conn, self.admin, oid)
        with self.assertRaises(services.WorkflowError):
            services.create_work_order(self.conn, self.admin, oid)

    def test_past_date_rejected(self):
        wid = services.create_work_order(self.conn, self.admin, self._outage())
        with self.assertRaises(services.WorkflowError):
            services.assign_technician(self.conn, self.admin, wid, self.tech["user_id"], "2000-01-01")

    def test_assign_non_technician_rejected(self):
        wid = services.create_work_order(self.conn, self.admin, self._outage())
        with self.assertRaises(services.WorkflowError):
            services.assign_technician(self.conn, self.admin, wid, self.eng["user_id"], "2027-01-01")

    def test_technician_cannot_touch_others_wo(self):
        wid = services.create_work_order(self.conn, self.admin, self._outage(),
                                         self.tech["user_id"], "2027-01-01")
        with self.assertRaises(auth.AuthError):
            services.update_work_order_status(self.conn, self.tech2, wid, "Completed", "done")

    def test_complete_requires_notes(self):
        wid = services.create_work_order(self.conn, self.admin, self._outage(),
                                         self.tech["user_id"], "2027-01-01")
        with self.assertRaises(services.WorkflowError):
            services.update_work_order_status(self.conn, self.tech, wid, "Completed")

    def test_full_outage_to_resolution(self):
        oid = self._outage()
        wid = services.create_work_order(self.conn, self.admin, oid, self.tech["user_id"], "2027-01-01")
        services.start_work_order(self.conn, self.tech, wid)
        services.update_work_order_status(self.conn, self.tech, wid, "Completed", "Replaced relay")
        resolved = services.list_outages(self.conn, status="Resolved")
        self.assertEqual([o["outage_id"] for o in resolved], [oid])
        self.assertIsNotNone(resolved[0]["resolved_at"])


class TestComplaints(Base):
    def test_complaint_link(self):
        oid = services.create_outage(self.conn, self.eng, 1, "Fault", "High")
        cid = services.log_complaint(self.conn, self.csr, "Kojo", "No power", outage_id=oid)
        rows = services.list_complaints(self.conn)
        self.assertEqual(rows[0]["complaint_id"], cid)
        self.assertEqual(rows[0]["status"], "Linked")

    def test_complaint_bad_outage(self):
        with self.assertRaises(services.WorkflowError):
            services.log_complaint(self.conn, self.csr, "Kojo", "No power", outage_id=123)

    def test_engineer_cannot_log_complaint(self):
        with self.assertRaises(auth.AuthError):
            services.log_complaint(self.conn, self.eng, "X", "desc")


if __name__ == "__main__":
    unittest.main(verbosity=2)
