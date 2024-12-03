import argparse
import logging
import traceback
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from BD.connection_db import ConnectionDB
# from bd.querys_db import QuerysDB
# from process.order_process import OrderProcess
# from process.excel_process import ExcelProcess
# from process.internal_process import InternalProcess
# import bd.queries as queries
import json


load_dotenv()

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--type",
        type=str,
        default=1,
        help="Define el tipo de Reporte a crear",
    )
    return parser.parse_args()

def main():
    start_time = time.time()
    start_time_readable = datetime.fromtimestamp(start_time).strftime("%Y-%m-%d")
    try:
        args = parse_arguments()
        if args.type == None or args.type == "":
            print(
                "Debe indicar el reporte a crear por defecto 1"
            )
        else:
            connection_postgres = ConnectionDB(
                "postgres",
                os.getenv("HOST_PG"),
                os.getenv("SSID_PG"),
                os.getenv("USER_PG"),
                os.getenv("PASS_PG"),
                os.getenv("PORT_PG"),
            )
            connection_postgres.connect()
            # connection_oracle = ConnectionDB(
            #     "oracle",
            #     os.getenv("HOST_ORCL"),
            #     os.getenv("SSID_ORCL"),
            #     os.getenv("USER_ORCL"),
            #     os.getenv("PASS_ORCL"),
            #     os.getenv("PORT_ORCL"),
            # )            
            # connection_oracle.connect()
    except Exception as e:
        print(f"Error durante la ejecución: {e}")

if __name__=="__main__":
    main()