# Carrega o dicionário do arquivo JSON
import json
import unicodedata
import re

with open('../../app/qualis/qualis_capes_17_20.json', 'r') as file:
    qualis_dict = json.load(file)


def normalizar_string(texto):
    # Remove espaços extras e normaliza os espaços ao redor de '/'
    texto = re.sub(r'\s*/\s*', '/', texto)  # Remove espaços ao redor de '/'
    texto = texto.strip().upper()  # Remove espaços nas extremidades e converte para maiúsculas

    # Normaliza a string para remover acentos e caracteres especiais
    texto = unicodedata.normalize('NFKD', texto)
    texto = ''.join([c for c in texto if not unicodedata.combining(c)])  # Remove acentos

    return texto
#Exemplo de consulta
issn = '1983-6422'
area_avaliacao = 'ASTRONOMIA/FÍSICA' #COM ACENTO
area_avaliacao = normalizar_string(area_avaliacao)

estrato = next((estrato for area, estrato in qualis_dict[issn] if area == area_avaliacao), None)
print(f'Estrato: {estrato}')
