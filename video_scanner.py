import os
import re
from video_database import connect_to_db

# Adjusted pattern to match datetime with either ':' or ';'
PATTERN = re.compile(r'\[?(\d{4}-\d{2}-\d{2} \d{2}[:;]\d{2})\](.+?) – (.+?)\.(mp4|ts|webm)')

def scan_directory(folder_path):
    """Scan the specified folder for video files."""
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(('.ts', '.mp4', '.webm')):
                metadata = extract_metadata(file)
                if metadata:
                    datetime, uploader, title, ext = metadata
                    # Insert the video into the database with the correct datetime format
                    add_video_to_db(file, datetime, uploader, title, ext, '')

def extract_metadata(filename):
    """Extract metadata from the filename."""
    match = PATTERN.match(filename)
    if match:
        datetime, uploader, title, ext = match.groups()
        # Replace ';' with ':' in the extracted datetime
        datetime = datetime.replace(';', ':')
        return datetime, uploader, title, ext
    return None

def add_video_to_db(filename, datetime, uploader, title, ext, file_path):
    """Insert a new video entry into the database."""
    with connect_to_db() as conn:
        conn.execute('''
            INSERT INTO videos (filename, datetime, uploader_name, title, extension, file_path, uploaded)
            VALUES (?, ?, ?, ?, ?, ?, 0)
        ''', (filename, datetime, uploader, title, ext, file_path))
