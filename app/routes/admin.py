from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from app.forms import RegisterForm
from app.models import User
from app import db
from werkzeug.security import generate_password_hash

from functools import wraps
from flask import abort, redirect, url_for
from flask_login import current_user
# Definir o Blueprint admin
admin_bp = Blueprint('admin', __name__, template_folder='templates/admin')



# Decorador
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            # Redireciona ou aborta com 403 se o usuário não for admin
            return abort(403)  # Ou redirecione para uma página de login
        return f(*args, **kwargs)
    return decorated_function

@admin_required
@admin_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        # Gerar o hash da senha com 'pbkdf2:sha256' para maior segurança
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')

        # Criar o novo usuário com o nome, email e a senha hasheada
        new_user = User(name=form.name.data, email=form.email.data, password=hashed_password)

        # Adicionar e salvar o novo usuário no banco de dados
        db.session.add(new_user)
        db.session.commit()

        flash('Registro realizado com sucesso! Agora você pode fazer login.', 'success')

        # Redirecionar para a página de login
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)

#Rota para listar todos os usuários (somente admin)
@admin_bp.route('/users')
@login_required
@admin_required  # Somente admins podem acessar
def list_users():
    users = User.query.all()
    return render_template('admin/list_users.html', users=users)


# Rota para excluir um usuário (somente admin)
@admin_bp.route('/delete_user/<int:user_id>')
@login_required
@admin_required  # Somente admins podem acessar
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash('Você não pode excluir outro administrador!', 'danger')
        return redirect(url_for('admin.list_users'))

    db.session.delete(user)
    db.session.commit()
    flash('Usuário excluído com sucesso!', 'success')
    return redirect(url_for('admin.list_users'))


# Rota para redefinir a senha de um usuário (somente admin)
@admin_bp.route('/reset_password/<int:user_id>', methods=['GET', 'POST'])
@login_required
@admin_required  # Somente admins podem acessar
def reset_password(user_id):
    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        new_password = request.form.get('new_password')
        user.password = generate_password_hash(new_password)
        db.session.commit()
        flash('Senha redefinida com sucesso!', 'success')
        return redirect(url_for('admin.list_users'))
    return render_template('admin/reset_password.html', user=user)

@admin_bp.route('/register_user', methods=['GET', 'POST'])
@login_required
@admin_required  # Apenas administradores podem acessar
def register_user():
    form = RegisterForm()

    if form.validate_on_submit():
        # Gerar o hash da senha com 'pbkdf2:sha256' para maior segurança
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')

        # Criar o novo usuário com o nome, email e a senha hasheada
        new_user = User(email=form.email.data, password=hashed_password)

        # Adicionar e salvar o novo usuário no banco de dados
        db.session.add(new_user)
        db.session.commit()

        flash('Usuário registrado com sucesso!', 'success')

        # Redirecionar para a lista de usuários
        return redirect(url_for('admin.list_users'))
        # Debug para checar erros do formulário
    if form.errors:
        print(form.errors)  # Verifique os erros do formulário no console

    return render_template('admin/register_user.html', form=form)


import matplotlib.pyplot as plt
import io
from matplotlib.ticker import MaxNLocator
from flask import send_file
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import requests

import plotly.graph_objects as go
import io
from flask import send_file
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import requests
import os

import plotly.graph_objects as go
import io
from flask import send_file
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
import requests


# Função para buscar dados do dashboard
import requests

def fetch_dashboard_data(area_id=None, subarea_id=None, ano_inicio=None, ano_fim=None):
    params = {}
    if area_id:
        params['area_id'] = area_id
    if subarea_id:
        params['subarea_id'] = subarea_id
    if ano_inicio and ano_fim:
        params['ano_inicio'] = ano_inicio
        params['ano_fim'] = ano_fim

    # Garantir que os parâmetros de filtro são passados na querystring
    dashboard_data_url = url_for('main.dashboard_data', _external=True)
    response = requests.get(dashboard_data_url, params=params)  # Enviar os filtros como query parameters
    if response.status_code == 200:
        return response.json()
    return None






