import bd.queries_pg
import bd.queries_oc as queries_oc
from bd.execution_query import ExecutionQuery
from bd.record_manager import RecordManager
import os
import csv


class ArchiveProcess(RecordManager):
    
  
    READING_FILE_DIRECTORY = "reading_files"#carpeta dónde se almacenan los archivos de lectura
    
    def __init__(self, oc_connection, pg_connection):
        super().__init__(oc_connection, pg_connection)
        self.pg_connection = pg_connection  
        self.oc_connection = oc_connection
        self.oc_query = ExecutionQuery(self.oc_connection, self.pg_connection)
        
        
    def _read_file(self,input_file):
        
        base_route = os.environ.get('PYTHONPATH', '.')  
        read_directory = os.path.join(base_route,self.READING_FILE_DIRECTORY)
        os.makedirs(read_directory, exist_ok=True) 
        #path_file_read =os.path.join(read_directory)
        
        path_file_read = os.path.join(read_directory, input_file)
        if not os.path.exists(path_file_read):
            with open(path_file_read, 'w') as file:
                file.write("") 
        
    def _read_file(self, input_file):
            base_route = os.environ.get('PYTHONPATH', '.')
            read_directory = os.path.join(base_route, self.READING_FILE_DIRECTORY)
            os.makedirs(read_directory, exist_ok=True)

            path_file_read = os.path.join(read_directory, input_file)
            
            if not os.path.isfile(path_file_read):
                print(f"Archivo no encontrado: {path_file_read}")
                return None

     

            # Si el archivo no existe, crearlo vacío
            ''' if not os.path.exists(path_file_read):
                with open(path_file_read, 'w', encoding="utf-8") as file:
                    file.write("")'''

            try:
                # Verificar si es TXT o CSV
                if input_file.endswith(".txt"):
                    with open(path_file_read, "r", encoding="utf-8") as archivo:
                        datos = [line.strip() for line in archivo if line.strip()]

                elif input_file.endswith(".csv"):
                    with open(path_file_read, "r", encoding="utf-8") as archivo:
                        lector_csv = csv.DictReader(archivo)  # Usamos DictReader para acceder por nombre de columna
                        if "FIC_ID" in lector_csv.fieldnames:  # Verificar que la columna exista
                            datos = [fila["FIC_ID"] for fila in lector_csv if fila["FIC_ID"].strip()]
                            
                            
                        else:
                            return "El archivo CSV no contiene la columna 'FIC_ID'."
                
                else:
                    return f"Formato no soportado: '{input_file}'. Usa archivos .txt o .csv"

                return datos

            except FileNotFoundError:
                return f"El archivo '{input_file}' no existe en {path_file_read}"
            except Exception as e:
                return f"Error al leer el archivo: {e}"