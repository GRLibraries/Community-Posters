import sqlite3
import json

DATABASE_FILE = "database/posters.db"
JSON_OUTPUT_FILE = "frontend/posters.json"

def create_db_connection():
    """Creates a database connection."""
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
    except sqlite3.Error as e:
        print(e)
    return conn

def get_posters_with_tags(conn):
    """Retrieves all posters and their associated tags."""
    cur = conn.cursor()
    cur.execute("""
        SELECT p.id, p.image_path, GROUP_CONCAT(t.name)
        FROM posters p
        LEFT JOIN poster_tags pt ON p.id = pt.poster_id
        LEFT JOIN tags t ON pt.tag_id = t.id
        GROUP BY p.id
    """)

    posters = []
    for row in cur.fetchall():
        poster_id, image_path, tags_str = row
        tags = tags_str.split(',') if tags_str else []
        posters.append({
            "id": poster_id,
            "image_path": image_path,
            "tags": tags
        })
    return posters

def main():
    """Main function to generate the static JSON file."""
    db_conn = create_db_connection()
    if db_conn:
        posters_data = get_posters_with_tags(db_conn)
        db_conn.close()

        with open(JSON_OUTPUT_FILE, 'w') as f:
            json.dump(posters_data, f, indent=4)

        print(f"Successfully generated {JSON_OUTPUT_FILE} with {len(posters_data)} posters.")

if __name__ == "__main__":
    main()
