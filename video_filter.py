from video_database import connect_to_db

def get_filtered_videos(uploader_name=None, date_name=None, disk_name=None, sort_column=None, sort_order='ASC'):
    """
    Fetch videos based on filters and sorting criteria.
    :param uploader_name: Filter by uploader name (optional).
    :param date_name: Filter by date (optional, format YYYY-MM-DD).
    :param disk_name: Filter by disk path (optional).
    :param sort_column: Column to sort by (optional).
    :param sort_order: Sort order (ASC or DESC, default ASC).
    :return: List of filtered and sorted videos.
    """
    query = "SELECT * FROM videos WHERE 1=1"
    params = []

    # Add filters dynamically
    if uploader_name:
        query += " AND uploader_name LIKE ?"
        params.append(f"%{uploader_name}%")
    if date_name:
        query += " AND DATE(datetime) = ?"
        params.append(date_name)
    if disk_name:
        query += " AND file_path LIKE ?"
        params.append(f"%{disk_name}%")

    # Add sorting dynamically
    if sort_column:
        if sort_column in ['uploader_name', 'title', 'filename']:  # Case-insensitive for text columns
            query += f" ORDER BY {sort_column} COLLATE NOCASE {sort_order}"
        else:
            query += f" ORDER BY {sort_column} {sort_order}"

    with connect_to_db() as conn:
        return conn.execute(query, params).fetchall()
