"""Issue #12 - messaging privacy."""

import io
import os
import unittest

from tests._base import Base
import config


class TestMessagingPrivacy(Base):
    def test_patient_cannot_see_others_thread(self):
        from models import message as mm
        mm.send("20142024", "10000000", "private note")
        mm.send("10000000", "20232023", "different patient")
        thread = mm.thread("20232023", "10000000")
        self.assertEqual(len(thread), 1)
        self.assertNotIn("private note", [m["content"] for m in thread])


if __name__ == "__main__":
    unittest.main(verbosity=2)
