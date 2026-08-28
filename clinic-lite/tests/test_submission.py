"""Issue #11 - completeness check, file handling, submission/review workflow."""

import importlib
import io
import os
import unittest

from tests._base import Base
import config


class TestRouteProtection(Base):
    """Cross-role protection now that the patient/clinician routes exist."""

    def setUp(self):
        super().setUp()
        import app as appmod
        importlib.reload(appmod)
        self.client = appmod.app.test_client()
        from models import user as um, clinic as cm
        um.register("10000000", "Doc", "doc@x.com", "Clinic@2026", "clinician")
        um.register("20142024", "Pat", "pat@x.com", "Clinic@2026", "patient")
        cm.Clinic("c1", "Test Clinic", "10000000", ["20142024"]).save()

    def test_dashboard_requires_login(self):
        self.assertEqual(self.client.get("/patient", follow_redirects=False).status_code, 302)

    def test_patient_blocked_from_clinician_area(self):
        self.client.post("/login", data={"user_id": "20142024", "password": "Clinic@2026"})
        self.assertEqual(self.client.get("/clinician").status_code, 403)

    def test_clinician_reaches_own_dashboard(self):
        self.client.post("/login", data={"user_id": "10000000", "password": "Clinic@2026"})
        self.assertEqual(self.client.get("/clinician").status_code, 200)


class TestCompleteness(Base):
    def test_csv_missing_column(self):
        from utils.completeness import check_csv
        r = check_csv("date,systolic\n2026-01-01,120\n",
                      ["date", "systolic", "diastolic"], ["systolic", "diastolic"])
        self.assertFalse(r["ok"])
        self.assertTrue(any("diastolic" in i for i in r["issues"]))

    def test_csv_non_numeric(self):
        from utils.completeness import check_csv
        r = check_csv("date,systolic\n2026-01-01,high\n", ["date", "systolic"], ["systolic"])
        self.assertFalse(r["ok"])
        self.assertTrue(any("expected a number" in i for i in r["issues"]))

    def test_csv_ok(self):
        from utils.completeness import check_csv
        r = check_csv("date,systolic\n2026-01-01,120\n", ["date", "systolic"], ["systolic"])
        self.assertTrue(r["ok"])


class TestFileHandler(Base):
    def _fs(self, name, data=b"hello"):
        from werkzeug.datastructures import FileStorage
        return FileStorage(stream=io.BytesIO(data), filename=name)

    def test_reject_bad_extension(self):
        from utils.file_handler import save_stream, FileError
        with self.assertRaises(FileError):
            save_stream(self._fs("x.exe"), "c1", "20142024", "1")

    def test_reject_oversize(self):
        from utils.file_handler import save_stream, FileError
        big = b"x" * (config.MAX_UPLOAD_BYTES + 10)
        with self.assertRaises(FileError):
            save_stream(self._fs("x.txt", big), "c1", "20142024", "1")

    def test_path_traversal_blocked(self):
        from utils.file_handler import target_path, FileError
        with self.assertRaises(FileError):
            target_path("c1", "../../etc", "1", ".txt")

    def test_naming_and_location(self):
        from utils.file_handler import save_stream
        p = save_stream(self._fs("whatever.csv", b"a,b\n1,2\n"), "c1", "20142024", "7")
        self.assertTrue(p.endswith(os.path.join("c1", "20142024", "20142024_7.csv")))


class TestWorkflow(Base):
    def _setup_clinic(self):
        from models import user as um, clinic as cm, health_task as tm
        um.register("10000000", "Doc", "doc@x.com", "Clinic@2026", "clinician")
        um.register("20142024", "Pat", "pat@x.com", "Clinic@2026", "patient")
        cm.Clinic("c1", "Test Clinic", "10000000", ["20142024"]).save()
        task = tm.create("BP log", "upload", "2030-01-01", "c1", "10000000",
                         check_spec={"expected_columns": ["date", "systolic"],
                                     "numeric_columns": ["systolic"]})
        tm.assign(task.task_id, ["20142024"])
        return task

    def test_submit_then_review_notifies_patient(self):
        from utils import submission_workflow as workflow
        from models import task_submission as sm
        from utils.email_handler import inbox_for
        task = self._setup_clinic()
        sub, check = workflow.submit_task("20142024", task.task_id,
                                          content=b"date,systolic\n2026-01-01,120\n", ext=".csv")
        self.assertTrue(check["ok"])
        workflow.review_submission("10000000", "20142024", task.task_id,
                                   "Reviewed - Normal", "ok")
        self.assertEqual(sm.get("20142024", task.task_id).review_status, "Reviewed - Normal")
        subjects = [n["subject"] for n in inbox_for("20142024")]
        self.assertTrue(any("reviewed" in s.lower() for s in subjects))

    def test_cannot_submit_unassigned(self):
        from utils import submission_workflow as workflow
        from models import user as um, health_task as tm
        self._setup_clinic()
        um.register("20232023", "Other", "o@x.com", "Clinic@2026", "patient")
        task2 = tm.create("Other task", "x", "2030-01-01", "c1", "10000000")
        with self.assertRaises(workflow.WorkflowError):
            workflow.submit_task("20232023", task2.task_id, content=b"hi", ext=".txt")

    def test_review_requires_same_clinic(self):
        from utils import submission_workflow as workflow
        from models import user as um
        task = self._setup_clinic()
        workflow.submit_task("20142024", task.task_id,
                             content=b"date,systolic\n2026-01-01,120\n", ext=".csv")
        um.register("99990000", "Stranger", "s@x.com", "Clinic@2026", "clinician")
        with self.assertRaises(workflow.WorkflowError):
            workflow.review_submission("99990000", "20142024", task.task_id,
                                       "Reviewed - Normal", "x")

    def test_invalid_outcome_rejected(self):
        from utils import submission_workflow as workflow
        task = self._setup_clinic()
        workflow.submit_task("20142024", task.task_id,
                             content=b"date,systolic\n2026-01-01,120\n", ext=".csv")
        with self.assertRaises(ValueError):
            workflow.review_submission("10000000", "20142024", task.task_id, "A+", "x")


if __name__ == "__main__":
    unittest.main(verbosity=2)
