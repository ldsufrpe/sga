# Instalação

python3 -m venv venv
source venv/bin/activate  # No Windows, use venv\Scripts\activate
pip install -r requirements.txt


#### Iniciar Banco

flask db init
flask db migrate -m "Initial migration."
flask db upgrade


#### Ajuste
Como isso deveria ser feito:

    Usar Relacionamentos:
        A abordagem ideal é definir um relacionamento 
entre Artigo e Area nos modelos do SQLAlchemy, como
discutido anteriormente. Isso permite que você acesse
artigo.area.nome diretamente no template sem a necessidade 
de consultas adicionais para cada artigo.

Exemplo:
class Artigo(db.Model):
    # ... outros campos ...
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'))
    area = db.relationship('Area', backref='artigos')

## Dashbord
Graficos que compare as areas e subares 
seletor de subareas


##Dashboard com Opções de Exportação de Gráficos:
Descrição: Adicionar a capacidade de exportar gráficos 
do dashboard como imagens (PNG, JPEG) ou como
relatórios em PDF.

## Exportação de Dados

Atualmente, seu sistema exporta artigos em CSV, XLSX e JSON. Se você desejar, podemos melhorar a interface para permitir exportações personalizadas, como selecionar quais colunas incluir na exportação

usuario:

lds.mat@gmail.com
12345678

leon.silva@ufrpe.br (admin)
123456



    Adicionar o Redis no Heroku (como mencionado anteriormente).
    Usar a variável REDIS_URL para configurar o Flask-Limiter com Redis no Heroku.