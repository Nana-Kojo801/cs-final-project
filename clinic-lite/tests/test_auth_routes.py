"""Issue #10 - registration validation, session, login-required protection."""

import importlib
import unittest

from tests._base import Base


class TestAuthRoutes(Base):
    def setUp(self):
        super().setUp()
        import app as appmod
        importlib.reload(appmod)
        self.app = appmod.app
        self.client = self.app.test_client()
        from models import user as um
        um.register("10000000", "Doc", "doc@x.com", "Clinic@2026", "clinician")

    def _login(self, uid, pw="Clinic@2026"):
        return self.client.post("/login", data={"user_id": uid, "password": pw},
                                follow_redirects=True)

    def test_login_required_route_redirects_when_anonymous(self):
        # /theme/<x> is protected by @login_required and exists from issue #10
        r = self.client.get("/theme/dark", follow_redirects=False)
        self.assertEqual(r.status_code, 302)

    def test_good_login_then_logout(self):
        r = self._login("10000000")
        self.assertEqual(r.status_code, 200)
        with self.client.session_transaction() as s:
            self.assertEqual(s.get("user_id"), "10000000")
            self.assertEqual(s.get("role"), "clinician")
        self.client.get("/logout")
        with self.client.session_transaction() as s:
            self.assertIsNone(s.get("user_id"))

    def test_bad_login_rejected(self):
        r = self._login("10000000", "wrongpass")
        self.assertIn(b"Invalid ID or password", r.data)

    def test_weak_password_registration_rejected(self):
        r = self.client.post("/register", data={
            "role": "patient", "user_id": "20452022", "name": "X",
            "email": "x@x.com", "password": "weak"}, follow_redirects=True)
        self.assertIn(b"Password", r.data)

    def test_bad_clinician_id_registration_rejected(self):
        r = self.client.post("/register", data={
            "role": "clinician", "user_id": "12345678", "name": "X",
            "email": "x2@x.com", "password": "Clinic@2026"}, follow_redirects=True)
        self.assertIn(b"end in 0000", r.data)

    def test_bad_patient_year_registration_rejected(self):
        r = self.client.post("/register", data={
            "role": "patient", "user_id": "20142099", "name": "X",
            "email": "x3@x.com", "password": "Clinic@2026"}, follow_redirects=True)
        self.assertIn(b"2022-2028", r.data)


if __name__ == "__main__":
    unittest.main(verbosity=2)
