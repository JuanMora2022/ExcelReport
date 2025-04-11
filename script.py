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

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

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
        clear_screen()
        print(" ")
        print("+++++++++ Tipos de reportes (type_report) ++++++++++++")
        print(" Consultas Oracle")
        print("1.Prueba Reporte")
        print("2.Reporte Novedad Fichas Nuevas ")
        print("3.Consulta a persona")
        print("4.Reporte Información Básica a fichas ")
        print("Consultas a postgres")
        print("5.Reporte Fichas postgres")
  
        #time.sleep(2)
        clear_screen()
        print("Reportes oficiales")
        print("2.Reporte Novedad Fichas Nuevas ")
        print("4.Reporte Información Básica a fichas ")
        print("8.emergencia enrolamientos ")
        clear_screen()

        
        
        if isinstance(args.type_report, int) or args.type_report =='':
            report_process = ReportProcess(connection_oracle, connection_postgres,args.type_report)
            report_process.execute()
      
       
            
     
    except Exception as e:
        print(f"Error durante la ejecución: {e}")

if __name__=="__main__":
    main()