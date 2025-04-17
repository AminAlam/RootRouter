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

        self.debug = True
        if self.debug:
            # remove all data from detected_cells
            c = self.conn.cursor()
            c.execute("DELETE FROM detected_cells")
            self.conn.commit()

    def create_table(self, conn, create_table_sql):
        c = conn.cursor()
        c.execute(create_table_sql)
        conn.commit()
        c.close()

    def create_connection(self, db_file):
        conn = sqlite3.connect(db_file, check_same_thread=False)
        return conn

    def insert_image(self, file_path: str, file_size: float, file_format: str, img_size_x: int, img_size_y: int, img_size_z: int):
        id = self.check_image_exists(file_path, file_size, file_format)
        if id is not None:
            return id
        sql = '''INSERT OR REPLACE INTO images(file_path, file_size, file_format, img_size_x, img_size_y, img_size_z, unique_id)
                    VALUES(?,?,?,?,?,?,?) '''

        unique_id = generate_unique_id()

        cur = self.conn.cursor()
        cur.execute('BEGIN EXCLUSIVE')
        cur.execute(sql, (file_path, file_size, file_format,
                    img_size_x, img_size_y, img_size_z, unique_id))
        self.conn.commit()
        id = cur.lastrowid
        cur.close()
        return id

    def get_unique_id_from_id(self, image_id: int):
        sql = '''SELECT unique_id FROM images WHERE id = ?'''

        cur = self.conn.cursor()
        cur.execute(sql, (image_id,))
        result = cur.fetchone()
        cur.close()

        if result:
            return result[0]  # Return the unique_id
        return None  # Return None if no record is found

    def update_image(self, image_id: int, number_of_cubes: int):
        sql = ''' UPDATE images
                    SET number_of_cubes = ?
                    WHERE id = ?'''
        cur = self.conn.cursor()
        cur.execute(sql, (number_of_cubes, image_id))
        self.conn.commit()
        id = cur.lastrowid
        cur.close()
        return id

    def get_image(self, image_id: int):
        sql = ''' SELECT file_path, file_size, file_format, img_size_x, img_size_y, img_size_z FROM images where id = ?'''
        cur = self.conn.cursor()
        cur.execute(sql, (image_id,))
        output = cur.fetchone()
        column_names = [description[0] for description in cur.description]
        output = dict(zip(column_names, output))
        cur.close()
        return output

    def get_image_size(self, image_id: int):
        sql = ''' SELECT img_size_x, img_size_y, img_size_z FROM images where id = ?'''
        cur = self.conn.cursor()
        cur.execute(sql, (image_id,))
        output = cur.fetchone()
        column_names = [description[0] for description in cur.description]
        output = dict(zip(column_names, output))
        cur.close()
        img_size = (output['img_size_x'],
                    output['img_size_y'], output['img_size_z'])
        return img_size

    def get_image_path(self, image_id: int):
        sql = ''' SELECT file_path FROM images where id = ?'''
        cur = self.conn.cursor()
        cur.execute(sql, (image_id,))
        output = cur.fetchone()
        cur.close()
        if output is not None:
            output = output[0]
        return output

    def check_image_exists(self, file_path: str, file_size: float, file_format: str):
        sql = ''' SELECT id FROM images where file_path = ? AND file_size = ? AND file_format = ?'''
        cur = self.conn.cursor()
        cur.execute(sql, (file_path, file_size, file_format))
        output = cur.fetchone()
        cur.close()
        if output is not None:
            return output[0]
        return None

    def insert_cube(self,
                    cube_x_start: int,
                    cube_x_end: int,
                    cube_y_start: int,
                    cube_y_end: int,
                    cube_z_start: int,
                    cube_z_end: int,
                    cube_size_bytes: int,
                    image_id: int,
                    cube_data: bytes,
                    cube_info_sent_to_server: bool = False,
                    cube_data_sent_to_server: bool = False):

        cube_id = self.check_cube_exists(cube_x_start=cube_x_start,
                                         cube_x_end=cube_x_end,
                                         cube_y_start=cube_y_start,
                                         cube_y_end=cube_y_end,
                                         cube_z_start=cube_z_start,
                                         cube_z_end=cube_z_end,
                                         image_id=image_id)
        if cube_id is not None:
            return cube_id

        sql = ''' INSERT OR REPLACE INTO cubes(cube_x_start, cube_x_end, cube_y_start, cube_y_end, cube_z_start, cube_z_end, cube_size_bytes, image_id, cube_info_sent_to_server, cube_data_sent_to_server, cube_data)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?) '''
        cur = self.conn.cursor()
        cur.execute('BEGIN EXCLUSIVE')
        cur.execute(sql, (cube_x_start, cube_x_end, cube_y_start, cube_y_end, cube_z_start, cube_z_end,
                    cube_size_bytes, image_id, cube_info_sent_to_server, cube_data_sent_to_server, cube_data))
        self.conn.commit()
        id = cur.lastrowid
        cur.close()

        return id

    def check_cube_exists(self,
                          cube_x_start: int,
                          cube_x_end: int,
                          cube_y_start: int,
                          cube_y_end: int,
                          cube_z_start: int,
                          cube_z_end: int,
                          image_id: int):
        sql = ''' SELECT id FROM cubes where cube_x_start = ? 
                                        AND cube_x_end = ?
                                        AND cube_y_start = ?
                                        AND cube_y_end = ?
                                        AND cube_z_start = ?
                                        AND cube_z_end = ?
                                        AND image_id = ?'''

        cur = self.conn.cursor()
        cur.execute(sql, (cube_x_start, cube_x_end, cube_y_start,
                    cube_y_end, cube_z_start, cube_z_end, image_id))
        output = cur.fetchone()
        cur.close()
        if output is not None:
            return output[0]
        return None

    def update_cube(self, cube_id: int, image_id: int,
                    cube_info_sent_to_server: bool = None,
                    cube_data_sent_to_server: bool = None,
                    received_soma_segmantation_from_server: bool = None,
                    received_branch_segmantation_from_server: bool = None,
                    cube_data_soma_segmentation: bytes = None,
                    cube_data_branch_segmentation: bytes = None):
        sql = ''' SELECT cube_info_sent_to_server, cube_data_sent_to_server, received_soma_segmantation_from_server, received_branch_segmantation_from_server,
                    cube_data_soma_segmentation, cube_data_branch_segmentation
                    FROM cubes WHERE id = ? AND image_id = ?'''
        cur = self.conn.cursor()
        cur.execute('BEGIN EXCLUSIVE')
        if type(cube_id) is not int or type(image_id) is not int:
            input('Error')
        cur.execute(sql, (cube_id, image_id))
        output = cur.fetchone()

        # get row names
        names = [description[0] for description in cur.description]
        output = dict(zip(names, output))
        if cube_info_sent_to_server == None:
            cube_info_sent_to_server = output['cube_info_sent_to_server']
        if cube_data_sent_to_server == None:
            cube_data_sent_to_server = output['cube_data_sent_to_server']
        if received_soma_segmantation_from_server == None:
            received_soma_segmantation_from_server = output['received_soma_segmantation_from_server']
        if received_branch_segmantation_from_server == None:
            received_branch_segmantation_from_server = output[
                'received_branch_segmantation_from_server']
        if cube_data_soma_segmentation == None:
            cube_data_soma_segmentation = output['cube_data_soma_segmentation']
        if cube_data_branch_segmentation == None:
            cube_data_branch_segmentation = output['cube_data_branch_segmentation']
        sql = ''' UPDATE cubes
                    SET cube_info_sent_to_server = ?,   
                        cube_data_sent_to_server = ?,   
                        received_soma_segmantation_from_server = ?,   
                        received_branch_segmantation_from_server = ?,   
                        cube_data_soma_segmentation = ?,   
                        cube_data_branch_segmentation = ?
                    WHERE id = ? AND image_id = ?'''

        cur = self.conn.cursor()
        cur.execute(sql, (cube_info_sent_to_server,
                          cube_data_sent_to_server,
                          received_soma_segmantation_from_server,
                          received_branch_segmantation_from_server,
                          cube_data_soma_segmentation,
                          cube_data_branch_segmentation,
                          cube_id,
                          image_id))
        self.conn.commit()
        id = cur.lastrowid
        cur.close()
        return id

    def get_cube_status(self, cube_id: int, image_id: int):
        sql = ''' SELECT cube_info_sent_to_server, cube_data_sent_to_server, received_soma_segmantation_from_server, received_branch_segmantation_from_server
                    FROM cubes
                    WHERE id = ? AND image_id = ?'''
        cur = self.conn.cursor()
        cur.execute(sql, (cube_id, image_id))
        output = cur.fetchone()
        cur.close()
        if output is not None:
            names = [description[0] for description in cur.description]
            output = dict(zip(names, output))
            output = {'cube_info_sent_to_server': output['cube_info_sent_to_server'],
                      'cube_data_sent_to_server': output['cube_data_sent_to_server'],
                      'received_soma_segmantation_from_server': output['received_soma_segmantation_from_server'],
                      'received_branch_segmantation_from_server': output['received_branch_segmantation_from_server']}
        else:
            output = {'cube_info_sent_to_server': False,
                      'cube_data_sent_to_server': False,
                      'received_soma_segmantation_from_server': False,
                      'received_branch_segmantation_from_server': False}
        return output

    def get_cubes_to_get_segmentation_results(self, segmentation_type: Union[str, str] = Union['soma', 'branch']):
        if segmentation_type not in ['soma', 'branch']:
            raise ValueError(
                "Invalid segmentation type. Must be 'soma' or 'branch'.")

        sql = f''' SELECT id, image_id
                    FROM cubes
                    WHERE received_{segmentation_type}_segmantation_from_server = 0 AND cube_data_sent_to_server = 1'''
        cur = self.conn.cursor()
        cur.execute(sql)
        output = cur.fetchall()
        description = [description[0] for description in cur.description]
        output = [dict(zip(description, row)) for row in output]
        cur.close()
        return output

    def get_cubes_not_sent_to_server_by_image_id(self, image_id: int):
        sql = ''' SELECT * FROM cubes
                    WHERE image_id = ? AND cube_data_sent_to_server = 0'''
        cur = self.conn.cursor()
        cur.execute(sql, (image_id,))
        output = cur.fetchall()
        description = [description[0] for description in cur.description]
        output = [dict(zip(description, row)) for row in output]
        cur.close()
        return output

    def get_cubes_number_by_image_id(self, image_id: int):
        sql = ''' SELECT count(*) FROM cubes WHERE image_id = ?'''
        cur = self.conn.cursor()
        cur.execute(sql, (image_id,))
        output = cur.fetchone()
        cur.close()
        if output is not None:
            output = output[0]
        else:
            output = 0
        return output

    def get_cubes_number_by_image_id_and_soma_segmentation(self, image_id: int):
        sql = ''' SELECT count(*) FROM cubes WHERE image_id = ? and received_soma_segmantation_from_server = 1'''
        cur = self.conn.cursor()
        cur.execute(sql, (image_id,))
        output = cur.fetchone()
        cur.close()
        if output is not None:
            output = output[0]
        else:
            output = 0
        return output

    def get_all_segmented_cubes_by_image_id(self, image_id: int, type: Union[str, str] = Union['soma', 'branch']):
        if type not in ['soma', 'branch']:
            raise ValueError(
                "Invalid segmentation type. Must be 'soma' or 'branch'.")
        sql = f''' SELECT * 
                    FROM cubes 
                    WHERE image_id = ? AND received_{type}_segmantation_from_server = 1
                    '''
        cur = self.conn.cursor()
        cur.execute(sql, (image_id,))
        output = cur.fetchall()
        description = [description[0] for description in cur.description]
        output = [dict(zip(description, row)) for row in output]
        cur.close()
        return output

    def get_all_cubes_by_image_id(self, image_id: int):
        sql = f''' SELECT * 
                    FROM cubes
                    WHERE image_id = ?
                    '''
        cur = self.conn.cursor()
        cur.execute(sql, (image_id,))
        output = cur.fetchall()
        description = [description[0] for description in cur.description]
        output = [dict(zip(description, row)) for row in output]
        cur.close()
        return output

    def check_cube_sent_to_server(self, image_id: int, cube_x_start: int, cube_x_end: int, cube_y_start: int, cube_y_end: int, cube_z_start: int, cube_z_end: int):
        sql = ''' SELECT cube_data_sent_to_server FROM cubes WHERE image_id = ? AND cube_x_start = ? AND cube_x_end = ? AND cube_y_start = ? AND cube_y_end = ? AND cube_z_start = ? AND cube_z_end = ?'''
        cur = self.conn.cursor()
        cur.execute(sql, (image_id, cube_x_start, cube_x_end,
                    cube_y_start, cube_y_end, cube_z_start, cube_z_end))
        output = cur.fetchone()
        cur.close()
        if output is not None:
            return output[0]
        return False

    def insert_cell(self, image_id: int, soma_x_pos: int, soma_y_pos: int, soma_z_pos: int, cube_over_cell: bytes = None, segmented_cube_over_cell: bytes = None):
        cell_id = self.check_cell_exists(
            image_id, soma_x_pos, soma_y_pos, soma_z_pos)
        if cell_id is not None:
            return cell_id
        sql = ''' INSERT OR REPLACE INTO detected_cells(soma_x_pos, soma_y_pos, soma_z_pos, cube_over_cell, segmented_cube_over_cell, image_id)
                    VALUES(?,?,?,?,?,?) '''
        cur = self.conn.cursor()
        cur.execute(sql, (soma_x_pos, soma_y_pos, soma_z_pos,
                    cube_over_cell, segmented_cube_over_cell, image_id))
        self.conn.commit()
        return cur.lastrowid

    def check_cell_exists(self, image_id: int, soma_x_pos: int, soma_y_pos: int, soma_z_pos: int):
        sql = ''' SELECT id FROM detected_cells where image_id = ? AND soma_x_pos = ? AND soma_y_pos = ? AND soma_z_pos = ?'''
        cur = self.conn.cursor()
        cur.execute(sql, (image_id, soma_x_pos, soma_y_pos, soma_z_pos))
        output = cur.fetchone()
        cur.close()
        if output is not None:
            return output[0]
        return None

    def get_cell(self, cell_id: int, image_id: int):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM detected_cells WHERE id = ? AND image_id = ?", (cell_id, image_id))
        row = cur.fetchone()
        if row is not None:
            column_names = [description[0] for description in cur.description]
            row = dict(zip(column_names, row))
            return row
        return None

    def get_cells_by_image_id(self, image_id: int):
        cur = self.conn.cursor()
        cur.execute(
            "SELECT * FROM detected_cells WHERE image_id = ?", (image_id,))
        output = cur.fetchall()
        if output is None or len(output) == 0:
            return None
        description = [description[0] for description in cur.description]
        output = [dict(zip(description, row)) for row in output]
        cur.close()
        return output

    def update_cell(self, cell_id: int, image_id: int, soma_x_pos: int = None, soma_y_pos: int = None, soma_z_pos: int = None, cube_over_cell: bytes = None, segmented_cube_over_cell: bytes = None):
        cell_info = self.get_cell(cell_id, image_id)
        if cell_info is None:
            return None
        if soma_x_pos is None:
            soma_x_pos = cell_info['soma_x_pos']
        if soma_y_pos is None:
            soma_y_pos = cell_info['soma_y_pos']
        if soma_z_pos is None:
            soma_z_pos = cell_info['soma_z_pos']
        if cube_over_cell is None:
            cube_over_cell = cell_info['cube_over_cell']
        if segmented_cube_over_cell is None:
            segmented_cube_over_cell = cell_info['segmented_cube_over_cell']

        sql = ''' UPDATE detected_cells
                    SET soma_x_pos = ? ,
                        soma_y_pos = ? ,
                        soma_z_pos = ? ,
                        cube_over_cell = ? ,
                        segmented_cube_over_cell = ?
                    WHERE id = ? AND image_id = ?'''

        cur = self.conn.cursor()
        cur.execute(sql, (soma_x_pos, soma_y_pos, soma_z_pos,
                    cube_over_cell, segmented_cube_over_cell, cell_id, image_id))
        self.conn.commit()
        return cell_id

    def update_napari_current_layer(self, file_path: str):
        # delete the previous entry
        sql = ''' DELETE FROM current_layer_napari'''
        cur = self.conn.cursor()
        cur.execute(sql)
        self.conn.commit()
        sql = ''' INSERT INTO current_layer_napari(file_path)
                    VALUES(?) '''
        cur = self.conn.cursor()
        cur.execute(sql, (file_path,))
        self.conn.commit()
        return cur.lastrowid

    def get_napaari_current_layer(self):
        sql = ''' SELECT file_path FROM current_layer_napari'''
        cur = self.conn.cursor()
        cur.execute(sql)
        output = cur.fetchone()
        cur.close()
        return output[0] if output is not None else None

    def count_number_of_cubes(self, image_id: int):
        sql = ''' SELECT count(*) FROM cubes WHERE image_id = ?'''
        cur = self.conn.cursor()
        cur.execute(sql, (image_id,))
        output = cur.fetchone()
        cur.close()
        return output[0]
