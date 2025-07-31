import pandas as pd
from geopy.geocoders import Nominatim
from time import sleep
import os

import sys
import collections.abc

if sys.version_info.major == 3 and sys.version_info.minor >= 10:
    collections.Callable = collections.abc.Callable

print("--- INICIANDO O SCRIPT DE PRÉ-PROCESSAMENTO ---")
print("Este processo pode demorar. Por favor, aguarde...")

# Carrega os dados originais da pasta 'Mapas'
try:
    df_restaurantes = pd.read_csv('after/restaurante.csv', sep=';')
    df_bares = pd.read_csv('after/bar.csv', sep=";")
except FileNotFoundError:
    print("\nERRO: Verifique se os arquivos 'restaurante.csv' e 'bar.csv' estão na pasta 'Mapas'.")
    exit()


# Adiciona uma coluna para identificar a origem de cada dado
df_restaurantes['dataset_type'] = 'restaurante'
df_bares['dataset_type'] = 'bar'

# Combina os dois dataframes para geocodificar tudo de uma vez
df_total = pd.concat([df_restaurantes, df_bares], ignore_index=True)
df_total.dropna(subset=['LOCAL'], inplace=True)

# Inicializa o geolocator com um nome de user_agent único
geolocator = Nominatim(user_agent='after_app_preprocessing_v2', timeout=15)

# Listas para guardar as coordenadas
latitudes = []
longitudes = []

total_rows = len(df_total)
print(f"\nTotal de endereços para geocodificar: {total_rows}")

# Loop de geocodificação com feedback no terminal
for index, row in df_total.iterrows():
    endereco = row['LOCAL']
    # Imprime o progresso
    print(f"Processando {index + 1}/{total_rows}: {endereco}")
    try:
        location = geolocator.geocode(endereco)
        if location:
            latitudes.append(location.latitude)
            longitudes.append(location.longitude)
        else:
            latitudes.append(None)
            longitudes.append(None)
            print(f"  -> Endereço não encontrado.")
    except Exception as e:
        print(f"  -> ERRO ao geocodificar: {e}")
        latitudes.append(None)
        longitudes.append(None)
    
    # Pausa de 1 segundo para não sobrecarregar a API
    sleep(1)

df_total['LAT'] = latitudes
df_total['LON'] = longitudes

# Remove as linhas que não puderam ser geocodificadas
linhas_antes = len(df_total)
df_total.dropna(subset=['LAT', 'LON'], inplace=True)
linhas_depois = len(df_total)
print(f"\n--- Geocodificação Concluída ---")
print(f"{linhas_depois} de {linhas_antes} endereços foram mapeados com sucesso.")

# Cria a pasta 'DadosProcessados' se ela não existir
output_folder = 'DadosProcessados'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Salva o novo arquivo CSV com os dados processados
output_path = os.path.join(output_folder, 'estabelecimentos_geocoded.csv')
df_total.to_csv(output_path, sep=';', index=False)

print(f"\nArquivo final pré-processado foi salvo em: {output_path}")
print("--- SCRIPT FINALIZADO ---")