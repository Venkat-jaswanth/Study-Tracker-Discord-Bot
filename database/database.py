import psycopg2
from psycopg2._psycopg import connection
from logging import info, error
from typing import Any, List, Optional, Tuple

from config import DB_URL, DB_PORT, DB_NAME, DB_USER, DB_PASS


class Database:

    conn: Optional[connection] = None

    @staticmethod
    def establish_connection():
        Database.conn = psycopg2.connect(
            host=DB_URL,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
        )
        info("DATABASE: Connection established")

    @staticmethod
    def terminate_connection():
        assert Database.conn is not None
        Database.conn.close()
        info("DATABASE: Connection terminated")

    @staticmethod
    def get_connection():
        assert Database.conn is not None
        return Database.conn

    @staticmethod
    def get_cursor():
        return Database.get_connection().cursor()
    
    @staticmethod
    def commit():
        conn = Database.get_connection()
        conn.commit()

    @staticmethod
    def execute_query(query: str, *args: Any):
        try:
            with Database.get_cursor() as cur:
                cur.execute(query, args)
            Database.commit()
        except Exception as exc:
            Database.establish_connection()
            error(f"exc: {exc}\nquery: {query}\nargs: {args}", exc_info=True)

    @staticmethod
    def fetch_many(query: str, *args: Any) -> List[Tuple[Any, ...]]:
        with Database.get_cursor() as cur:
            cur.execute(query, args)
            result = cur.fetchall()
            return result

    @staticmethod
    def fetch_one(query: str, *args: Any) -> Tuple[Any, ...]:
        """
        :raises ValueError: if no result is found
        """
        with Database.get_cursor() as cur:
            cur.execute(query, args)
            result = cur.fetchone()
            if result is None:
                raise ValueError("No result found")
            return result
