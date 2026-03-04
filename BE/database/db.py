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

if __name__ == "__main__":
    db_manager = DatabaseManager()
    db_manager.connect()
    db_manager.init_database()
    db_manager.close()
