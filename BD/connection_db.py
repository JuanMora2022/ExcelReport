import cx_Oracle
import psycopg2
import time
from dotenv import load_dotenv
import os
import logging
import traceback

load_dotenv()


class ConnectionDB:
    def __init__(self, db_type, host, database, user, password, port):
        self.db_type = db_type
        self.host = host
        self.database = database
        self.user = user
        self.password = password
        self.port = port
        self.connection = None

    def connect(self):
        attempts = 0
        max_attempts = 3
        while attempts < max_attempts:
            try:
                if self.db_type == "oracle":
                    dsn = cx_Oracle.makedsn(
                        self.host, self.port, service_name=self.database
                    )
                    self.connection = cx_Oracle.connect(self.user, self.password, dsn)
                elif self.db_type == "postgres":
                    self.connection = psycopg2.connect(
                        host=self.host,
                        database=self.database,
                        user=self.user,
                        password=self.password,
                        port=self.port,
                        options="-c client_encoding=latin1",
                    )
                else:
                    logging.warning("Tipo de base de datos no soportado")
                    return

                print(f"Conexión exitosa a la base de datos {self.db_type}")
                return
            except cx_Oracle.Error as e:
                (error,) = e.args
                message = f"Error al conectar con SOFIA(Oracle): {error.message}- {traceback.format_exc()}"
                code = f"código de error: {error.code}"
                logging.error(f"Error al conectar a Oracle: {error}")
               
            except psycopg2.Error as e:
                logging.error(f"Error al conectar a PostgreSQL: {e}")
               

            attempts += 1
            logging.warning(
                f"Reintentando conexión {self.host} ({attempts}/{max_attempts})..."
            )
            time.sleep(1)

        raise Exception(
            f"No se pudo establecer la conexión después de {max_attempts} intentos."
        )

    def disconnect(self):
        if self.connection:
            self.connection.close()
            print("Conexión cerrada")

    def is_connected(self):
        return self.connection is not None

    def _connect_to_postgres(self, user, password, host, port, database):
        attempts = 0
        max_attempts = 3
        while attempts < max_attempts:
            try:
                connection = psycopg2.connect(
                    user=user,
                    password=password,
                    host=host,
                    port=port,
                    database=database,
                )
                print("Conexión a PostgreSQL establecida")
                return connection
            except psycopg2.Error as e:
                logging.error(f"Error al conectar a PostgreSQL: {e}")
                attempts += 1
                logging.warning(f"Reintentando conexión ({attempts}/{max_attempts})...")
                time.sleep(1)

        raise Exception(
            f"No se pudo establecer la conexión a PostgreSQL después de {max_attempts} intentos."
        )

   