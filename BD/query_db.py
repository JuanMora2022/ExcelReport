def pg_get_fic_by_date():
    return""" 
        SELECT 
            A."FIC_ID",
            A.created_at,
            A."FIC_ESTADO",
            A."FIC_FCH_INICIALIZACION",
            COALESCE(COUNT(B."RGA_ID"), 0) AS REGISTROS_ACADEMICOS
        FROM 
            "INTEGRACION"."V_FICHA_CARACTERIZACION_B" A
        LEFT JOIN 
            "INTEGRACION"."V_REGISTRO_ACADEMICO_B" B
            ON A."FIC_ID" = B."FIC_ID"
        WHERE 
            A."FIC_FCH_INICIALIZACION" >= TIMESTAMP '2024-10-01 00:00:00'
            AND A."FIC_FCH_INICIALIZACION" <= TIMESTAMP '2024-10-31 00:00:00'
        GROUP BY 
            A."FIC_ID", A.created_at, A."FIC_ESTADO", A."FIC_FCH_INICIALIZACION"
        HAVING 
            COUNT(B."RGA_ID") = 0; 
    """

def oc_get_fic_replica():
    return"""
    SELECT 
        fic."FIC_ID", COUNT(fic."FIC_ID") as num_apren, 
        (
          select count(inf."NIS_FUN_INSTRUCTOR") as ins from "INTEGRACION"."V_INSTRUCTORXFICHA_B" inf where inf."FIC_ID" = fic."FIC_ID"
        ) as num_inst, 
        count(case when rga."RGA_ESTADO" = 13 then 1 end) as estado_13, 
        count(case when rga."RGA_ESTADO" = 7 then 1 end) as estado_7,
        count(case when rga."RGA_ESTADO" = 6 then 1 end) as estado_6, 
        count(case when rga."RGA_ESTADO" = 2 then 1 end) as estado_2, 
        count(case when rga."RGA_ESTADO" = 8 then 1 end) as estado_8, 
        fic."FIC_FCH_INICIALIZACION" as fch_inicio, 
        fic."FIC_ESTADO" 
    FROM "INTEGRACION"."V_REGISTRO_ACADEMICO_B" rga
    INNER JOIN "INTEGRACION"."V_FICHA_CARACTERIZACION_B" fic 
    ON rga."FIC_ID" = fic."FIC_ID" 
    WHERE fic."FIC_ID" in(:id) 
    GROUP BY fic."FIC_ID", fic."FIC_FCH_INICIALIZACION", fic."FIC_ESTADO
    """