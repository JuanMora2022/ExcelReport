

def get_record_oc():
    return """
      select * from "INTEGRACION"."V_FICHA_CARACTERIZACION_B" vfcb 
      """
      
def get_novedad_fichas_nuevas():
  return """
  select "FIC_ID","FIC_FCH_INICIALIZACION","FIC_FCH_FINALIZACION","FIC_FCH_REGISTRO","FIC_MOD_FORMACION","FIC_ESTADO" from "INTEGRACION"."V_FICHA_CARACTERIZACION_B" vfcb where "FIC_FCH_REGISTRO" >= TIMESTAMP '2024-11-30 00:00:00' and "FIC_ESTADO" in(1,6,7) and "FIC_MOD_FORMACION" <> 'P'
  """