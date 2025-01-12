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
        
    def _get_current_datetime(self):  # Agregar self como argumento
        return datetime.now().strftime("%Y-%m-%d_%H-%M")
        
        
    def _build_file(self, name_file, format_report):
        try:
            data = {
                'Nombre': ['Ana', 'Juan', 'Luis'],
                'Edad': [25, 30, 22],
                'Ciudad': ['Madrid', 'Barcelona', 'Sevilla']
            }
          
            # Usar la instancia para llamar al método _get_current_datetime
            name_file_compound = f"{name_file}_{self._get_current_datetime()}"

            if format_report == "xlsx":
                file_path = self._save_report(name_file_compound, data, format_report)
                
            elif format_report == "csv":
                file_path = self._save_report(name_file_compound, data, format_report)
                
            return f"Archivo generado correctamente: {file_path}"
                
        except Exception as e:
            print("excepcion", e, traceback.format_exc())
        
    def _save_report(self, name_file_compound, data, format_report):
        try:
            # Convertir los datos en un DataFrame
            df = pd.DataFrame(data)

            base_route = os.environ.get('PYTHONPATH', '.')

            # Construir la ruta para el archivo en la carpeta reports
            directorio = os.path.join(base_route, self.CONTAINER_FOLDER)
            os.makedirs(directorio, exist_ok=True)  # Crear la carpeta si no existe

            # Crear la ruta completa del archivo según el tipo de reporte
            if format_report.lower() == "xlsx":
                archivo = f"{name_file_compound}.xlsx"
                ruta_archivo = os.path.join(directorio, archivo)
                df.to_excel(ruta_archivo, index=False)
            elif format_report.lower() == "csv":
                archivo = f"{name_file_compound}.csv"
                ruta_archivo = os.path.join(directorio, archivo)
                df.to_csv(ruta_archivo, index=False)
            else:
                raise ValueError("Tipo de reporte no válido. Usa 'xlsx' o 'csv'.")

            print(f"Archivo {format_report.upper()} guardado en: {ruta_archivo}")
           
        except Exception as e:
            print(f"Error al guardar el reporte: {e}")
            raise
