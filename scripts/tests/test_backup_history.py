import importlib.util
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "backup_history", Path(__file__).resolve().parents[1] / "backup-history.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
backup_history = module.backup_history


class BackupTests(unittest.TestCase):
    def test_committed_wal_is_included_without_changing_source(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "history.db"
            destination = Path(folder) / "backup.db"
            with closing(sqlite3.connect(source)) as writer:
                writer.execute("PRAGMA journal_mode=WAL")
                writer.execute("CREATE TABLE scans (id INTEGER PRIMARY KEY)")
                writer.commit()
                writer.execute("INSERT INTO scans VALUES (1), (2)")
                writer.commit()
                self.assertTrue(Path(str(source) + "-wal").exists())
                result = backup_history(source, destination)
                self.assertEqual(result, {"integrity": "ok", "records": 2})
                self.assertEqual(
                    writer.execute("SELECT COUNT(*) FROM scans").fetchone()[0], 2
                )

    def test_existing_destination_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "history.db"
            destination = Path(folder) / "backup.db"
            with closing(sqlite3.connect(source)) as connection:
                connection.execute("CREATE TABLE scans (id INTEGER)")
            destination.write_bytes(b"preserve")
            with self.assertRaises(FileExistsError):
                backup_history(source, destination)
            self.assertEqual(destination.read_bytes(), b"preserve")

    def test_missing_source_does_not_create_files(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "missing.db"
            destination = Path(folder) / "backup.db"
            with self.assertRaises(FileNotFoundError):
                backup_history(source, destination)
            self.assertFalse(source.exists())
            self.assertFalse(destination.exists())

    def test_corrupt_source_is_rejected_before_destination_creation(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "broken.db"
            destination = Path(folder) / "backup.db"
            source.write_bytes(b"not a database")
            with self.assertRaises(sqlite3.DatabaseError):
                backup_history(source, destination)
            self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
