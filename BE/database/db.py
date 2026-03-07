import sqlite3
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path = './BE/database/masterShoe.db'):
        self.db_path = Path(db_path)
        self.connection = None

    def connect(self):
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            self.connection.execute("PRAGMA foreign_keys = ON;")
            return self.connection
    
    def init_database(self):
        if self.connection is None:
            self.connect()
        
        schema_path = Path('./BE/database/schema.sql')

        with open(schema_path,"r", encoding= "utf-8") as schema_file:
            schema_data = schema_file.read()

        self.connection.executescript(schema_data)
        self.connection.commit()

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None

    def excute_query(self, query, params = (), fetch = True):
        '''
        Docstring for execute_query
        
        :param self: 
        :param query: 
        :param params: tuple
        :param fetch: quyêt định có lấy kết quả hay không
            true -> tra ve toan bo ket qua (list[tuple])
            false -> tra ve id mới nhất được thêm vào
        '''
        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit() 
            if fetch:
                return cursor.fetchall()
            return cursor.lastrowid 
        except Exception as e:
            print(f"error: {e}")
            self.connection.rollback()
            self.connection.close()
            return None
            
