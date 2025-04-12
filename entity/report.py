import bd.queries_pg as queries_pg
import bd.queries_oc as queries_oc
from bd.execution_query import ExecutionQuery
from bd.record_manager import RecordManager
from entity.excel import ExcelProcess
from entity.archive import ArchiveProcess
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
    
    FOTMAT_REPORT = "csv" 
    
    GENERAL_REPORT_ARCHIVE = "SERVIDOR_PRUEBA_ORACLE_431_2 - Hoja 1.csv"
    BASIC_RECORDS_INFORMATION_REPORT="SERVIDOR_PRUEBA_ORACLE_431_2 - Hoja 1.csv"
    FICHAS_POSTGRES ="SERVIDOR_PRUEBA_ORACLE.csv"
    

    def __init__(self, oc_connection, pg_connection, type_report):
        super().__init__(oc_connection, pg_connection)
        self.pg_connection = pg_connection  
        self.oc_connection = oc_connection
        self.type_report = type_report
        
  
        
    def _extract_headers(self, query):
        try:
         
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
                '''elif self.type_report ==3:
                result = self._create_report_type_three()'''
            #informacion basica de fichas   
            elif self.type_report ==4:
                result = self._create_report_type_four()
            #informacion general fichas postgres  
            elif self.type_report ==5:
                result = self._test_call_pg()
            #seguimiento de fichas "Reporte largo de catalina    
            elif self.type_report == 6:
                result= self._create_general_report()
            #fichas sin registros academicos en postrges
            elif self.type_report == 7:
                result=self._create_report_records_state_thirteen()
                
                   
            else:
                result="Tipo de reporte no válido."
                
            print(result)
                
        except Exception as e:
            print(f"Ocurrió una excepción al crear el reporte: {e}")
            import traceback
            traceback.print_exc()
            

        
    def _execute_get_records_without_academic(self):
        records = self.select_pg(queries_pg.get_records_without_academic(),False)
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
    
      
    ########################################################
               
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

            report_process._build_file(name_file="Novedad_Fichas_Nuevas",format_report=self.FOTMAT_REPORT,report_contend=novedad_fichas_nuevas,headers=column_headers_oc,subfolder="Novedad Fichas Nuevas") 
            return "reporte generado"
         
    
    def _create_report_type_three(self): #Consulta_persona
        
        num_doc_input = input("Ingrese el documento de identidad sin puntos ni comas: ").strip()
        
        if not num_doc_input.isdigit():
            return "El documento ingresado no es válido. Debe contener solo números."
        
        num_doc_identidad = num_doc_input 
        
        report_process = ExcelProcess(self.oc_connection, self.pg_connection)
        
        novedad_persona = self._execute_query_persona(num_doc_identidad)
        if not novedad_persona:
            return "No se generó el reporte porque no hay datos de la persona"
        else:
            column_headers_oc = self.get_column_headers(queries_oc.get_persona(num_doc_identidad)[0], db_type="oc")
            report_process._build_file(name_file="Consulta_persona", format_report=self.FOTMAT_REPORT, report_contend=novedad_persona, headers=column_headers_oc,subfolder="Persona")
            return "Reporte de persona generado"
     
    #3144501,3142433,3141821
    def _create_report_type_four(self): #Información_básica_fichas
        report_process = ExcelProcess(self.oc_connection, self.pg_connection)
        ##########################

        archive_process = ArchiveProcess(self.oc_connection, self.pg_connection)
        fic_ids = archive_process._read_file(self.BASIC_RECORDS_INFORMATION_REPORT)
        
        if fic_ids is None:
             return "El archivo no existe. Verifique la ruta o cargue el archivo primero."
        
        fichas_existentes = self._verificar_fichas_oc(fic_ids)
        #print(f'fichas_existentes {fichas_existentes}')
        
        if fichas_existentes == False:
            return "No se encontraron fichas en la base de datos. Verifique los datos ingresados."

        fichas_existentes= [int(fic[0]) for fic in fichas_existentes]
        
        
        ################
       
        informacion_basica_fichas = self._execute_info_basic_data_records(fichas_existentes)
        #print(f'informacion_basica_fichas {informacion_basica_fichas}')

        if not informacion_basica_fichas:
            return "No se encontraron datos para generar el reporte."
        
        else:
            
            #column_headers_records = self.get_column_headers(queries_oc.get_info_basic_data_records(fichas_existentes)[0], db_type="oc")
            #column_headers_records.append("Notas") 
            column_headers_records=['FIC_ID', 'LMS_ID', 'PRF_TIPO_PROGRAMA', 'FIC_MOD_FORMACION', 'FIC_FCH_INICIALIZACION', 'FIC_FCH_FINALIZACION', 'FIC_ESTADO']
  
            fichas_dict = {row[0]: row for row in informacion_basica_fichas}
      
            fichas_completas = []
        
            for fic_id in fic_ids:
                try:
                    fic_id_int = int(fic_id)
                except ValueError:
                    print(f"Ficha inválida (no se puede convertir a entero): {fic_id}")
                    continue

                if fic_id_int in fichas_dict:
                    fichas_completas.append(fichas_dict[fic_id_int])
                else:
                    print(f"La ficha {fic_id_int} no se encontró información para la consulta ejecutada.")

            
                
            if column_headers_records:
                #mostrar sólo info existente column_headers_records sin el append,  informacion_basica_fichas
                report_process._build_file(
                    name_file="Información_básica_fichas", 
                    format_report=self.FOTMAT_REPORT, 
                    report_contend=informacion_basica_fichas, 
                    headers=column_headers_records,
                    subfolder="Informacion_basica_fichas"
                )
                
                return "Reporte de fichas generado con éxito."
            else:
                return "no se encotntraron encabezados"
        
      
          
        
 
    def _test_call_pg(self):
        report_process = ExcelProcess(self.oc_connection, self.pg_connection)
    

        archive_process = ArchiveProcess(self.oc_connection, self.pg_connection)
        fic_ids = archive_process._read_file(self.FICHAS_POSTGRES)
        
        if fic_ids is None:
            return "El archivo no existe. Verifique la ruta o cargue el archivo primero."
     
        if len(fic_ids) == 0:
            return "No se generó el reporte porque no se ingresaron fichas válidas. Verifique los datos ingresados."
   
   #################################################################
        fichas_existentes = self._verificar_fichas_pg(fic_ids)
        
        #print(f'=> {fichas_existentes}')
        if not fichas_existentes:
            return print("No se encontraron fichas en oracle")
    
        fichas_existentes= [int(fic[0]) for fic in fichas_existentes]
        
        if len(fichas_existentes) == 0:
            return "No se encontraron fichas en la base de datos. Verifique los datos ingresados."
    ########################################################################
        records_information = self._create_call_records_pg(fic_ids)
        
       # print(f'records_information {records_information}')
        
        if not records_information:
            return "No se encontraron datos de las fichas"
        
        else:
            query, params = queries_pg.get_record_pg(fic_ids)
            column_headers_records = self.get_column_headers(query, params=params, db_type="pg")
            column_headers_records.append("Notas") 
            if column_headers_records is None:
                return "No se pudieron obtener los encabezados de las columnas."
            fichas_dict = {row[0]: row for row in records_information}
            complete_records = []
            success = True
            
            for fic_id in fic_ids:
                try:
                    fic_id_int = int(fic_id)
                except ValueError:
                    print(f"Ficha inválida (no se puede convertir a entero): {fic_id}")
                    continue

                if fic_id_int in fichas_dict:
                    complete_records.append(fichas_dict[fic_id_int])
                else:
                    print(f"La ficha {fic_id_int} no se encontró información.")

            
            if success:
                report_process._build_file(
                    name_file="reporte de fichas postgres", 
                    format_report=self.FOTMAT_REPORT, 
                    report_contend=records_information, 
                    headers=column_headers_records,
                    subfolder="reporte fichas postgres"
                )
                return "Reporte de fichas generado con éxito."
           
   
    def _verificar_fichas_oc(self,fic_ids):
        query, params = queries_oc.verificar_fichas(fic_ids)
        records = self.select_oc(query, params, False)
        return records if records else False
    
    def _verificar_fichas_pg(self,fic_ids):
        query, params = queries_pg.verificar_fichas(fic_ids)
        records = self.select_pg(query, params, False)
        return records if records else False
    
    def _create_general_report(self):
        report_process = ExcelProcess(self.oc_connection, self.pg_connection)
        archive_process = ArchiveProcess(self.oc_connection, self.pg_connection)
        fic_ids = archive_process._read_file(self.GENERAL_REPORT_ARCHIVE)
        
        if fic_ids is None:
            return "El archivo no existe. Verifique la ruta o cargue el archivo primero."
      
        if len(fic_ids) == 0:
            return "No se generó el reporte porque no se ingresaron fichas válidas. Verifique los datos ingresados."
   
        fichas_existentes = self._verificar_fichas_oc(fic_ids)
       
        fichas_existentes = [int(fic[0]) for fic in fichas_existentes]
        
        if len(fichas_existentes) == 0:
            return "No se encontraron fichas en la base de datos. Verifique los datos ingresados."
        
        
        first_part, instrutor_production, apprentices_postgres, instructors_sofia = self._general_report_builder(fic_ids)

        reporte_dict = {}
        for i, fic_id in enumerate(fichas_existentes):  
            if fic_id not in fichas_existentes:
                continue  
            
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
                "Reporte de aprendices sofia": academic_record_sofia,
                "Notas": ""
            }

        if not reporte_dict:
            return "No se generó el reporte porque ninguna ficha era válida."

        # Obtener los encabezados del diccionario (clave del primer elemento)
        encabezados = list(reporte_dict[next(iter(reporte_dict))].keys())

        # Convertir diccionario en lista de listas para generar el reporte
        reporte_completo = [list(data.values()) for data in reporte_dict.values()]

        report_process._build_file(
            name_file="Seguimiento_fichas",
            format_report=self.FOTMAT_REPORT,
            report_contend=reporte_completo,
            headers=encabezados,
            subfolder="Seguimiento de Fichas Sofia-production"
        )

        return "Reporte general de fichas generado con éxito."

     
        
  
    def _create_report_records_state_thirteen(self):
        report_process = ExcelProcess(self.oc_connection, self.pg_connection)
       
       
        #se trae listado de fichas sin registros académicos en postgres
        result = self._execute_get_records_without_academic()

        # Construcción del diccionario de reporte
        reporte_dict = {}
        for ficha in result:
            fic_id, fecha_creacion, fic_estado, fecha_inicializacion, registros_academicos = ficha
            academic_record_sofia = self._apprentice_report_sofia(fic_id)
            
            reporte_dict[fic_id] = {
                "fic_id": fic_id,
                "fecha_creacion": fecha_creacion.strftime("%Y-%m-%d %H:%M:%S") if fecha_creacion else "N/A",
                "fic_estado": fic_estado,
                "fecha_inicializacion": fecha_inicializacion.strftime("%Y-%m-%d") if fecha_inicializacion else "N/A",
                "registros_academicos_production": registros_academicos,
                "registros_academicos_sofia":academic_record_sofia
            }

       
        encabezados = list(reporte_dict[next(iter(reporte_dict))].keys()) if reporte_dict else []

        
        reporte_completo = [list(data.values()) for data in reporte_dict.values()]
        
      
        report_process._build_file(
            name_file="Reporte_Fichas_Sin_Registros_academicos_production",
            format_report=self.FOTMAT_REPORT,
            report_contend=reporte_completo,
            headers=encabezados,
            subfolder="Fichas sin registros académicos"
        )

        return f"reporte 7 generado con éxito"

        
        
       
        
 


        
    
    
    
  
    


            