# Função para gerar gráfico de barras com ajustes para rótulos maiores
def generate_bar_chart(chart_data, chart_title, color):
    labels = chart_data['labels']  # Anos ou outras categorias
    data = chart_data['datasets'][0]['data']  # Valores correspondentes

    # Criar gráfico de barras com Plotly
    fig = go.Figure([go.Bar(x=labels, y=data, marker_color=color)])

    # Configurar o layout do gráfico
    fig.update_layout(
        title=chart_title,
        title_font=dict(size=24),  # Aumentar tamanho do título
        xaxis_title='Anos',
        yaxis_title='Número de Artigos',
        xaxis_type='category',
        xaxis=dict(
            tickmode='array',
            tickvals=labels,
            tickfont=dict(size=24),  # Aumentar significativamente o tamanho dos rótulos no eixo X
            title_font=dict(size=24),  # Aumentar o tamanho do título do eixo X
            showgrid=True,  # Exibe as linhas de grade no eixo X
            gridcolor='rgba(200, 200, 200, 0.5)',  # Cor das gridlines do eixo X
            gridwidth=3  # Largura da linha da grade no eixo X
        ),
        yaxis=dict(
            tickfont=dict(size=24),  # Aumentar significativamente o tamanho dos rótulos no eixo Y
            title_font=dict(size=24),  # Aumentar o tamanho do título do eixo Y
            showgrid=True,  # Exibe as linhas de grade no eixo X
            gridcolor='rgba(200, 200, 200, 0.5)',  # Cor das gridlines do eixo X
            gridwidth=3  # Largura da linha da grade no eixo X # Estilo tracejado da linha
        ),
        title_x=0.5,  # Centraliza o título
        plot_bgcolor='rgba(0,0,0,0)',  # Fundo transparente
    )

    # Exportar gráfico para PNG com alta resolução
    buf = io.BytesIO()
    fig.write_image(buf, format="png", engine="kaleido", width=1400, height=700)  # Aumenta resolução
    buf.seek(0)
    return buf

# Função para gerar gráfico de linha (Fator de Impacto)
def generate_line_chart(chart_data, chart_title, color):
    labels = chart_data['labels']  # Anos
    data = chart_data['datasets'][0]['data']  # Valores correspondentes

    # Criar gráfico de linha com Plotly
    fig = go.Figure([go.Scatter(x=labels, y=data, mode='lines+markers', line=dict(color=color, width=2), fill='tozeroy')])

    # Configurar o layout do gráfico
    fig.update_layout(
        title=chart_title,
        title_font=dict(size=24),  # Aumentar tamanho do título
        xaxis_title='Anos',
        yaxis_title='Fator de Impacto',
        xaxis_type='category',
        xaxis=dict(
            tickmode='array',
            tickvals=labels,
            tickfont=dict(size=24),  # Aumentar tamanho dos rótulos no eixo X
            title_font=dict(size=24),
            showgrid=True,  # Exibe as linhas de grade no eixo X
            gridcolor='rgba(200, 200, 200, 0.5)',  # Cor das gridlines do eixo X
            gridwidth=3  # Largura da linha da grade no eixo X
            # Aumentar o tamanho do título do eixo X
        ),
        yaxis=dict(
            tickfont=dict(size=24),  # Aumentar tamanho dos rótulos no eixo Y
            title_font=dict(size=24),  # Aumentar o tamanho do título do eixo Y
            showgrid=True,  # Exibe as linhas de grade no eixo X
            gridcolor='rgba(200, 200, 200, 0.5)',  # Cor das gridlines do eixo X
            gridwidth=3  # Largura da linha da grade no eixo X
        ),
        title_x=0.5,  # Centralizar o título
        plot_bgcolor='rgba(0,0,0,0)'  # Fundo transparente
    )

    # Exportar gráfico para PNG com alta resolução
    buf = io.BytesIO()
    fig.write_image(buf, format="png", engine="kaleido", width=1400, height=700)  # Aumenta resolução
    buf.seek(0)
    return buf


#Função para gerar gráfico de pizza com proporção correta
# Função para gerar gráfico de pizza com ajustes nos labels
def generate_pie_chart(chart_data, chart_title, colors):
    labels = chart_data['labels']  # Categorias
    data = chart_data['datasets'][0]['data']  # Valores

    # Criar gráfico de pizza com Plotly (sem buraco no centro)
    fig = go.Figure([go.Pie(labels=labels, values=data,
                            marker=dict(colors=colors),
                            textinfo='percent+label',  # Mostrar rótulo e porcentagem
                            textfont=dict(size=18))])  # Aumentar o tamanho da fonte dos rótulos

    # Configurar o layout do gráfico de pizza
    fig.update_layout(
        title=chart_title,
        title_font=dict(size=24),  # Aumentar tamanho do título
        title_x=0.5,  # Centralizar o título
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,  # Ajuste da posição da legenda
            xanchor="center",
            x=0.5,
            font=dict(size=16)  # Tamanho da fonte da legenda
        ),
        height=700,  # Definir a altura do gráfico
        width=700  # Definir a largura do gráfico (proporção 1:1)
    )

    # Exportar gráfico para PNG com alta resolução
    buf = io.BytesIO()
    fig.write_image(buf, format="png", engine="kaleido", width=700, height=700)  # Ajustar resolução e proporção
    buf.seek(0)
    return buf

# Função para adicionar rodapé e cabeçalho no PDF
def add_header_footer(canvas, doc):
    # Cabeçalho
    canvas.saveState()
    canvas.setFont('Helvetica-Bold', 10)
    canvas.drawString(inch, 11*inch, "Relatório de Artigos Científicos")

    # Rodapé - Página e Data
    canvas.setFont('Helvetica', 8)
    canvas.drawString(inch, 0.75*inch, f"Página {doc.page}")
    canvas.drawRightString(7.5*inch, 0.75*inch, "Gerado em: 2024-09-10")  # Data fixa, pode ser dinâmica com datetime

    canvas.restoreState()


