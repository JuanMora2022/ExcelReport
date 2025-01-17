

def get_record_oc():
    return """
      select * from "INTEGRACION"."V_FICHA_CARACTERIZACION_B" vfcb 
      """
      
def get_novedad_fichas_nuevas():
  return """
  select "FIC_ID","FIC_FCH_INICIALIZACION","FIC_FCH_FINALIZACION","FIC_FCH_REGISTRO","FIC_MOD_FORMACION","FIC_ESTADO" from "INTEGRACION"."V_FICHA_CARACTERIZACION_B" vfcb where "FIC_FCH_REGISTRO" >= TIMESTAMP '2024-11-30 00:00:00' and "FIC_ESTADO" in(1,6,7) and "FIC_MOD_FORMACION" <> 'P'
  """
  
def get_persona():
    return """ select * from INTEGRACION.V_PERSONA_B vpb where NUM_DOC_IDENTIDAD ='1004519830' """
  
def get_info_basic_data_records(fic_ids):
    placeholders = ", ".join([f":param{i}" for i in range(len(fic_ids))])  # Genera los placeholders con nombres
    query = f"""
        SELECT b."FIC_ID", b."LMS_ID", A."PRF_TIPO_PROGRAMA", b."FIC_MOD_FORMACION", "FIC_FCH_INICIALIZACION", 
               "FIC_FCH_FINALIZACION", "FIC_ESTADO" 
        FROM "INTEGRACION"."V_PROGRAMA_FORMACION_B" A 
        INNER JOIN "INTEGRACION"."V_FICHA_CARACTERIZACION_B" B 
        ON A."PRF_ID" = B."PRF_ID" 
        WHERE "FIC_ID" IN ({placeholders})
    """
    params = {f"param{i}": fic_id for i, fic_id in enumerate(fic_ids)}  # Asocia los parámetros con los valores
    return query, params

  
  
        
