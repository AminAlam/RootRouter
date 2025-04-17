import sqlite3
from typing import Union
import uuid


def generate_unique_id():
    return str(uuid.uuid4())


class database():
    def __init__(self) -> None:
        self.db_file = 'db_client.db'
        self.conn = self.create_connection(self.db_file)
        self.sql_create_table_moisture_sensors = """ CREATE TABLE IF NOT EXISTS moisture_sensors (
                                        sensor_name text NOT NULL,
                                        sensor_location float NOT NULL,
                                        file_format text NOT NULL,
                                        img_size_x integer NOT NULL DEFAULT 0,
                                        img_size_y integer NOT NULL DEFAULT 0,
                                        img_size_z integer NOT NULL DEFAULT 0,
                                        number_of_cubes integer NOT NULL DEFAULT 0,
                                        unique_id text NOT NULL,
                                        id integer primary key
                                    ); """

        self.create_table(self.conn, self.sql_create_table_images)
        self.create_table(self.conn, self.sql_create_table_cubes)
        self.create_table(self.conn, self.sql_create_table_detected_cells)
        self.create_table(self.conn, self.sql_create_table_napari_layers)

    def create_table(self, conn, create_table_sql):
        c = conn.cursor()
        c.execute(create_table_sql)
        conn.commit()
        c.close()

    def create_connection(self, db_file):
        conn = sqlite3.connect(db_file, check_same_thread=False)
        return conn