# Função para inserir gráficos no PDF com proporções corretas
def add_chart_to_pdf(chart_buf, chart_title, chart_type, elements, styles):
    if chart_type == 'pie':
        # Para gráficos de pizza, usamos proporção 1:1
        img = Image(chart_buf, width=5*inch, height=5*inch)  # Proporção 1:1 para pizza (circular)
    else:
        # Para gráficos de barras e linha, usamos proporção 2:1
        img = Image(chart_buf, width=7*inch, height=3.5*inch)  # Proporção 2:1 para barras e linha

    elements.append(Paragraph(chart_title, styles['Heading2']))  # Usar os estilos corretos
    elements.append(img)
    elements.append(Spacer(1, 0.75*inch))  # Espaçamento entre os gráficos


def generate_pdf_with_dynamic_charts(area_id=None, subarea_id=None, ano_inicio=None, ano_fim=None):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()  # Definir os estilos aqui
    elements = []  # Definir a lista de elementos aqui

    # Título do Relatório
    elements.append(Paragraph("Relatório do Dashboard de Artigos Científicos", styles['Title']))
    elements.append(Spacer(1, 0.5*inch))

    # Fetch dos dados da API com os filtros aplicados
    dashboard_data = fetch_dashboard_data(area_id=area_id, subarea_id=subarea_id, ano_inicio=ano_inicio,
                                          ano_fim=ano_fim)

    if dashboard_data:
        # Inserindo as métricas
        metrics = dashboard_data['metrics']
        elements.append(Paragraph(f"Total de Artigos: {metrics['total_artigos']}", styles['Normal']))
        elements.append(Paragraph(f"Média de Fator de Impacto: {metrics['media_fator_impacto']:.2f}", styles['Normal']))
        elements.append(Paragraph(f"Artigos do Ano Atual: {metrics['artigos_ano_atual']}", styles['Normal']))
        elements.append(Spacer(1, 0.5*inch))

        # Títulos dos gráficos e suas cores
        chart_info = {
            'chart1': {'title': 'Distribuição de Publicações por Ano', 'color': '#36A2EB', 'type': 'bar'},
            'chart2': {'title': 'Distribuição por Classificação Qualis', 'color': '#FF6384', 'type': 'bar'},
            'chart3': {'title': 'Publicações por Revista', 'color': '#FFCE56', 'type': 'bar'},
            'chart4': {'title': 'Publicações por Área Específica', 'color': '#4BC0C0', 'type': 'bar'},
            'chart5': {'title': 'Evolução do Fator de Impacto por Ano', 'color': '#9966FF', 'type': 'line'},  # Linha
            'chart6': {'title': 'Distribuição de Publicações Internacionalizadas', 'color': ['#FF9F40', '#FFCD56'],
                       'type': 'pie'},  # Pizza
            'chart7': {'title': 'Classificação Qualis (Gráfico de Pizza)',
                       'color': ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'], 'type': 'pie'},  # Pizza
            'chart8': {'title': 'Publicações por Área de Avaliação Qualis', 'color': '#8e44ad', 'type': 'bar'}
        }

        # Gerar gráficos conforme o tipo e inserir com proporções corretas
        for chart_id, info in chart_info.items():
            chart_data = dashboard_data.get(chart_id)
            if chart_data:
                if info['type'] == 'pie':
                    buf = generate_pie_chart(chart_data, info['title'], info['color'])
                elif info['type'] == 'line':
                    buf = generate_line_chart(chart_data, info['title'], info['color'])
                else:
                    buf = generate_bar_chart(chart_data, info['title'], info['color'])

                # Inserir gráfico no PDF com proporções adequadas
                add_chart_to_pdf(buf, info['title'], info['type'], elements, styles)

    # Geração do PDF com cabeçalho e rodapé
    doc.build(elements, onFirstPage=add_header_footer, onLaterPages=add_header_footer)

    buffer.seek(0)
    return buffer


# Rota Flask para gerar e baixar o PDF
@admin_bp.route('/download_pdf', methods=['GET'])
@login_required
def download_pdf():
    # Capturar os filtros aplicados no dashboard
    area_id = request.args.get('area_id', type=int)
    subarea_id = request.args.get('subarea_id', type=int)
    ano_inicio = request.args.get('ano_inicio', type=int)
    ano_fim = request.args.get('ano_fim', type=int)

    # Buscar os dados filtrados com os parâmetros
    dashboard_data = fetch_dashboard_data(area_id=area_id, subarea_id=subarea_id, ano_inicio=ano_inicio, ano_fim=ano_fim)

    # Gerar o PDF usando os dados filtrados
    pdf_buffer = generate_pdf_with_dynamic_charts(dashboard_data)
    return send_file(pdf_buffer, as_attachment=True, download_name='relatorio_dashboard.pdf', mimetype='application/pdf')




