import sqlite3
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path


@dataclass
class Note:
    id: int
    telegram_message_id: int
    audio_file_id: str
    transcript: str
    category: str
    summary: str
    created_at: datetime
    included_in_summary_at: datetime | None


class Database:
    def __init__(self, db_path: str = "db/brain_dump.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_connection() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_message_id INTEGER,
                    audio_file_id TEXT,
                    transcript TEXT,
                    category TEXT,
                    summary TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    included_in_summary_at TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS daily_summaries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    summary_text TEXT,
                    notes_count INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT
                );
            """)

    def save_note(
        self,
        telegram_message_id: int,
        audio_file_id: str,
        transcript: str,
        category: str,
        summary: str,
    ) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO notes (telegram_message_id, audio_file_id, transcript, category, summary)
                VALUES (?, ?, ?, ?, ?)
                """,
                (telegram_message_id, audio_file_id, transcript, category, summary),
            )
            return cursor.lastrowid or 0

    def get_notes_for_summary(self, for_date: date | None = None) -> list[Note]:
        if for_date is None:
            for_date = date.today()

        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM notes
                WHERE date(created_at) = ?
                AND included_in_summary_at IS NULL
                ORDER BY created_at
                """,
                (for_date.isoformat(),),
            ).fetchall()

            return [self._row_to_note(row) for row in rows]

    def get_all_notes_for_date(self, for_date: date | None = None) -> list[Note]:
        if for_date is None:
            for_date = date.today()

        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT * FROM notes
                WHERE date(created_at) = ?
                ORDER BY created_at
                """,
                (for_date.isoformat(),),
            ).fetchall()

            return [self._row_to_note(row) for row in rows]

    def _row_to_note(self, row: sqlite3.Row) -> Note:
        return Note(
            id=row["id"],
            telegram_message_id=row["telegram_message_id"],
            audio_file_id=row["audio_file_id"],
            transcript=row["transcript"],
            category=row["category"],
            summary=row["summary"],
            created_at=datetime.fromisoformat(row["created_at"]),
            included_in_summary_at=datetime.fromisoformat(row["included_in_summary_at"])
            if row["included_in_summary_at"]
            else None,
        )

    def mark_notes_as_summarized(self, note_ids: list[int]) -> None:
        if not note_ids:
            return
        with self._get_connection() as conn:
            # Safe: placeholders are just "?" chars, values passed as parameters
            placeholders = ",".join("?" * len(note_ids))
            conn.execute(
                f"""
                UPDATE notes
                SET included_in_summary_at = CURRENT_TIMESTAMP
                WHERE id IN ({placeholders})
                """,  # nosec B608
                note_ids,
            )

    def save_daily_summary(self, summary_text: str, notes_count: int) -> int:
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO daily_summaries (summary_text, notes_count)
                VALUES (?, ?)
                """,
                (summary_text, notes_count),
            )
            return cursor.lastrowid or 0

    def get_today_notes_count(self) -> int:
        with self._get_connection() as conn:
            row = conn.execute(
                """
                SELECT COUNT(*) as count FROM notes
                WHERE date(created_at) = date('now')
                """
            ).fetchone()
            return int(row["count"]) if row else 0

    def get_last_note_time(self) -> datetime | None:
        with self._get_connection() as conn:
            row = conn.execute(
                """
                SELECT created_at FROM notes
                WHERE date(created_at) = date('now')
                ORDER BY created_at DESC
                LIMIT 1
                """
            ).fetchone()
            return datetime.fromisoformat(row["created_at"]) if row else None

    def get_setting(self, key: str, default: str | None = None) -> str | None:
        with self._get_connection() as conn:
            row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
            return str(row["value"]) if row else default

    def set_setting(self, key: str, value: str) -> None:
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
                """,
                (key, value),
            )

    def delete_old_notes(self, days: int = 7) -> int:
        """Delete notes older than specified days. Returns count of deleted notes."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                DELETE FROM notes
                WHERE created_at < datetime('now', ? || ' days')
                """,
                (f"-{days}",),
            )
            return cursor.rowcount
