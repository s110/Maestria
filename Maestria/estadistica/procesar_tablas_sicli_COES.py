import polars as pl
import glob
import os
import datetime
from xlsxwriter import Workbook

tiempo_inicial = datetime.datetime.now()
tabla_1_2024 = pl.read_csv(
    r"C:\Users\slopez\OneDrive - Celepsa\Maestria Data Science\Estadistica y Probabilidad\proyecto_final\Tabla 1_SICLI_2024.txt",
    separator='	', infer_schema=False)
tabla_2_2024 = pl.read_csv(
    r"C:\Users\slopez\OneDrive - Celepsa\Maestria Data Science\Estadistica y Probabilidad\proyecto_final\Tabla 2_SICLI_2024.txt",
    separator='	', infer_schema=False)
tabla_3_2024 = pl.read_csv(
    r"C:\Users\slopez\OneDrive - Celepsa\Maestria Data Science\Estadistica y Probabilidad\proyecto_final\Tabla 3_SICLI_2024.txt",
    separator='	', infer_schema=False)
tabla_5_2024 = pl.read_csv(
    r"C:\Users\slopez\OneDrive - Celepsa\Maestria Data Science\Estadistica y Probabilidad\proyecto_final\Tabla 5_SICLI_2024.txt",
    separator='	', infer_schema=False)

print(tabla_3_2024.filter((pl.col('COD_USUARIO_LIBRE').is_in([
    '20511165181'
]
))&(pl.col('COD_PERIODO')=='202401')).with_columns(
    pl.col(['POTEN_CONTRATADA_HP',
            'POTEN_CONTRATADA_FP']).str.replace(',', '.', literal=True).cast(pl.Float64)).group_by(
    ['COD_USUARIO_LIBRE']).agg(pl.col(['POTEN_CONTRATADA_HP',
                                                                 'POTEN_CONTRATADA_FP']).sum()))
tipo_cambio = 3.75
porcentaje_extra_pc_nulls=1.3

tabla_5_2024 = tabla_5_2024.lazy().filter(pl.col('MES_FACTURADO') == pl.col('MES_FACTURADO').max()).with_columns(
    pl.col(['PREC_ENERG_BRG_HP',
            'PREC_ENERG_BRG_FP',
            'PREC_POTEN_BRG',
            'MAX_DEM_FP_PS', 'MAX_DEM_HP_PS']).str.replace(',', '.', literal=True).cast(pl.Float64)).with_columns(
    pl.max_horizontal('MAX_DEM_FP_PS', 'MAX_DEM_HP_PS').alias('POT_MAX'), (pl.col(['PREC_ENERG_BRG_HP',
                                                                                   'PREC_ENERG_BRG_FP']) * 10 / tipo_cambio).round(
        2), (pl.col('PREC_POTEN_BRG') / tipo_cambio)).select(
    ['COD_SUMINISTRO_USUARIO', 'PREC_ENERG_BRG_HP',
     'PREC_ENERG_BRG_FP',
     'PREC_POTEN_BRG',
     'POT_MAX']).group_by(
    ['COD_SUMINISTRO_USUARIO'
     ]).agg(pl.col(['PREC_ENERG_BRG_HP',
                    'PREC_ENERG_BRG_FP',
                    'PREC_POTEN_BRG',
                    'POT_MAX']).mean()).collect()

tabla_3_2024 = tabla_3_2024.filter(pl.col('COD_PERIODO') == pl.col('COD_PERIODO').max()).with_columns(
    pl.col(['POTEN_CONTRATADA_HP',
            'POTEN_CONTRATADA_FP']).str.replace(',', '.', literal=True).cast(pl.Float64)).group_by(
    ['COD_USUARIO_LIBRE', 'COD_SUMINISTRO_USUARIO']).agg(pl.col(['POTEN_CONTRATADA_HP',
                                                                 'POTEN_CONTRATADA_FP']).sum())

tabla_joined_sicli = tabla_5_2024.join(tabla_3_2024, how='inner', left_on='COD_SUMINISTRO_USUARIO',
                                       right_on='COD_SUMINISTRO_USUARIO', suffix='_tabla_3').with_columns(
    pl.when(~pl.col('POTEN_CONTRATADA_FP').is_null()).then(pl.col('POTEN_CONTRATADA_FP')).otherwise(
        pl.col('POT_MAX') * 1.2).alias('POTENCIA_CONTRATADA_FILLED')).group_by(['COD_USUARIO_LIBRE']).agg(
    pl.col(['POTENCIA_CONTRATADA_FILLED']).sum().alias('POTENCIA_CONTRATADA'),
    pl.col('PREC_ENERG_BRG_FP').mean().alias('PRECIO_ENERGIA')).filter(pl.col('POTENCIA_CONTRATADA') != 0).lazy()

precio_promedio_contratos = round(tabla_joined_sicli.collect().select('PRECIO_ENERGIA').mean().item(0, 0),2)
# se usara este precio en caso no haya un precio disponible
# para la potencia se usara la potencia promedio *1.2 en los rucs donde no hayan clientes

