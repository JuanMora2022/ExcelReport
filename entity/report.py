import bd.queries_pg
import bd.queries_oc
from bd.querys_db import QuerysDB
from bd.record_manager import RecordManager
import logging
import traceback
from psycopg2 import sql
from datetime import date
import pdb
import time
import os


class ReportProcess(RecordManager):
    def __init__(self, oc_connection, pg_connection, type_report):
        super().__init__(oc_connection, pg_connection)
        self.pg_connection = pg_connection  
        self.oc_connection = oc_connection
        self.type_report = type_report
        

    def execute(self):
        try:
         
            if self.type_report == 1:
                self._create_report_type_one()
            else:
                print("Tipo de reporte no válido.")
                
        except Exception as e:
            print(f"Ocurrió una excepción al crear el reporte: {e}")
            import traceback
            traceback.print_exc()

    def _create_report_type_one(self):
        records = self.select_oc(
            queries_oc.get_record_oc(), {}, False
        )
        return records

            

