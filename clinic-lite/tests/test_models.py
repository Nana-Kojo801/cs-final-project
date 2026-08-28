"""Issue #9 - JSON data model: validation, storage, user model."""

import io
import os
import unittest

from tests._base import Base
import config


class TestValidator(Base):
    def test_ids(self):
        from utils.validator import validate_id
        self.assertTrue(validate_id("10000000", "clinician")[0])
        self.assertFalse(validate_id("10000001", "clinician")[0])
        self.assertTrue(validate_id("20142024", "patient")[0])
        self.assertFalse(validate_id("20142099", "patient")[0])   # year out of range
        self.assertFalse(validate_id("1234567", "patient")[0])    # 7 digits

    def test_passwords(self):
        from utils.validator import validate_password
        self.assertFalse(validate_password("short1!")[0])
        self.assertFalse(validate_password("nouppercase1!")[0])
        self.assertFalse(validate_password("NOLOWERCASE1!")[0])
        self.assertFalse(validate_password("NoDigits!!")[0])
        self.assertFalse(validate_password("NoSpecial11")[0])
        self.assertTrue(validate_password("Clinic@2026")[0])


class TestStorageTruncate(Base):
    def test_atomic_write_no_trailing_bytes(self):
        from utils.storage import read_json, write_json
        write_json("users", {"a": "x" * 500})
        write_json("users", {"b": 1})          # much shorter payload
        self.assertEqual(read_json("users"), {"b": 1})   # no "Extra data" corruption

    def test_corrupt_file_fails_safe(self):
        from utils.storage import read_json
        with open(os.path.join(config.DATA_DIR, "users.json"), "w") as f:
            f.write("{ this is not json")
        self.assertEqual(read_json("users", {}), {})


class TestAuthAndUsers(Base):
    def test_register_and_authenticate(self):
        from models import user as um
        u, err = um.register("20142024", "Pat One", "p1@x.com", "Clinic@2026", "patient")
        self.assertIsNone(err)
        self.assertNotIn("Clinic@2026", u.password_hash)
        self.assertIsNotNone(um.authenticate("20142024", "Clinic@2026"))
        self.assertIsNone(um.authenticate("20142024", "wrong"))

    def test_duplicate_id_rejected(self):
        from models import user as um
        um.register("20142024", "A", "a@x.com", "Clinic@2026", "patient")
        _, err = um.register("20142024", "B", "b@x.com", "Clinic@2026", "patient")
        self.assertIsNotNone(err)


if __name__ == "__main__":
    unittest.main(verbosity=2)
