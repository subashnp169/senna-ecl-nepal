"""Read-only SQL view connector (institution-side)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import sqlite3


@dataclass
class SQLViewConfig:
    connection_string: str
    view_name: str
    as_of_date_column: str = "as_of_date"
    read_only: bool = True


class SQLViewConnector:
    def __init__(self, config: SQLViewConfig):
        self.config = config

    def fetch(self, as_of_date: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        # Generic fetch; in production use SQLAlchemy with read-only role.
        # Here we support sqlite for testing/demo.
        conn = sqlite3.connect(self.config.connection_string)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        q = f"SELECT * FROM {self.config.view_name} WHERE {self.config.as_of_date_column} = ?"
        if limit:
            q += f" LIMIT {int(limit)}"
        cur.execute(q, (as_of_date,))
        rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows
