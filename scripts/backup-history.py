"""Create a consistent, non-overwriting backup of DomainCheck SQLite history."""

import argparse
import json
import sqlite3
from contextlib import closing
from pathlib import Path


def backup_history(source: Path, destination: Path) -> dict[str, object]:
    source = source.resolve(strict=True)
    destination = destination.resolve()
    if source == destination:
        raise ValueError("Source and destination must differ")
    with closing(sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)) as connection:
        connection.execute("BEGIN")
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise ValueError("Source integrity check failed")
        rows = connection.execute("SELECT COUNT(*) FROM scans").fetchone()[0]
        # Exclusive creation prevents overwriting another backup, including races.
        with destination.open("xb"):
            pass
        with closing(sqlite3.connect(destination)) as backup:
            connection.backup(backup)
            backup_integrity = backup.execute("PRAGMA integrity_check").fetchone()[0]
            backup_rows = backup.execute("SELECT COUNT(*) FROM scans").fetchone()[0]
            if backup_integrity != "ok" or rows != backup_rows:
                raise ValueError(
                    "Backup verification failed; preserve file for diagnosis"
                )
        return {"integrity": backup_integrity, "records": backup_rows}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    try:
        result = backup_history(args.source, args.destination)
    except (OSError, ValueError, sqlite3.Error) as error:
        parser.exit(1, f"Backup failed: {error}\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
