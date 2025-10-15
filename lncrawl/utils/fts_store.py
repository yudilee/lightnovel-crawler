import sqlite3
from typing import Iterable, List, Mapping, Tuple

# ------------------------------------------------------------------ #
#                             SQL Queries                            #
# ------------------------------------------------------------------ #

_INIT_SQL = """
    CREATE VIRTUAL TABLE store USING fts5(
        key,
        value UNINDEXED
    );
"""

_SEARCH_SQL = """
    SELECT value FROM store WHERE key MATCH ?
"""

_COUNT_SQL = """
    SELECT COUNT(*) FROM store
"""

_INSERT_SQL = """
    INSERT INTO store(key, value) VALUES (?, ?)
"""

_DELETE_SQL = """
    DELETE FROM store WHERE key = ?
"""

_DELETE_MATCHING_SQL = """
    DELETE FROM store WHERE key MATCH ?
"""

_PURGE_SQL = """
    DELETE FROM store; VACUUM;
"""


# ------------------------------------------------------------------ #
#                              FTSStore                              #
# ------------------------------------------------------------------ #

class FTSStore:
    """Utility class for key-value substring search using SQLite FTS5."""

    def __init__(self):
        """Initialize the in-memory FTSStore."""
        self._db = sqlite3.connect(":memory:")
        self._db.execute(_INIT_SQL)

    def close(self):
        """Close the database connection."""
        self._db.close()

    def clear(self):
        """Remove all items, and cleanup memory."""
        self._db.executescript(_PURGE_SQL)

    def count(self) -> int:
        """Returns number of items in the store"""
        c = self._db.execute(_COUNT_SQL)
        return c.fetchone()[0]

    def search(self, query: str) -> List[str]:
        """Perform a full-text search on key and return values."""
        query += '*'  # for prefix match
        c = self._db.execute(_SEARCH_SQL, [query])
        return list(set([r[0] for r in c.fetchall()]))

    def insert_dict(self, mapping: Mapping[str, str]):
        """Insert multiple items from a key-value mapping"""
        with self._db:
            self._db.executemany(_DELETE_SQL, [[k] for k in mapping.keys()])
            self._db.executemany(_INSERT_SQL, mapping.items())

    def insert(self, key: str, value: str):
        """Insert a single item."""
        self.insert_dict({key: value})

    def insert_keys(self, keys: Iterable[str], value: str):
        """Assign same value to multiple keys"""
        self.insert_dict({key: value for key in keys})

    def insert_pairs(self, pairs: Iterable[Tuple[str, str]]):
        """Insert multiple items."""
        self.insert_dict(dict(pairs))

    def delete_many(self, keys: Iterable[str]):
        """Insert multiple items by key."""
        with self._db:
            self._db.executemany(_DELETE_SQL, [[k] for k in keys])

    def delete(self, key: str):
        """Delete an item by key."""
        self.delete_many([key])

    def search_and_delete(self, query: str):
        """Insert multiple items by key."""
        query += '*'  # for prefix match
        self._db.execute(_DELETE_MATCHING_SQL, [query])


# ------------------------------------------------------------------ #
#                                Tests                               #
# ------------------------------------------------------------------ #
if __name__ == '__main__':
    from rich import print
    from rich.traceback import Traceback

    def eqset(a, b):
        return set(a) == set(b)

    s = FTSStore()
    try:
        # fresh
        assert s.count() == 0

        # insert one
        s.insert("harry potter", "id:101")
        assert s.count() == 1
        assert eqset(s.search("har"), ["id:101"])  # token-prefix

        # upsert emulation (delete+insert inside insert_dict)
        s.insert("harry potter", "id:101-v2")
        assert s.count() == 1
        assert eqset(s.search("har"), ["id:101-v2"])

        # insert multiple keys with same value
        s.insert_keys(["harold", "harmony"], "id:200")
        assert s.count() == 3
        assert eqset(s.search("har"), ["id:101-v2", "id:200"])

        # insert pairs (mixed)
        s.insert_pairs([("ring", "id:300"), ("harvest moon", "id:400")])
        assert s.count() == 5
        assert eqset(s.search("har"), ["id:101-v2", "id:200", "id:400"])
        assert eqset(s.search("ring"), ["id:300"])

        # insert_dict batch with overwrite + new
        s.insert_dict({"harry potter": "id:101-v3", "harkness": "id:500"})
        assert s.count() == 6
        assert eqset(s.search("har"), ["id:101-v3", "id:200", "id:400", "id:500"])

        # delete_many some keys
        s.delete_many(["harmony", "ring"])
        assert s.count() == 4
        assert eqset(s.search("har"), ["id:101-v3", "id:200", "id:400", "id:500"])
        assert eqset(s.search("ring"), [])  # gone

        # delete single
        s.delete("harold")
        assert s.count() == 3
        assert eqset(s.search("har"), ["id:101-v3", "id:400", "id:500"])

        # search_and_delete by prefix (token-prefix)
        s.search_and_delete("har")  # deletes har*, i.e., harry potter, harvest moon, harkness
        assert s.count() == 0

        # repopulate and clear()
        s.insert_pairs([("alpha", "A"), ("beta", "B"), ("gamma", "C")])
        assert s.count() == 3
        s.clear()
        assert s.count() == 0

        print(":heavy_check_mark:  [bold green]Tests passed[/bold green]")
    except Exception:
        print(Traceback(show_locals=False))
    finally:
        s.close()
