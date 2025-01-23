import bd.queries_pg as queries_pg
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
import cx_Oracle


class ReportProcess(RecordManager):
    def __init__(self, oc_connection, pg_connection, type_report):
        super().__init__(oc_connection, pg_connection)
        self.pg_connection = pg_connection  
        self.oc_connection = oc_connection
        self.type_report = type_report
        
  
        
    def _extract_headers(self, query):
        try:
            # Usa el método select_oc de ExecutionQuery para ejecutar la consulta
            cursor = self.select_oc(query, one=False)
            
            if cursor:  
                headers = [col[0] for col in cursor.description]  # Extraemos los encabezados desde la descripción del cursor
                return headers
            return []
        except Exception as e:
            logging.error(f"Ocurrió un error al extraer los encabezados: {e}")
            return []

        

    def execute(self):
        try:
            
            #prueba sin reporte
            if self.type_report == 1:
                result = self._create_report_type_one()
                
            #Novedad fichas nuevas        
            elif self.type_report ==2:
                result = self._create_report_type_two()
                
            #persona  
            elif self.type_report ==3:
                result = self._create_report_type_three()
                
            elif self.type_report ==4:
                result = self._create_report_type_four()
                
            elif self.type_report ==5:
                result = self._test_call_pg()
                
            else:
                result="Tipo de reporte no válido."
                
            print(result)
                
        except Exception as e:
            print(f"Ocurrió una excepción al crear el reporte: {e}")
            import traceback
            traceback.print_exc()
            
    def _create_call_records_pg(self,params):
                
                query, params = queries_pg.get_record_pg(params)
                records = self.select_pg(query, params, False)

                return records if records else None
            
    
    def _execute_info_basic_data_records(self, fic_ids):
        query, params = queries_oc.get_info_basic_data_records(fic_ids) 
        records = self.select_oc(query, params,False) 
        return records if records else None           
            
    def _execute_query_fichas(self):
        records = self.select_oc(queries_oc.get_record_oc(), (), False)
        return records if records else None  
            
    def _execute_query_novedad_fichas(self):
        records = self.select_oc(queries_oc.get_novedad_fichas_nuevas(), (), False)
        return records if records else None  

    def _execute_query_persona(self, num_doc_identidad):
        query, params = queries_oc.get_persona(num_doc_identidad)
        records = self.select_oc(query, params, False)
        return records if records else None

    
    def _create_report_type_one(self): #funciona el script?
        report_process = ExcelProcess(self.oc_connection,self.pg_connection)
        records = self._execute_query_fichas()
        return records if records else None  
    
    def _create_report_type_two(self): #Novedad_Fichas_Nuevas
        report_process = ExcelProcess(self.oc_connection,self.pg_connection)
        novedad_fichas_nuevas= self._execute_query_novedad_fichas()
        if not novedad_fichas_nuevas:
             return "No se generó el reporte porque no hay Novedades de fichas nuevas"
        else:
            column_headers_oc = self.get_column_headers(queries_oc.get_novedad_fichas_nuevas(), db_type="oc")

            report_process._build_file(name_file="Novedad_Fichas_Nuevas",format_report="xlsx",report_contend=novedad_fichas_nuevas,headers=column_headers_oc) 
            return "reporte generado"
         
    
    def _create_report_type_three(self): #Consulta_persona
        
        num_doc_identidad = int(input("Ingrese el documento de identidad sin puntos ni comas: ")) 
        
        report_process = ExcelProcess(self.oc_connection, self.pg_connection)
        
        novedad_persona = self._execute_query_persona(num_doc_identidad)
        if not novedad_persona:
            return "No se generó el reporte porque no hay datos de la persona"
        else:
            column_headers_oc = self.get_column_headers(queries_oc.get_persona(num_doc_identidad)[0], db_type="oc")
            report_process._build_file(name_file="Consulta_persona", format_report="xlsx", report_contend=novedad_persona, headers=column_headers_oc)
            return "Reporte de persona generado"
     
    #3144501,3142433,3141821
    def _create_report_type_four(self): #Información_básica_fichas
        report_process = ExcelProcess(self.oc_connection, self.pg_connection)
        
        #fic_ids = [3144501,3142433,3141821]  # Lista de IDs de ejemplo
        fic_ids_input = input("Ingrese los Fic_ids de las fichas separados por comas: ")
        fic_ids = [int(fic_id.strip()) for fic_id in fic_ids_input.split(",") if fic_id.strip().isdigit()]
        
        if not fic_ids:
            return "No se generó el reporte porque no se ingresaron fichas válidas. Verifique los datos ingresados."
        
        informacion_basica_fichas = self._execute_info_basic_data_records(fic_ids)

        if not informacion_basica_fichas:
            return "No se encontraron datos para generar el reporte."
        
        else:
            
            column_headers_records = self.get_column_headers(queries_oc.get_info_basic_data_records(fic_ids)[0], db_type="oc")
            column_headers_records.append("Notas")  
            
            fichas_dict = {row[0]: row for row in informacion_basica_fichas}
            # Lista final con todas las fichas incluyendo las que no tienen información
            fichas_completas = []
            
            for fic_id in fic_ids:
                if fic_id in fichas_dict:
                    fichas_completas.append(fichas_dict[fic_id])
                else:
                    print(f"La ficha {fic_id} no se encontró información.")
                    fichas_completas.append((fic_id, None, None, None, None, None, None,"No se encontró información de la ficha "))
           
            #mostrar sólo info existente column_headers_records sin el append,  informacion_basica_fichas
            report_process._build_file(
                name_file="Información_básica_fichas", 
                format_report="xlsx", 
                report_contend=fichas_completas, 
                headers=column_headers_records
            )
            
            return "Reporte de fichas generado con éxito."
          
          
        
    #    3146093,3145907,3145903
    def _test_call_pg(self):
        report_process = ExcelProcess(self.oc_connection, self.pg_connection)
        
        fic_ids_input = input("Ingrese los Fic_ids de las fichas separados por comas: ")
        fic_ids = [int(fic_id.strip()) for fic_id in fic_ids_input.split(",") if fic_id.strip().isdigit()]
        
        if not fic_ids:
            return "No se generó el reporte porque no se ingresaron fichas válidas. Verifique los datos ingresados."
        
        records_information = self._create_call_records_pg(fic_ids)
        
        #return  records_information
        ##############################################################################
        if not records_information:
            return "No se encontraron datos de las fichas"
        
        query, params = queries_pg.get_record_pg(fic_ids)
        column_headers_records = self.get_column_headers(query, params=params, db_type="pg")


        
        if column_headers_records is None:
            return "No se pudieron obtener los encabezados de las columnas."
        
        column_headers_records.append("Notas")
        
        fichas_dict = {row[0]: row for row in records_information}
        
        complete_records = []
        success = True
        
        for fic_id in fic_ids:
            if fic_id in fichas_dict:
                complete_records.append(fichas_dict[fic_id])
            else:
                print(f"La ficha {fic_id} no se encontró información.")
                success = False 
        
        if success:
            report_process._build_file(
                name_file="reporte de fichas postgres", 
                format_report="xlsx", 
                report_contend=complete_records, 
                headers=column_headers_records
            )
            return "Reporte de fichas generado con éxito."
        else:
            return "No se generó el reporte debido a que no se encontraron todas las fichas."


            
            
       
        
        
        
    
    
    
  
    


            

