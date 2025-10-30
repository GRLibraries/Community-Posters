import sqlite3
from sqlite3 import Error

def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        print(f"Successfully connected to {db_file}")
    except Error as e:
        print(e)
    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def main():
    database = r"database/posters.db"

    sql_create_posters_table = """ CREATE TABLE IF NOT EXISTS posters (
                                        id integer PRIMARY KEY,
                                        image_path text NOT NULL,
                                        extracted_text text,
                                        date_received text NOT NULL
                                    ); """

    sql_create_tags_table = """CREATE TABLE IF NOT EXISTS tags (
                                    id integer PRIMARY KEY,
                                    name text NOT NULL UNIQUE
                                );"""

    sql_create_poster_tags_table = """CREATE TABLE IF NOT EXISTS poster_tags (
                                          poster_id integer NOT NULL,
                                          tag_id integer NOT NULL,
                                          FOREIGN KEY (poster_id) REFERENCES posters (id),
                                          FOREIGN KEY (tag_id) REFERENCES tags (id),
                                          PRIMARY KEY (poster_id, tag_id)
                                      );"""

    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        create_table(conn, sql_create_posters_table)
        create_table(conn, sql_create_tags_table)
        create_table(conn, sql_create_poster_tags_table)
        print("Tables created successfully.")
        conn.close()
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()
