"""Issue #6 - authentication and role-based access control."""

import unittest

from tests._base import Base
from core import auth


class TestAuth(Base):
    def test_password_rules(self):
        self.assertFalse(auth.validate_password("short1")[0])
        self.assertFalse(auth.validate_password("allletters")[0])
        self.assertFalse(auth.validate_password("12345678")[0])
        self.assertTrue(auth.validate_password("Passw0rd1")[0])

    def test_hash_roundtrip(self):
        h = auth.hash_password("Secret123")
        self.assertTrue(auth.check_password("Secret123", h))
        self.assertFalse(auth.check_password("wrong", h))
        self.assertNotIn("Secret123", h)

    def test_bad_login(self):
        with self.assertRaises(auth.AuthError):
            auth.authenticate(self.conn, "eng1", "nope")
        with self.assertRaises(auth.AuthError):
            auth.authenticate(self.conn, "ghost", "whatever")

    def test_rbac_matrix(self):
        self.assertTrue(auth.has_permission("engineer", "create_outage"))
        self.assertFalse(auth.has_permission("engineer", "create_work_order"))
        self.assertFalse(auth.has_permission("technician", "create_outage"))
        self.assertTrue(auth.has_permission("customer_service", "log_complaint"))
        self.assertFalse(auth.has_permission("customer_service", "view_reports"))

    def test_require_raises_for_wrong_role(self):
        with self.assertRaises(auth.AuthError):
            auth.require(self.tech, "create_outage")
        auth.require(self.eng, "create_outage")  # no raise


if __name__ == "__main__":
    unittest.main(verbosity=2)
