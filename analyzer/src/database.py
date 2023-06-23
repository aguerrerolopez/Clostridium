import os
import pymysql
from pymysql.connections import Connection
from typing import Dict, List, Union

def db_connect() -> Connection:
    """Open connection to database"""
    return pymysql.connect(
        host=os.environ['DB_HOST'],
        user=os.environ['DB_USER'],
        passwd=os.environ['DB_PASS'],
        db=os.environ['DB_NAME'],
    )

def db_disconnect(conn: Connection):
    """Close connection to database"""
    conn.close()

def db_query(conn: Connection, sql: str, params: List[Union[str, int]] = []) -> List[Dict[str, any]]:
    """Make database query and get results"""
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor.execute(sql, params)
    res = cursor.fetchall()
    cursor.close()
    return res
