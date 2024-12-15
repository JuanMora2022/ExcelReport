import time
from BD.execution_query import ExecutionQuery
import BD.query_db as queries
from BD.record_manger import RecordManager
from datetime import datetime, timedelta
import pdb
import traceback
import json

class CreatioReport(RecordManager):
    def __init__(self, oc_connection, pg_connection):
        super().__init__(oc_connection, pg_connection)
        self.pg_connection
        self.oc_connection

    def execute(self, type_error):
        try:
            print(type_error)
        except Exception as e:
            print("ERROR")