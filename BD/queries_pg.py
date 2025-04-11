

def get_record_pg(fic_ids):
    placeholders = ",".join(["%s"] * len(fic_ids))  
    query = f'SELECT * FROM "INTEGRACION"."V_FICHA_CARACTERIZACION_B" vfcb WHERE "FIC_ID" IN ({placeholders})'
    return query, fic_ids


def general_report_first_part2(fic_ids):
    placeholders = ",".join(["%s"] * len(fic_ids))  
    query = f'select A."FIC_ID",B."PRF_DENOMINACION",A."LMS_ID",A."FIC_FCH_INICIALIZACION",A."FIC_FCH_FINALIZACION",B."PRF_CODIGO" from "INTEGRACION"."V_FICHA_CARACTERIZACION_B" A  inner join "INTEGRACION"."V_PROGRAMA_FORMACION_B" B ON A."PRF_ID" = B."PRF_ID" and "FIC_ID" IN({placeholders})'
    return query, fic_ids


def general_report_first_part(fic_ids):
    placeholders = ",".join(["%s"] * len(fic_ids))  
    query = f'''
        SELECT 
            A."FIC_ID",
            B."PRF_DENOMINACION",
            A."LMS_ID",
            TO_CHAR(A."FIC_FCH_INICIALIZACION", 'YYYY-MM-DD HH24:MI:SS'),
            TO_CHAR(A."FIC_FCH_FINALIZACION", 'YYYY-MM-DD HH24:MI:SS'),
            B."PRF_CODIGO" 
        FROM "INTEGRACION"."V_FICHA_CARACTERIZACION_B" A  
        INNER JOIN "INTEGRACION"."V_PROGRAMA_FORMACION_B" B 
            ON A."PRF_ID" = B."PRF_ID"
        WHERE "FIC_ID" IN ({placeholders})
    '''
    return query, fic_ids

    
def get_active_instructor(fic_ids):
    placeholders = ",".join(["%s"] * len(fic_ids))  # Cambia %s por ?
    query = f"""
        SELECT "FIC_ID", COUNT("NIS_FUN_INSTRUCTOR") AS "INSTRUCTORES_VIGENTES"
        FROM "INTEGRACION"."V_INSTRUCTORXFICHA_B" vib
        WHERE "INF_ESTADO" = 'V' AND "FIC_ID" IN ({placeholders})
        GROUP BY "FIC_ID"
    """
    return query, fic_ids  


def get_apprentices(fic_ids):
    placeholders = ",".join(["%s"] * len(fic_ids))  
    query = f'SELECT "FIC_ID", COUNT(*) AS total_registros_academicos FROM "INTEGRACION"."V_REGISTRO_ACADEMICO_B"WHERE "FIC_ID" IN ({placeholders}) GROUP BY "FIC_ID"'
    return query, fic_ids
    
def enrolamientos(fic_ids):
    placeholders = ",".join(["%s"] * len(fic_ids))  
    query = f'SELECT "FIC_ID", COUNT(*) AS "NUMERO_ENROLLAMIENTOS" FROM "INTEGRACION"."USUARIO_LMS_ENROLL_C" ulec WHERE "FIC_ID" IN ({placeholders}) GROUP BY "FIC_ID" ORDER BY "FIC_ID" '
    return query, fic_ids

def get_records_without_academic():
    return """SELECT A."FIC_ID", A.created_at, A."FIC_ESTADO", A."FIC_FCH_INICIALIZACION", COALESCE(COUNT(B."RGA_ID"), 0) AS REGISTROS_ACADEMICOS FROM "INTEGRACION"."V_FICHA_CARACTERIZACION_B" A LEFT JOIN "INTEGRACION"."V_REGISTRO_ACADEMICO_B" B ON A."FIC_ID" = B."FIC_ID" WHERE A."FIC_FCH_INICIALIZACION" >= '2025-01-01' AND A."FIC_FCH_INICIALIZACION" <= CURRENT_DATE AND A."FIC_ESTADO" <> 9 GROUP BY A."FIC_ID", A.created_at, A."FIC_ESTADO", A."FIC_FCH_INICIALIZACION" HAVING COUNT(B."RGA_ID") = 0"""


def verificar_fichas(fic_ids):
    placeholders = ", ".join(["%s"] * len(fic_ids))  # %s para cada parámetro
    query = f"""SELECT "FIC_ID" FROM "INTEGRACION"."V_FICHA_CARACTERIZACION_B" WHERE "FIC_ID" IN ({placeholders})"""
    params = tuple(fic_ids)  # en orden, como tupla
    return query, params
