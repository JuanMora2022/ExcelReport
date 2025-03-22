import bd.queries_pg
import bd.queries_oc as queries_oc
from bd.execution_query import ExecutionQuery
from bd.record_manager import RecordManager
import logging
import traceback
from psycopg2 import sql
from datetime import date
from datetime import datetime
import pdb
import time
import os
import pandas as pd


class ExcelProcess(RecordManager):
    
    CONTAINER_FOLDER = "reports"
    
    def __init__(self, oc_connection, pg_connection):
        super().__init__(oc_connection, pg_connection)
        self.pg_connection = pg_connection  
        self.oc_connection = oc_connection
        self.oc_query = ExecutionQuery(self.oc_connection, self.pg_connection)
        
    def _get_current_datetime(self):  
        return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        #return int(datetime.now().timestamp())
        
        
    def _build_file(self, name_file, format_report,report_contend,headers,subfolder):
        try:
           
            for i in report_contend:
                list_values = i
                
            for header in headers:
                list_headers = header
            
            
            if isinstance(report_contend, tuple):
         
                data = [dict(zip(headers, report_contend))]
            elif isinstance(report_contend, list):
              
                data = [dict(zip(headers, row)) for row in report_contend]
           
    
         
            # Usar la instancia para llamar al método _get_current_datetime
            name_file_compound = f"{name_file}_{self._get_current_datetime()}"

            if format_report == "xlsx":
                file_path = self._save_report(name_file_compound, data, format_report,subfolder)
                
            elif format_report == "csv":
                file_path = self._save_report(name_file_compound, data, format_report,subfolder)
                
            return f"Archivo generado correctamente: {file_path}"
                
        except Exception as e:
            print("excepcion", e, traceback.format_exc())
        
    def _save_report(self, name_file_compound, data, format_report,subfolder):
        try:
            # Convertir los datos en un DataFrame
            df = pd.DataFrame(data)
            
            # Convertir todas las columnas datetime a naive (sin zona horaria)
            for col in df.select_dtypes(include=['datetime64[ns, UTC]', 'datetime64[ns]']):
                df[col] = df[col].dt.tz_localize(None)


            base_route = os.environ.get('PYTHONPATH', '.')

            # Construir la ruta para el archivo en la carpeta reports
            directorio = os.path.join(base_route, self.CONTAINER_FOLDER)
            os.makedirs(directorio, exist_ok=True)  # Crear la carpeta si no existe
            
            subdirectorio = os.path.join(directorio, subfolder)
            os.makedirs(subdirectorio, exist_ok=True)

            # Crear la ruta completa del archivo según el tipo de reporte
            if format_report.lower() == "xlsx":
                archivo = f"{name_file_compound}.xlsx"
                ruta_archivo = os.path.join(subdirectorio, archivo)
                df.to_excel(ruta_archivo, index=False)
            elif format_report.lower() == "csv":
                archivo = f"{name_file_compound}.csv"
                ruta_archivo = os.path.join(subdirectorio, archivo)
                df.to_csv(ruta_archivo, index=False)
            else:
                raise ValueError("Tipo de reporte no válido. Usa 'xlsx' o 'csv'.")

            print(f"Archivo {format_report.upper()} guardado en: {ruta_archivo}")
           
        except Exception as e:
            print(f"Error al guardar el reporte: {e}")
            raise



