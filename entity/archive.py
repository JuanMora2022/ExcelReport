import bd.queries_pg
import bd.queries_oc as queries_oc
from bd.execution_query import ExecutionQuery
from bd.record_manager import RecordManager
import os


class ArchiveProcess(RecordManager):
    
  
    READING_FILE_DIRECTORY = "reading_files"
    
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
        
        try:
            # Abrir y leer el archivo
            with open(path_file_read, "r", encoding="utf-8") as archivo:
                numeros = [line.strip() for line in archivo if line.strip()]
            return numeros
        except FileNotFoundError:
            return f"El archivo '{input_file}' no existe en {path_file_read}"
        except Exception as e:
            return f"Error al leer el archivo: {e}"
        
        