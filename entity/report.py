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
import datetime


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
            #informacion basica de fichas   
            elif self.type_report ==4:
                result = self._create_report_type_four()
            #informacion general fichas postgres  
            elif self.type_report ==5:
                result = self._test_call_pg()
            #seguimiento de fichas "Reporte largo de catalina    
            elif self.type_report == 6:
                result= self._create_general_report()
            #fichas estado 13
            elif self.type_report == 7:
                result=self._create_report_records_state_thirteen()
                
                
            elif self.type=8:
                result=self._enrollment_verification()
                   
            else:
                result="Tipo de reporte no válido."
                
            print(result)
                
        except Exception as e:
            print(f"Ocurrió una excepción al crear el reporte: {e}")
            import traceback
            traceback.print_exc()
            
    def _parse_date(self,date_str):
        for fmt in ('%Y/%m/%d', '%Y-%m-%d'): 
            try:
                return datetime.datetime.strptime(date_str, fmt).strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue
        raise ValueError(f"Formato de fecha incorrecto: {date_str}. Usa YYYY/MM/DD o YYYY-MM-DD")

            
            
  
    
    def _execute_get_records_without_academic(self, params):
        query = queries_pg.get_records_without_academic() 
        records = self.select_pg(query, params) 
        return records if records else None

       
        
        
######################################################################################################   
    def _execute_active_instructors_pg(self,params) : 
            query, params = queries_pg.get_active_instructor(params)
            records = self.select_pg(query, params, False)
            return records if records else None  
        
    def _execute_active_instructors_sofia(self, fic_ids):
        query, params = queries_oc.get_active_instructor(fic_ids)
        records = self.select_oc(query, params, False)
        return records if records else None
    
    def _apprentice_report_sofia(self, fic_id):
        query, params = queries_oc.get_state_academic_records([fic_id])  
        records = self.select_oc(query, params, False)

        if not records:
            return "No se encontraron registros académicos en Sofía"

    
        formatted_records = [f"{amount} en estado {state}" for _, state, amount in records]

        return ", ".join(formatted_records) 

               
    def _execute_first_part_general_report(self,params):
            query, params = queries_pg.general_report_first_part(params)
            first_part = self.select_pg(query, params, False)
            return first_part if first_part else None
        
    def _execute_number_aprentices_pg(self,params):
        query, params = queries_pg.get_apprentices(params)
        records = self.select_pg(query, params, False)
        return records if records else None      
            
            
    def _general_report_builder(self, fic_ids):
        first_part = self._execute_first_part_general_report(fic_ids)
        instructor_production = self._execute_active_instructors_pg(fic_ids)  
        apprentices_postgres =self._execute_number_aprentices_pg(fic_ids)
        instructors_sofia = self._execute_active_instructors_sofia(fic_ids)
       
        
        return first_part, instructor_production,apprentices_postgres,instructors_sofia

        
        
  ##################################################################################      
            
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
        
        print(f'records_information {records_information}')
        
        if not records_information:
            return "No se encontraron datos de las fichas"
        
        else:
            query, params = queries_pg.get_record_pg(fic_ids)
            column_headers_records = self.get_column_headers(query, params=params, db_type="pg")
            if column_headers_records is None:
                return "No se pudieron obtener los encabezados de las columnas."
            fichas_dict = {row[0]: row for row in records_information}
            complete_records = []
            success = True
            
            for fic_id in fic_ids:
                if fic_id in fichas_dict:
                    complete_records.append(fichas_dict[fic_id])
                else:
                  
                    print(f"La ficha {fic_id} no se encontró información.")
                    complete_records.append((fic_id,) + (None,) * 36 + ("No se encontró información de la ficha",))
                    #success = False 
            
            if success:
                report_process._build_file(
                    name_file="reporte de fichas postgres", 
                    format_report="xlsx", 
                    report_contend=complete_records, 
                    headers=column_headers_records
                )
                return "Reporte de fichas generado con éxito."
           


 
    def _create_general_report(self):
        report_process = ExcelProcess(self.oc_connection, self.pg_connection)
        use_default_fic_ids = False  # False para ingresar datos Manuales-True para que los lea de una variable
        if use_default_fic_ids:
            fic_ids = [3145903,3089232,3125865,3036645]  # Lista con un valor fijo para pruebas
        else:
            fic_ids_input = input("Ingrese los Fic_ids de las fichas separados por comas: ")
            fic_ids = [int(fic_id.strip()) for fic_id in fic_ids_input.split(",") if fic_id.strip().isdigit()]
        
        if not fic_ids:
            return "No se generó el reporte porque no se ingresaron fichas válidas. Verifique los datos ingresados."
        
        else:
            first_part, instrutor_production,apprentices_postgres,instructors_sofia= self._general_report_builder(fic_ids)

            reporte_dict = {}
            for i, fic_id in enumerate(fic_ids):
                academic_record_sofia = self._apprentice_report_sofia(fic_id)
            
                reporte_dict[fic_id] = {
                    
                    "Número de ficha": fic_id,
                    "Programa de formación": first_part[i][1] if i < len(first_part) else "N/A",
                    "Course ID": first_part[i][2] if i < len(first_part) else "N/A",
                    "Fecha inicio de formación": first_part[i][3] if i < len(first_part) else "N/A",
                    "Fecha fin de formación": first_part[i][4] if i < len(first_part) else "N/A",
                    "Código programa formación": first_part[i][5] if i < len(first_part) else "N/A",
                    "Número de instructores en Zajuna": instrutor_production[i][1] if i < len(instrutor_production) else "N/A",
                    "Número de aprendices en Zajuna": apprentices_postgres[i][1] if i < len(apprentices_postgres) else "N/A",
                    "Aprendices Ruta de aprendizaje": "",
                    "Número de instructores en Sofía": instructors_sofia[i][1] if instructors_sofia and i < len(instructors_sofia) else "No se encontraron instructores vigentes",
                    "Reporte de aprendices sofia":academic_record_sofia,
                    "Notas": ""
                }

            # Obtener los encabezados del diccionario (clave del primer elemento)
            encabezados = list(reporte_dict[next(iter(reporte_dict))].keys())

            # Convertir diccionario en lista de listas para generar el reporte
            reporte_completo = [list(data.values()) for data in reporte_dict.values()]
            
            report_process._build_file(
                name_file="Seguimiento_fichas",
                format_report="xlsx",
                report_contend=reporte_completo,
                headers=encabezados
            )

            return "Reporte general de fichas generado con éxito."
     
        
  
    def _create_report_records_state_thirteen(self):
        
        #pdb.set_trace()
        manual = input("Desea ingresar fecha de inicio y fin  si (s)  no(n): ")
        if manual.lower() == "s":
            date_execute_one = input("Ingrese fecha Inicio (YYYY/MM/DD): ")
            date_execute_two = input("Ingrese fecha fin (YYYY/MM/DD): ")
            new_date_execute_one = self._parse_date(date_execute_one)
            new_date_execute_two = self._parse_date(date_execute_two)
           
        else:
            new_date_execute_one = '2025-01-01 00:00:00'
            new_date_execute_two= '2025-02-28 00:00:00'
            
        params = (new_date_execute_one, new_date_execute_two) 
        
        result = self._execute_get_records_without_academic(params)
        
        print(result)
        
        
 

  
            
       
        
        
        
    
    
    
  
    


            

