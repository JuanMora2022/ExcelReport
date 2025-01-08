import argparse
import logging
import traceback
import os
import time
from datetime import datetime
from dotenv import load_dotenv
from bd.connection_db import ConnectionDB
from entity.report import ReportProcess
import sys

load_dotenv()

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--type_report",
        type=int,
        default=1,
        help="Define el tipo de Reporte a crear",
    )
    return parser.parse_args()

def main():
    start_time = time.time()
    start_time_readable = datetime.fromtimestamp(start_time).strftime("%Y-%m-%d")
    try:
        args = parse_arguments()
        connection_postgres = ConnectionDB(
                "postgres",
                os.getenv("HOST_PG"),
                os.getenv("SSID_PG"),
                os.getenv("USER_PG"),
                os.getenv("PASS_PG"),
                os.getenv("PORT_PG"),
            )
        connection_postgres.connect()
        connection_oracle = ConnectionDB(
            "oracle",
            os.getenv("HOST_ORCL"),
            os.getenv("SSID_ORCL"),
            os.getenv("USER_ORCL"),
            os.getenv("PASS_ORCL"),
            os.getenv("PORT_ORCL"),
        )            
        connection_oracle.connect()
        if args.type_report == 1 or args.type_report =='':
            print("Generar reporte 1")
            report_process = ReportProcess(connection_oracle, connection_postgres,args.type_report)
            report_process.execute()
      
            
        if args.type_report == 2:
            print("Generar reporte 2")
        
     
    except Exception as e:
        print(f"Error durante la ejecución: {e}")

if __name__=="__main__":
    main()