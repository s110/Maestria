import polars as pl
from sklearn.linear_model import LinearRegression
import datetime
from prophet import Prophet

#estoy mas acostumbrado a polars por que me permite trabajar con datasets mas grandes que memoria. usare este para el ejercicio

meses={"""Enero""":1,
"""Febrero""":2,
"""Marzo""":3,
"""Abril""":4,
"""Mayo""":5,
"""Junio""":6,
"""Julio""":7,
"""Agosto""":8,
"""Setiembre""":9,
"""Octubre""":10,
"""Noviembre""":11,
"""Diciembre""":12}

#funcion para pasar de meses escritos a meses numericos
def transformar_a_meses(value):
    return meses.get(value)

#se lee la hoja de excel, formateandola para tener columnas temporales

df=pl.read_excel(r"C:\Users\slopez\OneDrive - Celepsa\Desktop\Nestle\Preguntas Exámen BI 2025.xlsx",sheet_name="Pregunta 5")
df.columns=df.row(1)
df=df[2:].with_columns(pl.col('Ventas (miles S/.)').cast(float),pl.date(year=pl.col("Año"),month=pl.col('Mes').map_elements(transformar_a_meses,return_dtype=pl.Int8),day=1).alias("Fecha"))

#se transforma la fecha en valores de segundos en unix, ya que permite usar esos valores numericos para la regresion (X)
# array 2023 es un array de las fechas de 2023


fecha_np=df.select('Fecha').with_columns(pl.col('Fecha').dt.epoch('s')).to_numpy()
ventas_np=df.select('Ventas (miles S/.)').to_numpy()
array_2023=pl.date_range(start=datetime.date(2023,1,1),end=datetime.date(2023,12,1),interval="1mo",eager=True).dt.epoch('s').to_numpy().reshape(-1,1)

#se entrena el modelo linear de sklearn y se halla el R2

linear_model=LinearRegression()
linear_model.fit(X=fecha_np,y=ventas_np)
prediction=linear_model.predict(X=array_2023)
r2=linear_model.score(X=fecha_np,y=ventas_np)

df_predicciones = pl.DataFrame({
    "Fecha": array_2023,
    "Prediccion": prediction.flatten()
})
print('Score con modelo lineal:',r2)


#para mejores forecast usamos prophet que es bien usado para proyectar de manera rapida.

prophet_input=df.select(['Fecha','Ventas (miles S/.)']).rename({'Fecha':'ds','Ventas (miles S/.)':'y'})
prophet_input_pd=prophet_input.to_pandas()

prophet_model = Prophet()
prophet_model.fit(prophet_input_pd)
future = prophet_model.make_future_dataframe(periods=12,freq='MS')
prophet_forecast = prophet_model.predict(future)

fig1=prophet_model.plot(prophet_forecast)

#Los datos son altamente erraticos en el año, pero presentan cierta estacionalidad anual ya que repiten patrones.
