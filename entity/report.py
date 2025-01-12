import bd.queries_pg
import bd.queries_oc as queries_oc
from bd.execution_query import ExecutionQuery
from bd.record_manager import RecordManager
from entity.excel import ExcelProcess
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
        
        self.oc_query = ExecutionQuery(self.oc_connection, self.pg_connection)
        

    def execute(self):
        try:
         
            if self.type_report == 1:
                result = self._create_report_type_one()
                    
            elif self.type_report ==2:
                result = self._create_report_type_two()
                
            elif self.type_report ==3:
                result = self._create_report_type_three()
                
            else:
                result="Tipo de reporte no válido."
                
            print(result)
                
        except Exception as e:
            print(f"Ocurrió una excepción al crear el reporte: {e}")
            import traceback
            traceback.print_exc()

    def _create_report_type_one(self):
        records = self.oc_query.select_oc(queries_oc.get_record_oc(), (), False)
        return records if records else None  
    
    def _create_report_type_two(self):
        records = self.oc_query.select_oc(queries_oc.get_novedad_fichas_nuevas(), (), False)
        return records if records else None  
    
    def _create_report_type_three(self):
        report_process = ExcelProcess(self.oc_connection,self.pg_connection)
        report_process._build_file(name_file="Consulta3",format_report="xlsx") 
        return "reporte generado"

    


            

