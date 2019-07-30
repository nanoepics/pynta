import sqlite3
from pathlib import Path
from typing import Tuple

import yaml

from pynta.util import get_logger

logger = get_logger(__name__)


def initialize_database() -> Tuple[sqlite3.Connection, sqlite3.Cursor]:
    """ We are using a simple SQLite database to store some information regarding the use of the program. The most
    important feature is being able to store the latest set parameters in such a way the they can be recovered when
    restarting the program. If the database does not exist, it should be created.
    """
    home = Path.home()
    pynta_path = Path(home, '.pynta')
    if not pynta_path.is_dir():
        try:
            pynta_path.mkdir()
        except PermissionError:
            logger.error(f'This user does not have access to {pynta_path}. Consider another directory')
            raise

    database_path = Path(pynta_path, 'config.sqlite')
    if not database_path.is_file():
        logger.info('Going to create a new database')
        conn = sqlite3.connect(str(database_path))
        cur = conn.cursor()
        sql_command = """CREATE TABLE configs (
                            id INTEGER PRIMARY KEY AUTOINCREMENT, 
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, 
                            name VARCHAR, 
                            description VARCHAR)
                            """
        cur.execute(sql_command)
        sql_command = """CREATE TABLE users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name VARCHAR
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)
                            """
        cur.execute(sql_command)
        sql_command = """CREATE TABLE samples (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name VARCHAR,
                            description TEXT
                            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP) 
                            """
        cur.execute(sql_command)
        sql_command = """CREATE TABLE experiments (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name VARCHAR,
                            user_id INTEGER NOT NULL,
                                FOREIGN KEY (user_id) REFERENCES users(id))
        """
        cur.execute(sql_command)
        sql_command = """INSERT INTO configs (name, description)
        VALUES 
        ('Initial Database', 'Starting Fiber Tracking for the first time')
        """
        cur.execute(sql_command)
        conn.commit()
    else:
        logger.info('Database found')
        conn = sqlite3.connect(str(database_path))
        cur = conn.cursor()
    return conn, cur


def store_config(db: Tuple[sqlite3.Connection, sqlite3.Cursor], config: dict) -> None:
    conn = db[0]
    cur = db[1]
    data = yaml.dump(config)
    sql_command = f"""INSERT INTO configs (name, description) VALUES 
    ('Saved Config', '{data}')
    """
    cur.execute(sql_command)
    conn.commit()

