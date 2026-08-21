import sqlite3
from app.config import DB_PATH

class Database:
    def __init__(self):
        with sqlite3.connect(DB_PATH) as c:
            c.executescript("""
            PRAGMA foreign_keys=ON;

            CREATE TABLE IF NOT EXISTS tracks(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                artist TEXT NOT NULL,
                album TEXT NOT NULL,
                genre TEXT NOT NULL,
                path TEXT UNIQUE NOT NULL,
                cover TEXT,
                duration REAL DEFAULT 0,
                favorite INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS playlists(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                cover TEXT
            );

            CREATE TABLE IF NOT EXISTS playlist_tracks(
                playlist_id INTEGER NOT NULL,
                track_id INTEGER NOT NULL,
                position INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY(playlist_id, track_id),
                FOREIGN KEY(playlist_id) REFERENCES playlists(id) ON DELETE CASCADE,
                FOREIGN KEY(track_id) REFERENCES tracks(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS history(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                track_id INTEGER NOT NULL,
                played_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(track_id) REFERENCES tracks(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS settings(
                key TEXT PRIMARY KEY,
                value TEXT
            );
            """)

    def _rows(self, sql, params=()):
        with sqlite3.connect(DB_PATH) as c:
            c.row_factory = sqlite3.Row
            return c.execute(sql, params).fetchall()

    def _row(self, sql, params=()):
        rows = self._rows(sql, params)
        return rows[0] if rows else None

    def upsert_track(self, x):
        with sqlite3.connect(DB_PATH) as c:
            c.execute("""
            INSERT INTO tracks(title,artist,album,genre,path,cover,duration)
            VALUES(?,?,?,?,?,?,?)
            ON CONFLICT(path) DO UPDATE SET
              title=excluded.title, artist=excluded.artist,
              album=excluded.album, genre=excluded.genre,
              cover=excluded.cover, duration=excluded.duration
            """, (
                x["title"], x["artist"], x["album"], x["genre"],
                x["path"], x["cover"], x["duration"]
            ))

    def tracks(self, query=""):
        if not query:
            return self._rows("SELECT * FROM tracks ORDER BY title COLLATE NOCASE")
        q=f"%{query}%"
        return self._rows("""
            SELECT * FROM tracks
            WHERE title LIKE ? OR artist LIKE ? OR album LIKE ? OR genre LIKE ?
            ORDER BY title COLLATE NOCASE
        """, (q,q,q,q))

    def track(self, track_id):
        return self._row("SELECT * FROM tracks WHERE id=?", (track_id,))

    def favorites(self):
        return self._rows("SELECT * FROM tracks WHERE favorite=1 ORDER BY title COLLATE NOCASE")

    def toggle_favorite(self, track_id):
        with sqlite3.connect(DB_PATH) as c:
            c.execute("UPDATE tracks SET favorite=CASE favorite WHEN 1 THEN 0 ELSE 1 END WHERE id=?", (track_id,))

    def add_history(self, track_id):
        with sqlite3.connect(DB_PATH) as c:
            c.execute("INSERT INTO history(track_id) VALUES(?)", (track_id,))

    def recent(self, limit=12):
        return self._rows("""
            SELECT t.* FROM tracks t
            JOIN history h ON h.track_id=t.id
            GROUP BY t.id
            ORDER BY MAX(h.played_at) DESC
            LIMIT ?
        """, (limit,))

    def playlists(self):
        return self._rows("SELECT * FROM playlists ORDER BY name COLLATE NOCASE")

    def create_playlist(self, name):
        with sqlite3.connect(DB_PATH) as c:
            c.execute("INSERT OR IGNORE INTO playlists(name) VALUES(?)", (name.strip(),))

    def delete_playlist(self, playlist_id):
        with sqlite3.connect(DB_PATH) as c:
            c.execute("DELETE FROM playlists WHERE id=?", (playlist_id,))

    def playlist(self, playlist_id):
        return self._row("SELECT * FROM playlists WHERE id=?", (playlist_id,))

    def playlist_tracks(self, playlist_id):
        return self._rows("""
            SELECT t.* FROM tracks t
            JOIN playlist_tracks pt ON pt.track_id=t.id
            WHERE pt.playlist_id=?
            ORDER BY pt.position
        """, (playlist_id,))

    def add_to_playlist(self, playlist_id, track_id):
        with sqlite3.connect(DB_PATH) as c:
            exists=c.execute(
                "SELECT 1 FROM playlist_tracks WHERE playlist_id=? AND track_id=?",
                (playlist_id,track_id)
            ).fetchone()
            if exists:
                return
            pos=c.execute(
                "SELECT COALESCE(MAX(position),-1)+1 FROM playlist_tracks WHERE playlist_id=?",
                (playlist_id,)
            ).fetchone()[0]
            c.execute(
                "INSERT INTO playlist_tracks(playlist_id,track_id,position) VALUES(?,?,?)",
                (playlist_id,track_id,pos)
            )

    def remove_from_playlist(self, playlist_id, track_id):
        with sqlite3.connect(DB_PATH) as c:
            c.execute(
                "DELETE FROM playlist_tracks WHERE playlist_id=? AND track_id=?",
                (playlist_id,track_id)
            )

    def get_setting(self, key, default=None):
        row=self._row("SELECT value FROM settings WHERE key=?", (key,))
        return row["value"] if row else default

    def set_setting(self, key, value):
        with sqlite3.connect(DB_PATH) as c:
            c.execute(
                "INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key,str(value))
            )
