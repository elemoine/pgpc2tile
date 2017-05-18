import psycopg2.pool
import multiprocessing

from .exception import Pgpc2tileException


_pool = None


def init(dbstring):
    scheme = 'postgresql://'
    if not dbstring.startswith(scheme):
        dbstring = scheme + dbstring

    global _pool
    _pool = psycopg2.pool.ThreadedConnectionPool(
            1, multiprocessing.cpu_count(), dbstring)


def query(query, parameters=None):
    if not _pool:
        raise Pgpc2tileException('database uninitialized')
    conn = _pool.getconn()
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(query, parameters)
    res = cur.fetchall()
    _pool.putconn(conn)
    return res
