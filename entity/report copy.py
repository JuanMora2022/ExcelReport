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
    def __init__(self, oc_connection, pg_connection):
        super().__init__(oc_connection, pg_connection)
        self.pg_connection
        self.oc_connection
        
        
    import os

    def execute(self):
        while True:
            try:
                os.system('cls')  # cambiar a clear en linux
                print("+++++++++++++++ Seleccione tipo de reporte +++++++++++")
                print("1. Reporte Novedad Fichas Nuevas")
                print("21. Salir")
                print("++++++++++++++++++++++++++++++++++++")
                
                report = int(input("Seleccione el reporte a ejecutar: "))
                print("        ")
                
                if report == 1:
                    self._create_report_type_one()
                
                elif report == 21:
                    print("Saliendo...")
                    break  
                else:
                    print("Opción no válida, intente nuevamente.")
                
                input("Presione Enter para continuar...")  
                
            except Exception as e:
                print(f"Ocurrió una excepción al crear el reporte: {e}")
                import traceback
                traceback.print_exc()  # Esto imprimirá el stack trace completo

    def _create_report_type_one(self):
        query = queries_oc.get_record_oc()
        print(f"Ejecutando consulta: {query}")
        records = self.select_oc(query, {}, False)
        return records

            
            
        

        
            

