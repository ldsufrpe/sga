import unicodedata
from datetime import datetime

from flask import Blueprint, request, flash, redirect
from flask_login import login_required
from flask_paginate import Pagination, get_page_parameter
from flask import render_template, url_for, jsonify
from flask import send_file
from app import db
from app.forms import ArtigoForm
import re
import backoff
from app.models import Artigo, Area, Subarea  # Certifique-se de que Area e Subarea estão sendo importados aqui
import requests

import os
import io
import csv
import json
import openpyxl  # Para exportar XLSX

# Criar o blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/painel')
@login_required
def painel():
    return render_template('painel.html')

@main_bp.route('/cadastro', methods=['GET', 'POST'])
@login_required
def submit_artigo():
    form = ArtigoForm()

    # Carregar opções de área e subárea
    form.area_id.choices = [('', 'SELECIONE UMA ÁREA')] + [(area.id, area.nome) for area in Area.query.all()]
    form.subarea_id.choices = [('', 'SELECIONE UMA SUBÁREA')] + [(subarea.id, subarea.nome) for subarea in Subarea.query.all()]

    if form.validate_on_submit():
        # Salvar o artigo no banco de dados
        artigo = Artigo(
            doi=form.doi.data,
            titulo=form.titulo.data,
            ano=form.ano.data,
            revista=form.revista.data,
            issn=form.issn.data,
            area_id=form.area_id.data,
            subarea_id=form.subarea_id.data,
            autores=form.autores.data,
            internacionalizacao=form.internacionalizacao.data,
            classificacao=form.classificacao.data,
            fator_impacto=form.fator_impacto.data
        )
        db.session.add(artigo)
        db.session.commit()

        # Obter os nomes das áreas e subáreas para o JSON de resposta
        area_nome = Area.query.get(artigo.area_id).nome
        subarea_nome = Subarea.query.get(artigo.subarea_id).nome

        response = {
            "status": "success",
            "message": "Artigo cadastrado com sucesso!",
            "artigo": {
                "id": artigo.id,
                "doi": artigo.doi,
                "titulo": artigo.titulo,
                "ano": artigo.ano,
                "revista": artigo.revista,
                "issn": artigo.issn,
                "area": area_nome,  # Nome da área
                "subarea": subarea_nome,  # Nome da subárea
                "autores": artigo.autores,
                "internacionalizacao": artigo.internacionalizacao,
                "classificacao": artigo.classificacao,
                "fator_impacto": artigo.fator_impacto
            }
        }
        return jsonify(response), 201, {'Content-Type': 'application/json; charset=utf-8'}

    # Tratamento para GET ou erro de validação
    if request.method == 'GET' or form.errors:
        if request.is_xhr or request.content_type == 'application/json':
            # Retornar os erros como JSON se a requisição for via fetch
            errors = {field: error[0] for field, error in form.errors.items()}
            return jsonify({"status": "error", "errors": errors}), 400
        else:
            # Renderizar o template HTML para requisições normais
            return render_template('form.html', form=form, success_message=None)



@main_bp.route('/api/submissoes', methods=['GET'])
def ver_submissoes():
    artigos = Artigo.query.all()

    # Adicionar os nomes das áreas e subáreas aos artigos
    response = [{
        "id": artigo.id,
        "doi": artigo.doi,
        "titulo": artigo.titulo,
        "ano": artigo.ano,
        "revista": artigo.revista,
        "issn": artigo.issn,
        "area": Area.query.get(artigo.area_id).nome if artigo.area_id else 'Área não encontrada',
        "subarea": Subarea.query.get(artigo.subarea_id).nome if artigo.subarea_id else 'Subárea não encontrada',
        "autores": artigo.autores,
        "internacionalizacao": artigo.internacionalizacao,
        "classificacao": artigo.classificacao,
        "fator_impacto": artigo.fator_impacto
    } for artigo in artigos]

    # Se precisar retornar como JSON para API
    if request.args.get('format') == 'json':
        return jsonify(response)

    # Se quiser renderizar em HTML
    return render_template('submissoes.html', artigos=response)


