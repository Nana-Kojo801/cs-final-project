"""Shared test fixture: points config paths at a fresh temp dir per test."""

import os
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import config  # noqa: E402


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        config.DATA_DIR = os.path.join(self.tmp, "data")
        config.SUBMISSIONS_DIR = os.path.join(self.tmp, "submissions")
        os.makedirs(config.DATA_DIR)
        os.makedirs(config.SUBMISSIONS_DIR)
        import importlib
        import utils.storage as storage
        storage.DATA_DIR = config.DATA_DIR
        storage.ensure_data_files()
        # rebind path globals in whichever optional modules are present in this checkout
        for mod_name, attr, value in (
            ("utils.file_handler", "SUBMISSIONS_DIR", config.SUBMISSIONS_DIR),
            ("utils.email_handler", "LOG_PATH",
             os.path.join(config.DATA_DIR, "notifications.log")),
        ):
            try:
                setattr(importlib.import_module(mod_name), attr, value)
            except ModuleNotFoundError:
                pass

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmp, ignore_errors=True)
