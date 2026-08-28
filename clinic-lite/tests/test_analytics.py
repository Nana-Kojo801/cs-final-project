"""Issue #13 - engagement privacy and analytics isolation."""

import io
import os
import unittest

from tests._base import Base
import config


class TestEngagementPrivacy(Base):
    def test_summary_is_single_patient_scoped(self):
        from utils import engagement
        engagement.record_event("20142024", "task", True, "1")
        engagement.record_event("20232023", "task", True, "1")
        s = engagement.summary("20142024")
        self.assertEqual(s["on_time_tasks"], 1)   # only this patient's event
        # module exposes no "all patients" / ranking function
        self.assertFalse(hasattr(engagement, "leaderboard"))
        self.assertFalse(hasattr(engagement, "rank_patients"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
