import sqlite3

DATABASE_PATH = 'database.db'

def connect_to_db():
    """Connect to the SQLite database."""
    return sqlite3.connect(DATABASE_PATH)

def create_table():
    """Create the videos table with updated column names."""
    with connect_to_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                uploader_name TEXT,
                unique_code TEXT DEFAULT '#0000',
                datetime TEXT,
                title TEXT,
                extension TEXT,
                file_path TEXT,
                filename TEXT,
                uploaded INTEGER DEFAULT 0
            )
        ''')

def get_all_videos():
    """Fetch all videos."""
    with connect_to_db() as conn:
        return conn.execute("SELECT * FROM videos").fetchall()

def update_video_path(video_id, new_path):
    """Update the file_path of a video entry."""
    with connect_to_db() as conn:
        conn.execute("UPDATE videos SET file_path = ? WHERE id = ?", (new_path, video_id))

def is_code_unique(uploader_name, code):
    """Check if the unique code is already used by the uploader."""
    with connect_to_db() as conn:
        result = conn.execute("SELECT COUNT(*) FROM videos WHERE uploader_name = ? AND unique_code = ?", (uploader_name, code)).fetchone()
        return result[0] == 0

def update_unique_code(video_id, new_code):
    """Update the unique code for a video entry."""
    with connect_to_db() as conn:
        conn.execute("UPDATE videos SET unique_code = ? WHERE id = ?", (new_code, video_id))

def update_uploaded_status(video_id, status):
    """Update the uploaded status for a video entry."""
    with connect_to_db() as conn:
        conn.execute("UPDATE videos SET uploaded = ? WHERE id = ?", (1 if status else 0, video_id))

def delete_video_from_db(video_id):
    """Delete a video entry from the database by its ID."""
    with connect_to_db() as conn:
        conn.execute("DELETE FROM videos WHERE id = ?", (video_id,))
        conn.commit()
