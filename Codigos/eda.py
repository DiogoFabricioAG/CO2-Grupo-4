import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Cargar el dataset
file_path = './Codigos/dataset_huancavelica.xlsx'
df = pd.read_excel(file_path)
# Si no les funciona: pip install openpyxl

# Mostrar las columnas del dataset
print("Columnas del dataset:")
print(df.columns)

# Mostrar los valores nulos de cada columna
print("\nValores nulos por columna:")
print(df.isnull().sum())

# Mostrar los tipos de datos de cada columna
print("\nTipos de datos por columna:")
print(df.dtypes)

# Mostrar estadísticas descriptivas para las variables numéricas
print("\nEstadísticas descriptivas para variables numéricas:")
print(df.describe())

# Contar los tipos de valores diferentes en una columna
def contar_valores_unicos(df, columna):
    print(f"\nValores únicos en la columna '{columna}':")
    print(df[columna].value_counts())

# Supongamos que tienes un DataFrame llamado 'df' y quieres analizar la columna 'NombreVariable'
contar_valores_unicos(df, 'departamento')
contar_valores_unicos(df, 'provincia')
contar_valores_unicos(df, 'distrito')

#CODIGO PARA GRAFICO DE BARRAS
def MakePlotBar(df, NombreVariable, titulo = "Poner un título", GuardarIMG=False):
  #Crear el gráfico y los ejes a manipular
  fig,ax = plt.subplots(figsize=(16,9))

  #Definir ejes
  x = df[NombreVariable].value_counts(ascending=True).index
  y = df[NombreVariable].value_counts(ascending=True)

  ax.barh(x,y,height=0.75,color="green")

  ax.set_title(titulo, fontsize=18, color="red",loc="right")

  ax.xaxis.set_tick_params(labelsize=8.5,labelcolor="black")
  ax.set_xticklabels(ax.get_xticks(),rotation=45,weight='bold',size=12)
  ax.yaxis.set_tick_params(labelsize=15,labelcolor="black")

  #Formato de miles a texto
  def MakeMiles(numero):
    if 1000<=numero<=9999:
      return str(numero)[0]+","+str(numero)[1:]
    elif 10000<=numero<=99999:
      return str(numero)[:2]+","+str(numero)[2:]
    else:
      return str(numero)

  #Asegurar que el texto no se superponga con el gráfico de barras
  for i,v in enumerate(y):
      ax.text(v+1,i,f'{MakeMiles(v)}',color="blue")

  plt.tight_layout()

  #dar amplitud al grafico
  niveles_var={}
  for nivel in df[NombreVariable].unique():
    niveles_var[nivel] = df[df[NombreVariable]==nivel].shape[0]

  #convertir el diccionario en serie
  niveles_var_df = pd.Series(niveles_var)

  #agregar el maximo nivel de barra a cada limite
  LimiteX = niveles_var_df.sort_values(ascending=False)[0]
  plt.xlim(0,1.1*LimiteX)

  #guardar imagen
  if GuardarIMG==True:
    tituloIMG=titulo+ ".jpeg"
    plt.savefig(tituloIMG,dpi=300)

  #graficar
  plt.show()

#Grafico de barras para la columna 'provincia'
MakePlotBar(df, 'provincia', titulo="Distribución de provincias", GuardarIMG=True)