import BD.query_db as queries
from BD.execution_query import ExecutionQuery
from psycopg2 import sql
import cx_Oracle

class RecordManager(ExecutionQuery):
    def __init__(self, oc_connection, pg_connection):
        super().__init__(oc_connection, pg_connection)
        self.oc_connection = oc_connection
        self.pg_connection = pg_connection

    def _get_record_by_fic_id(self, query_select, ids):
        record = self.select_pg()