@main_bp.route('/fetch_metadata', methods=['POST'])
@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=3)
def fetch_metadata():
    doi = request.json.get('doi')
    if doi:
        # Remover prefixos indesejados como https://doi.org/
        doi = re.sub(r'^https?://doi.org/', '', doi)

        # Agora faça a requisição à API CrossRef usando o DOI limpo
        response = requests.get(f'https://api.crossref.org/works/{doi}')
        if response.status_code == 200:
            data = response.json()['message']

            # Use um fallback seguro para lidar com listas vazias
            titulo = data.get('title', [''])[0] if data.get('title', []) else ''
            ano = (data.get('published-print', {}).get('date-parts', [[None]])[0][0] or
                   data.get('published-online', {}).get('date-parts', [[None]])[0][0] or '')
            revista = data.get('container-title', [''])[0] if data.get('container-title', []) else ''
            issn = data.get('ISSN', [''])[0] if data.get('ISSN', []) else ''
            autores = ', '.join(
                [f"{author.get('given', '')} {author.get('family', '')}" for author in data.get('author', [])]
            )

            return {
                'titulo': titulo,
                'ano': ano,
                'revista': revista,
                'issn': issn,
                'autores': autores
            }, 200
        else:
            return {'error': 'DOI não encontrado'}, 404
    return {'error': 'DOI inválido'}, 400


@main_bp.route('/check_doi', methods=['POST'])
def check_doi():
    data = request.get_json()
    doi = data.get('doi', '').strip()

    # Limpeza do DOI removendo a URL base, se existir
    doi = re.sub(r'^https?://doi.org/', '', doi)

    # Verificar se o DOI já existe no banco de dados
    artigo = Artigo.query.filter_by(doi=doi).first()

    if artigo:
        return jsonify({'exists': True, 'message': 'O DOI informado já existe no banco de dados.'}), 200
    else:
        return jsonify({'exists': False, 'message': 'O DOI está disponível.'}), 200

# atualizar campo classificacao

# Definir o caminho absoluto para o arquivo qualis_capes_17_20.json
# Determina o diretório base do projeto
current_dir = os.path.abspath(os.path.dirname(__file__))
base_dir = os.path.abspath(os.path.join(current_dir, os.pardir))

