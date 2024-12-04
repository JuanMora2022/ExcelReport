from exeption.timeout_exception import TimeoutException
import cx_Oracle
import psycopg2
from psycopg2 import sql
import pdb
import traceback
import concurrent.futures
import logging

class ExecutionQuery:
    def __init__(self, oc_connection, pg_connection):
        self.oc_connection = oc_connection
        self.pg_connection = pg_connection

    def select_oc(self, query, params={}, one=True):
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(self._execute_query_oc, query, params, one)
                logging.info(future)
                return future.result(timeout=self.TIME_OUT)
        except concurrent.futures.TimeoutError:
            # pdb.set_trace()
            logging.error(
                f"La consulta tomó más de {self.TIME_OUT/60} minutos y fue interrumpida."
            )
            raise TimeoutException(
                f"La consulta tomó más de {self.TIME_OUT/60} minutos y fue interrumpida."
            )
        except cx_Oracle.Error as e:
            (error,) = e.args
            table = self._table_name(query)
            logging.error(f"Error al consultar datos {table}: {e}")
            #insert_into_histories = InsertIntoHistories(self.pg_connection)
            # insert_into_histories.insert(
            #     (
            #         f"Error al ejecutar la consulta en {table} en SOFIA(Oracle): {error.message}",
            #         error.code,
            #         "error",
            #     )
            # )
            return None
    
    def select_pg(self, query, params=None, one=True):
        try:
            # params = list(params)
            cursor = self.pg_connection.connection.cursor()
            cursor.execute(query, params)
            datos = cursor.fetchone() if one else cursor.fetchall()
            cursor.close()
            return datos
        except psycopg2.Error as e:
            self.pg_connection.connection.rollback()
            table = self._table_name(query)
            # insert_into_histories = InsertIntoHistories(self.pg_connection)
            # insert_into_histories.insert((f'Error al ejecutar la consulta en la tabla {table} INTEGRACION(Postgres): {e.pgerror}',e.pgcode,'error'))
            print(f"Error al consultar datos {table}:", e)

    def _table_name(self, query):
        if isinstance(query, sql.Composed):
            query = query.as_string(self.pg_connection.connection)
        query = query.lower()
        words = query.split()
        search_word = self._operation_type(query)
        index_from = words.index(search_word)
        table = words[index_from + 1]
        table = table.rstrip(",;").upper()
        return table
    
    def _execute_query_oc(self, query, params, one):
        cursor = self.oc_connection.connection.cursor()
        cursor.execute(query, params)
        datos = cursor.fetchone() if one else cursor.fetchall()
        cursor.close()
        return datos
    
    def _operation_type(self, query):
        search_word = None
        if "insert into" in query:
            search_word = "into"
        elif "update" in query:
            search_word = "update"
        elif "select" in query:
            search_word = "from"
        return search_word