archivos_excel_cmg = glob.glob(os.path.join(r'C:\Users\slopez\OneDrive - Celepsa\Originacion\CMG', "**", "*.xlsx"),
                               recursive=True)
dataframes_cmg = []
for archivo in archivos_excel_cmg:
    dataframes_cmg.append(
        pl.read_excel(archivo).unpivot(index='S/./kWh', variable_name='BARRA', value_name='CMG_PEN_KWH').with_columns(
            pl.col('S/./kWh').str.to_datetime(format='%d/%m/%Y %H:%M:%S')).rename({'S/./kWh': 'FECHA'}))
cmg_concat = pl.concat(dataframes_cmg).lazy().sort(by=['FECHA', 'BARRA']).group_by_dynamic('FECHA', every='1mo',
                                                                                           closed='right',
                                                                                           group_by='BARRA').agg(
    (pl.col('CMG_PEN_KWH') * 1000 / tipo_cambio).mean().alias('CMG_USD_MWH')).select(
    ['FECHA', 'BARRA', 'CMG_USD_MWH'])

dataframes_coes = []
archivos_resumen_coes = glob.glob(
    os.path.join(r'C:\Users\slopez\OneDrive - Celepsa\Originacion\Transferencias_resumen', "**", "*.xlsx"),
    recursive=True)
for archivo in archivos_resumen_coes:
    archivo_date=archivo.split(sep='\\')[6]
    df_empresas_raw = pl.read_excel(source=archivo, sheet_name="REPORTE", has_header=False).drop_nulls(
        subset=['column_1'])
    df_empresas_raw.columns = df_empresas_raw.row(0)
    df_empresas_raw = df_empresas_raw[1:].lazy().filter(
        (pl.col('RUC CLIENTE').is_not_null()) & (pl.col('TIPO USUARIO') == 'LIBRE') & (
                    pl.col('TIPO DE CONTRATO') == 'BILATERAL') & (
            pl.col('RUC CLIENTE').is_in(['20269985900', '20331898008']).not_())).with_columns(pl.lit(archivo_date+'01').str.to_datetime(format='%Y%m%d').alias('PERIODO'))
    dataframes_coes.append(df_empresas_raw)

resumen_coes_concat = pl.concat(dataframes_coes).cast({'ENERGÍA (MW.h)':pl.Float64,'VALORIZACIÓN S/.':pl.Float64})

coes_cmg_resumen_join= resumen_coes_concat.filter(pl.col('PERIODO')>=datetime.datetime(year=2024, month=1,day=1)).join(cmg_concat, how='left',left_on=['PERIODO','BARRA DE TRANSFERENCIA'],right_on=['FECHA','BARRA']).with_columns(pl.col('CMG_USD_MWH').fill_null(strategy='mean'))
coes_sicli_joined= coes_cmg_resumen_join.join(tabla_joined_sicli, how='left',left_on='RUC CLIENTE',right_on='COD_USUARIO_LIBRE').with_columns(pl.col('PRECIO_ENERGIA').fill_null(strategy='mean'),pl.col('POTENCIA_CONTRATADA').fill_null(value=pl.col('ENERGÍA (MW.h)')*porcentaje_extra_pc_nulls/730.001)).filter(pl.col('CMG_USD_MWH')!=0)
coes_sicli_group_ruc_periodo= coes_sicli_joined.with_columns((pl.col('ENERGÍA (MW.h)')*(pl.col('PRECIO_ENERGIA')-pl.col('CMG_USD_MWH'))).round(2).alias('MARGEN_COMERCIAL')).group_by(['RUC CLIENTE','PERIODO']).agg(pl.col('CLIENTE / CENTRAL GENERACIÓN').last(),pl.col('MARGEN_COMERCIAL').sum(),pl.col('POTENCIA_CONTRATADA').sum(),pl.col('ENERGÍA (MW.h)').sum())
coes_sicli_group_ruc_final= coes_sicli_group_ruc_periodo.group_by(['RUC CLIENTE','CLIENTE / CENTRAL GENERACIÓN']).agg(pl.col(['MARGEN_COMERCIAL','ENERGÍA (MW.h)','POTENCIA_CONTRATADA']).mean().round(2)).sort(['MARGEN_COMERCIAL','ENERGÍA (MW.h)','POTENCIA_CONTRATADA'],descending=True).collect()
with Workbook(r'C:\Users\slopez\OneDrive - Celepsa\Maestria Data Science\Estadistica y Probabilidad\proyecto_final\info_clientes_libres_proyecto_v1.xlsx') as workbook:
    coes_sicli_group_ruc_final.write_excel(
                        workbook=workbook,
                        worksheet="INFO_CLIENTES",
                        table_style="Table Style Light 9",
                        table_name="info_clientes_libres",
                        autofit=True,
                        column_formats={'MARGEN_COMERCIAL':'0.00','ENERGÍA (MW.h)':'0.00','POTENCIA_CONTRATADA':'0.00'}
                    )

print('Terminado en:', datetime.datetime.now() - tiempo_inicial)