# Caminho absoluto para qualis_capes_17_20.json
json_file_path = os.path.join(base_dir, 'qualis/qualis_capes_17_20.json')
cache = {}
@main_bp.route('/get_classificacao', methods=['POST'])
def get_classificacao():
    data = request.get_json()
    issn = data.get('issn', '').strip()
    area_avaliacao = data.get('area_avaliacao', '').strip()

    # Normalizar a string da área de avaliação
    def normalizar_string(texto):
        texto = re.sub(r'\s*/\s*', '/', texto)
        texto = texto.strip().upper()
        texto = unicodedata.normalize('NFKD', texto)
        texto = ''.join([c for c in texto if not unicodedata.combining(c)])
        return texto

    area_avaliacao = normalizar_string(area_avaliacao)

    # Verifique no cache primeiro
    cache_key = f"{issn}_{area_avaliacao}"
    if cache_key in cache:
        return jsonify({'classificacao': cache[cache_key]}), 200

    try:
        print(json_file_path)
        with open(json_file_path, 'r') as file:
            qualis_dict = json.load(file)

        estrato = next((estrato for area, estrato in qualis_dict.get(issn, []) if area == area_avaliacao), None)
        if estrato:
            cache[cache_key] = estrato
            return jsonify({'classificacao': estrato}), 200
        else:
            # Alteração: Quando a classificação não é encontrada, retorna 0
            cache[cache_key] = '0'
            return jsonify({'classificacao': '0'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

#################### Rotas de CRUD ###################

@main_bp.route('/artigos', methods=['GET'])
@login_required
def listar_artigos():
    # Capturar os parâmetros de pesquisa e ordenação
    titulo = request.args.get('titulo', '').strip()
    revista = request.args.get('revista', '').strip()
    ano = request.args.get('ano', '').strip()
    classificacao = request.args.get('classificacao', '').strip()
    area_id = request.args.get('area_id', '').strip()
    subarea_id = request.args.get('subarea_id', '').strip()
    sort_by = request.args.get('sort_by', 'id')  # Coluna padrão para ordenação
    sort_dir = request.args.get('sort_dir', 'desc')  # Direção padrão para ordenação

    # Construir a consulta com base nos parâmetros
    query = Artigo.query

    if titulo:
        query = query.filter(Artigo.titulo.ilike(f'%{titulo}%'))
    if revista:
        query = query.filter(Artigo.revista.ilike(f'%{revista}%'))
    if ano:
        query = query.filter_by(ano=ano)
    if classificacao:
        query = query.filter(Artigo.classificacao.ilike(f'%{classificacao}%'))
    if area_id:
        query = query.filter_by(area_id=area_id)
    if subarea_id:
        query = query.filter_by(subarea_id=subarea_id)

    # Aplicar ordenação
    if sort_dir == 'desc':
        query = query.order_by(getattr(Artigo, sort_by).desc())
    else:
        query = query.order_by(getattr(Artigo, sort_by).asc())

    # Paginação
    page = request.args.get(get_page_parameter(), type=int, default=1)
    per_page = request.args.get('per_page', type=int, default=10)
    artigos = query.paginate(page=page, per_page=per_page)

    areas = Area.query.all()
    subareas = Subarea.query.all()

    return render_template('listar_artigos.html', artigos=artigos, areas=areas, subareas=subareas, sort_by=sort_by, sort_dir=sort_dir)

@main_bp.route('/visualizar_artigo/<int:id>')
@login_required
def visualizar_artigo(id):
    # Busca o artigo
    artigo = Artigo.query.get_or_404(id)

    # Busca os nomes da área e subárea usando os IDs armazenados no artigo
    area = Area.query.get(artigo.area_id)
    subarea = Subarea.query.get(artigo.subarea_id)

    # Passa os nomes de área e subárea para o template
    area_nome = area.nome if area else "Não especificada"
    subarea_nome = subarea.nome if subarea else "Não especificada"

    return render_template('visualizar_artigo.html', artigo=artigo, area_nome=area_nome, subarea_nome=subarea_nome)




@main_bp.route('/artigos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_artigo(id):
    artigo = Artigo.query.get_or_404(id)
    form = ArtigoForm(obj=artigo)
    form.article_id.data = artigo.id  # Preenche o campo oculto com o ID do artigo

    # Atualizar as opções de área e subárea, se necessário
    form.area_id.choices = [(area.id, area.nome) for area in Area.query.all()]
    form.subarea_id.choices = [(subarea.id, subarea.nome) for subarea in Subarea.query.all()]

    if form.validate_on_submit():
        form.populate_obj(artigo)
        db.session.commit()
        flash('Artigo atualizado com sucesso!', 'success')
        return redirect(url_for('main.listar_artigos'))
    return render_template('editar_artigo.html', form=form, artigo=artigo)




@main_bp.route('/artigos/deletar/<int:id>', methods=['POST'])
@login_required
def deletar_artigo(id):
    artigo = Artigo.query.get_or_404(id)
    db.session.delete(artigo)
    db.session.commit()
    flash('Artigo deletado com sucesso!', 'success')
    return redirect(url_for('main.listar_artigos'))



######################### Exportar CSV ######################


@main_bp.route('/exportar_artigos', methods=['GET'])
@login_required
def exportar_artigos():
    # Capturar os parâmetros de pesquisa e ordenação (mesma lógica da rota listar_artigos)
    titulo = request.args.get('titulo', '').strip()
    revista = request.args.get('revista', '').strip()
    ano = request.args.get('ano', '').strip()
    classificacao = request.args.get('classificacao', '').strip()
    area_id = request.args.get('area_id', '').strip()
    subarea_id = request.args.get('subarea_id', '').strip()
    sort_by = request.args.get('sort_by', 'id')
    sort_dir = request.args.get('sort_dir', 'asc')
    export_format = request.args.get('format', 'csv')  # Formato padrão é CSV

    # Construir a consulta com base nos parâmetros
    query = Artigo.query

    if titulo:
        query = query.filter(Artigo.titulo.ilike(f'%{titulo}%'))
    if revista:
        query = query.filter(Artigo.revista.ilike(f'%{revista}%'))
    if ano:
        query = query.filter_by(ano=ano)
    if classificacao:
        query = query.filter(Artigo.classificacao.ilike(f'%{classificacao}%'))
    if area_id:
        query = query.filter_by(area_id=area_id)
    if subarea_id:
        query = query.filter_by(subarea_id=subarea_id)

    # Aplicar ordenação
    if sort_dir == 'desc':
        query = query.order_by(getattr(Artigo, sort_by).desc())
    else:
        query = query.order_by(getattr(Artigo, sort_by).asc())

    artigos = query.all()

    # Exportar para CSV
    if export_format == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'DOI', 'Título', 'Ano', 'Revista', 'ISSN', 'Classificação', 'Área de Avaliação', 'Área Específica', 'Autores', 'Internacionalização', 'Fator de Impacto'])
        for artigo in artigos:
            writer.writerow([
                artigo.id,
                artigo.doi,
                artigo.titulo,
                artigo.ano,
                artigo.revista,
                artigo.issn,
                artigo.classificacao,
                Area.query.get(artigo.area_id).nome,
                Subarea.query.get(artigo.subarea_id).nome,
                artigo.autores,
                'Sim' if artigo.internacionalizacao else 'Não',
                str(artigo.fator_impacto) if artigo.fator_impacto is not None else ''  # Verifica se é None e converte para string
            ])
        output.seek(0)
        return send_file(io.BytesIO(output.getvalue().encode()), mimetype='text/csv', as_attachment=True, download_name='artigos.csv')

    # Exportar para XLSX
    elif export_format == 'xlsx':
        output = io.BytesIO()
        workbook = openpyxl.Workbook()
        sheet = workbook.active
        sheet.append(['ID', 'DOI', 'Título', 'Ano', 'Revista', 'ISSN', 'Classificação', 'Área de Avaliação', 'Área Específica', 'Autores', 'Internacionalização', 'Fator de Impacto'])
        for artigo in artigos:
            sheet.append([
                artigo.id,
                artigo.doi,
                artigo.titulo,
                artigo.ano,
                artigo.revista,
                artigo.issn,
                artigo.classificacao,
                Area.query.get(artigo.area_id).nome,
                Subarea.query.get(artigo.subarea_id).nome,
                artigo.autores,
                'Sim' if artigo.internacionalizacao else 'Não',
                float(artigo.fator_impacto) if artigo.fator_impacto is not None else 0.0  # Converte para float ou define como 0.0
            ])
        workbook.save(output)
        output.seek(0)
        return send_file(output, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', as_attachment=True, download_name='artigos.xlsx')

    # Exportar para JSON
    elif export_format == 'json':
        data = []
        for artigo in artigos:
            data.append({
                'ID': artigo.id,
                'DOI': artigo.doi,
                'Título': artigo.titulo,
                'Ano': artigo.ano,
                'Revista': artigo.revista,
                'ISSN': artigo.issn,
                'Classificação': artigo.classificacao,
                'Área de Avaliação': Area.query.get(artigo.area_id).nome,
                'Área Específica': Subarea.query.get(artigo.subarea_id).nome,
                'Autores': artigo.autores,
                'Internacionalização': 'Sim' if artigo.internacionalizacao else 'Não',
                'Fator de Impacto': float(artigo.fator_impacto) if artigo.fator_impacto is not None else 0.0  # Converte para float ou define como 0.0
            })
        return send_file(io.BytesIO(json.dumps(data, ensure_ascii=False, indent=4).encode()), mimetype='application/json', as_attachment=True, download_name='artigos.json')

    # Caso o formato não seja suportado
    else:
        flash('Formato de exportação não suportado!', 'error')
        return redirect(url_for('main.listar_artigos'))

############################# Dashboard ###########################

@main_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    # Consultar áreas de avaliação
    areas = Area.query.all()

    # Consultar áreas específicas com artigos associados
    subareas = Subarea.query.join(Artigo, Subarea.id == Artigo.subarea_id).group_by(Subarea.id).all()

    # Consultar anos com artigos associados
    anos = db.session.query(Artigo.ano).distinct().order_by(Artigo.ano).all()

    # Renderizar o template e passar os dados necessários
    return render_template('dashboard.html', areas=areas, subareas=subareas, anos=[ano[0] for ano in anos])


@main_bp.route('/api/dashboard_data', methods=['GET'])
def dashboard_data():
    area_id = request.args.get('area_id', type=int)
    subarea_id = request.args.get('subarea_id', type=int)
    ano_inicio = request.args.get('ano_inicio', type=int)
    ano_fim = request.args.get('ano_fim', type=int)

    query = Artigo.query

    # Aplicar os filtros, se fornecidos
    if area_id:
        query = query.filter_by(area_id=area_id)
    if subarea_id:
        query = query.filter_by(subarea_id=subarea_id)
    if ano_inicio and ano_fim:
        query = query.filter(Artigo.ano >= ano_inicio, Artigo.ano <= ano_fim)

    # Consulta filtrada
    artigos_filtrados = query.all()

    # Cálculo das métricas filtradas
    total_artigos_filtrados = len(artigos_filtrados)
    soma_fator_impacto_filtrado = sum(float(artigo.fator_impacto) for artigo in artigos_filtrados if artigo.fator_impacto)
    media_fator_impacto_filtrada = soma_fator_impacto_filtrado / total_artigos_filtrados if total_artigos_filtrados > 0 else 0.0

    # Cálculo das métricas gerais
    todos_artigos = Artigo.query.all()  # consulta sem filtros
    total_artigos = len(todos_artigos)
    soma_fator_impacto = sum(float(artigo.fator_impacto) for artigo in todos_artigos if artigo.fator_impacto)
    media_fator_impacto = soma_fator_impacto / total_artigos if total_artigos > 0 else 0.0
    ano_atual = datetime.now().year
    artigos_ano_atual = len([artigo for artigo in todos_artigos if artigo.ano == ano_atual])

    dados_graficos = {
        'chart1': {'labels': [], 'datasets': [{'label': 'Número de Artigos', 'data': [], 'backgroundColor': '#36A2EB'}]},
        'chart2': {'labels': [], 'datasets': [{'label': 'Classificação Qualis', 'data': [], 'backgroundColor': '#FF6384'}]},
        'chart3': {'labels': [], 'datasets': [{'label': 'Número de Artigos por Revista', 'data': [], 'backgroundColor': '#FFCE56'}]},
        'chart4': {'labels': [], 'datasets': [{'label': 'Artigos por Área Específica', 'data': [], 'backgroundColor': '#4BC0C0'}]},
        'chart5': {'labels': [], 'datasets': [{'label': 'Fator de Impacto Médio por Ano', 'data': [], 'backgroundColor': '#9966FF'}]},
        'chart6': {'labels': ['Sim', 'Não'], 'datasets': [{'label': 'Artigos Internacionalizados', 'data': [0, 0], 'backgroundColor': ['#FF9F40', '#FFCD56']}]},
        'chart7': {'labels': [], 'datasets': [{'label': 'Classificação Qualis', 'data': [], 'backgroundColor': ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0']}]},
        'chart8': {'labels': [], 'datasets': [{'label': 'Número de Artigos por Área de Avaliação Qualis', 'data': [], 'backgroundColor': '#8e44ad'}]},
        'metrics': {
            'total_artigos': total_artigos,
            'media_fator_impacto': round(media_fator_impacto, 2),
            'artigos_ano_atual': artigos_ano_atual,
            'total_artigos_filtrados': total_artigos_filtrados,
            'media_fator_impacto_filtrada': round(media_fator_impacto_filtrada, 2)
        }
    }

    anos = {}
    classificacoes = {}
    revistas = {}
    subareas = {}
    fator_impacto_por_ano = {}
    internacionalizados = [0, 0]
    areas_qualis = {}  # Variável para armazenar o número de artigos por área de avaliação Qualis

    for artigo in artigos_filtrados:
        # Chart 1 - Número de Artigos por Ano
        if artigo.ano not in anos:
            anos[artigo.ano] = 0
        anos[artigo.ano] += 1

        # Chart 2 - Classificação Qualis
        classificacao = artigo.classificacao if artigo.classificacao else "Não Classificado"
        if classificacao not in classificacoes:
            classificacoes[classificacao] = 0
        classificacoes[classificacao] += 1

        # Chart 3 - Número de Artigos por Revista
        if artigo.revista not in revistas:
            revistas[artigo.revista] = 0
        revistas[artigo.revista] += 1

        # Chart 4 - Artigos por Área Específica
        subarea_nome = Subarea.query.get(artigo.subarea_id).nome if artigo.subarea_id else 'Subárea não encontrada'
        if subarea_nome not in subareas:
            subareas[subarea_nome] = 0
        subareas[subarea_nome] += 1

        # Chart 5 - Fator de Impacto Médio por Ano
        if artigo.ano not in fator_impacto_por_ano:
            fator_impacto_por_ano[artigo.ano] = []
        fator_impacto_por_ano[artigo.ano].append(float(artigo.fator_impacto) if artigo.fator_impacto else 0)

        # Chart 6 - Artigos Internacionalizados
        if artigo.internacionalizacao:
            internacionalizados[0] += 1  # 'Sim'
        else:
            internacionalizados[1] += 1  # 'Não'

        # Chart 7 - Classificação Qualis (Gráfico de Pizza)
        if classificacao not in classificacoes:
            classificacoes[classificacao] = 0
        classificacoes[classificacao] += 1

        # Chart 8 - Número de Artigos por Área de Avaliação Qualis
        area_nome = Area.query.get(artigo.area_id).nome if artigo.area_id else 'Área não encontrada'
        if area_nome not in areas_qualis:
            areas_qualis[area_nome] = 0
        areas_qualis[area_nome] += 1

    # Populando os dados nos gráficos
    sorted_anos = sorted(anos.items())
    for ano, count in sorted_anos:
        dados_graficos['chart1']['labels'].append(ano)
        dados_graficos['chart1']['datasets'][0]['data'].append(count)

    for classificacao, count in classificacoes.items():
        dados_graficos['chart2']['labels'].append(classificacao)
        dados_graficos['chart2']['datasets'][0]['data'].append(count)

    for revista, count in revistas.items():
        dados_graficos['chart3']['labels'].append(revista)
        dados_graficos['chart3']['datasets'][0]['data'].append(count)

    for subarea_nome, count in subareas.items():
        dados_graficos['chart4']['labels'].append(subarea_nome)
        dados_graficos['chart4']['datasets'][0]['data'].append(count)

    sorted_fator_impacto_por_ano = sorted(fator_impacto_por_ano.items())  # Ordenar os anos
    for ano, fatores in sorted_fator_impacto_por_ano:
        media_fator = sum(fatores) / len(fatores) if fatores else 0
        dados_graficos['chart5']['labels'].append(ano)
        dados_graficos['chart5']['datasets'][0]['data'].append(media_fator)

    dados_graficos['chart6']['datasets'][0]['data'] = internacionalizados

    # Populando os dados do gráfico 7 (Classificação Qualis)
    for classificacao, count in classificacoes.items():
        dados_graficos['chart7']['labels'].append(classificacao)
        dados_graficos['chart7']['datasets'][0]['data'].append(count)

    # Populando os dados do gráfico 8
    for area_nome, count in areas_qualis.items():
        dados_graficos['chart8']['labels'].append(area_nome)
        dados_graficos['chart8']['datasets'][0]['data'].append(count)

    return jsonify(dados_graficos)


# def image_to_base64(image_path):
#     with open(image_path, "rb") as image_file:
#         return base64.b64encode(image_file.read()).decode('utf-8')

# @main_bp.route('/save-chart', methods=['POST'])
# def save_chart():
#     data = request.get_json()
#     chart_id = data['chartId']
#     image_data = data['imageData'].split(',')[1]  # Remove o prefixo base64
#
#     # Verificar o conteúdo base64
#     # print(f"Recebendo imagem do gráfico: {chart_id}")
#     # print(f"Primeiros 50 caracteres da imagem base64: {image_data[:50]}")
#
#     # Decodificar a imagem base64
#     try:
#         image_bytes = base64.b64decode(image_data)
#     except Exception as e:
#         print(f"Erro na decodificação da imagem: {e}")
#         return jsonify({"error": f"Falha na decodificação da imagem: {e}"}), 500
#
#     # Definir o caminho do diretório 'static/img'
#     img_dir = os.path.join('static', 'img')
#
#     # Criar o diretório 'static/img' se ele não existir
#     if not os.path.exists(img_dir):
#         os.makedirs(img_dir)
#         print(f"Diretório 'static/img' criado.")
#
#     # Tentar salvar a imagem no servidor
#     file_path = os.path.join(img_dir, f'{chart_id}.png')
#     # print(f"Tentando salvar a imagem em: {file_path}")
#
#     try:
#         with open(file_path, 'wb') as f:
#             f.write(image_bytes)
#         print(f"Imagem salva com sucesso: {file_path}")
#     except Exception as e:
#         print(f"Erro ao salvar a imagem: {e}")
#         return jsonify({"error": f"Falha ao salvar a imagem: {e}"}), 500
#
#     return jsonify({"message": "Imagem salva com sucesso!", "file_path": file_path})


@main_bp.route('/flash_test')
def flash_test():
    flash('Esta é uma mensagem de teste de sucesso!', 'success')
    return render_template('listar_artigos.html')  # ou qualquer outro template que esteja usando

@main_bp.route('/ping')
def ping():
    return 'pong', 200
