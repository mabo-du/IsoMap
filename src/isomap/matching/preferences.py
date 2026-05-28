"""preferences.py — SQLite user preference cache for column mappings.
exports: PreferenceCache class
used_by: mapper.py -> PreferenceCache
rules:
Must create SQLite database if it doesn't exist.
"""

import sqlite3
import datetime
from pathlib import Path
from typing import Optional, List, Dict

class PreferenceCache:
    def __init__(self, db_path: str = "data/preferences.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        
    def _init_db(self):
        """Initializes the SQLite database with the necessary table."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS UserPreference (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_column_normalised TEXT NOT NULL,
                    target_field TEXT NOT NULL,
                    repository TEXT,
                    frequency INTEGER DEFAULT 1,
                    last_used TIMESTAMP,
                    UNIQUE(source_column_normalised, target_field, repository)
                )
            ''')
            conn.commit()

    def get_preference(self, norm_source: str, repository: Optional[str] = None) -> Optional[str]:
        """
        Retrieves the most frequently used target_field for a normalized source column.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if repository:
                cursor.execute('''
                    SELECT target_field FROM UserPreference
                    WHERE source_column_normalised = ? AND (repository = ? OR repository IS NULL)
                    ORDER BY frequency DESC, last_used DESC LIMIT 1
                ''', (norm_source, repository))
            else:
                cursor.execute('''
                    SELECT target_field FROM UserPreference
                    WHERE source_column_normalised = ?
                    ORDER BY frequency DESC, last_used DESC LIMIT 1
                ''', (norm_source,))
                
            row = cursor.fetchone()
            return row[0] if row else None

    def store_preference(self, norm_source: str, target_field: str, repository: Optional[str] = None):
        """
        Stores or updates a user mapping override in the preference cache.
        """
        now = datetime.datetime.now()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if exists
            cursor.execute('''
                SELECT id, frequency FROM UserPreference
                WHERE source_column_normalised = ? AND target_field = ? AND repository = ?
            ''', (norm_source, target_field, repository or ""))
            
            row = cursor.fetchone()
            
            if row:
                # Update
                pref_id, freq = row
                cursor.execute('''
                    UPDATE UserPreference
                    SET frequency = ?, last_used = ?
                    WHERE id = ?
                ''', (freq + 1, now, pref_id))
            else:
                # Insert
                cursor.execute('''
                    INSERT INTO UserPreference (source_column_normalised, target_field, repository, frequency, last_used)
                    VALUES (?, ?, ?, 1, ?)
                ''', (norm_source, target_field, repository or "", now))
                
            conn.commit()
