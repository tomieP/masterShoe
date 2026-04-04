from BE.database.db import DatabaseManager

def get_db():
    db = DatabaseManager()
    db.connect()
    try:
        yield db
    except Exception:
        raise
    finally:
        db.close()

