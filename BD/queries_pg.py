

def get_record_pg(fic_ids):
    placeholders = ",".join(["%s"] * len(fic_ids))  
    query = f'SELECT * FROM "INTEGRACION"."V_FICHA_CARACTERIZACION_B" vfcb WHERE "FIC_ID" IN ({placeholders})'
    return query, fic_ids
    

