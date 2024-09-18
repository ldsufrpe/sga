import pandas as pd
import unicodedata
import re


def normalizar(texto):
    if pd.isna(texto):
        return ''
    texto = re.sub(r'\s*/\s*', '/', texto)
    texto = texto.strip().upper()
    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join([c for c in texto if not unicodedata.combining(c)])
    return texto


def inspecionar_estratos_completo(arquivo_excel, issn):
    # Lê o arquivo Excel
    df = pd.read_excel(arquivo_excel, dtype=str)

    # Imprime as colunas para garantir que estão corretas
    print("Colunas do DataFrame:")
    print(df.columns.tolist())

    # Limpa e normaliza as colunas
    df['ISSN'] = df['ISSN'].apply(normalizar)
    df['Área de Avaliação'] = df['Área de Avaliação'].apply(normalizar)
    df['Estrato'] = df['Estrato'].apply(normalizar)

    # Filtra por ISSN
    df_issn = df[df['ISSN'] == issn]

    if df_issn.empty:
        print(f"Nenhuma entrada encontrada para ISSN {issn}.")
        return

    print(f"\nDados para ISSN {issn}:")
    print(df_issn[['Área de Avaliação', 'Estrato']])

    # Verifica estratos únicos
    estratos_unicos = df_issn['Estrato'].unique()
    print(f"\nEstratos únicos para ISSN {issn}: {estratos_unicos}")

    # Imprime cada área e estrato
    for index, row in df_issn.iterrows():
        print(f"Área: {row['Área de Avaliação']} - Estrato: {row['Estrato']}")


def criar_dicionario_qualis_completo(arquivo_excel):
    # Lê o arquivo Excel
    df = pd.read_excel(arquivo_excel, dtype=str)

    # Limpa e normaliza as colunas
    df['ISSN'] = df['ISSN'].apply(normalizar)
    df['Área de Avaliação'] = df['Área de Avaliação'].apply(normalizar)
    df['Estrato'] = df['Estrato'].apply(normalizar)

    # Cria o dicionário com depuração
    qualis_dict = {}

    for _, row in df.iterrows():
        issn = row['ISSN']
        area_avaliacao = row['Área de Avaliação']
        estrato = row['Estrato']

        # Ignora linhas com dados faltantes
        if not issn or not area_avaliacao or not estrato:
            continue

        if issn not in qualis_dict:
            qualis_dict[issn] = []

        tupla = (area_avaliacao, estrato)
        qualis_dict[issn].append(tupla)
        print(f"Adicionando para ISSN {issn}: {tupla}")

    return qualis_dict


# Exemplo de uso
arquivo_excel = 'qualis_capes.xlsx'
#issn = '1983-6430'

# Passo 1: Inspecionar os dados
#inspecionar_estratos_completo(arquivo_excel, issn)

# Passo 2: Criar o dicionário com depuração
qualis_dict = criar_dicionario_qualis_completo(arquivo_excel)

# Passo 3: Verificar o dicionário
# print("\nEstratos para ISSN 1983-6430:")
# print(qualis_dict.get(issn, []))
#print(qualis_dict)

import json
# Salva o dicionário em um arquivo JSON
with open('../../qualis_capes.json', 'w') as file:
    json.dump(qualis_dict, file)


# # Carrega o dicionário do arquivo JSON
# with open('qualis.json', 'r') as file:
#     qualis_dict = json.load(file)

# Exemplo de consulta
# issn = '1983-6430'
# area_avaliacao = 'ENGENHARIAS I'
# estrato = next((estrato for area, estrato in qualis_dict[issn] if area == area_avaliacao), None)
# print(f'Estrato: {estrato}')
