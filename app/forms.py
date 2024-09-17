from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, BooleanField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp, NumberRange, Optional, ValidationError
from app.models import Artigo
import re
from wtforms import HiddenField


from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo

# Formulário de Registro
class RegisterForm(FlaskForm):
    # name = StringField('Nome', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirme a Senha',
                                     validators=[DataRequired(), EqualTo('password', message='As senhas devem ser iguais.')])
    submit = SubmitField('Registrar')

# Formulário de Login
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember = BooleanField('Lembrar de mim')
    submit = SubmitField('Login')


class ArtigoForm(FlaskForm):
    article_id = HiddenField()  # Campo oculto para armazenar o ID do artigo

    def validate_doi(self, field):
        # Limpeza do DOI removendo a URL base, se existir
        doi = re.sub(r'^https?://doi.org/', '', field.data)

        # Verificação do formato do DOI
        pattern = r'^(10\.\d{4,9}/[-._;()/:A-Z0-9]+)$'
        if not re.match(pattern, doi, re.IGNORECASE):
            raise ValidationError("O DOI deve estar no formato 10.xxxx/xxxxx.")

        # Atualiza o campo com o DOI limpo
        field.data = doi

        # Verifica se o DOI já existe no banco de dados e se o artigo com esse DOI não é o que está sendo editado
        existing_article = Artigo.query.filter_by(doi=doi).first()
        if existing_article and existing_article.id != int(self.article_id.data or 0):
            raise ValidationError("O DOI informado já existe no banco de dados. Por favor, insira um DOI único.")

    # Demais campos do formulário
    doi = StringField('DOI', validators=[
        DataRequired(message="O DOI é obrigatório."),
        validate_doi
    ])
    titulo = StringField('Título', validators=[
        DataRequired(message="O título é obrigatório."),
        Length(min=5, max=255, message="O título deve ter entre 5 e 255 caracteres.")
    ])
    ano = IntegerField('Ano de Publicação', validators=[
        DataRequired(message="O ano de publicação é obrigatório."),
        NumberRange(min=1900, max=2100, message="O ano deve estar entre 1900 e 2100.")
    ])
    revista = StringField('Revista', validators=[
        DataRequired(message="O nome da revista é obrigatório."),
        Length(max=255, message="O nome da revista deve ter até 255 caracteres.")
    ])
    issn = StringField('ISSN', validators=[
        DataRequired(message="O ISSN é obrigatório."),
        Regexp(r'^\d{4}-\d{3}[\dX]$', message="O ISSN deve estar no formato XXXX-XXXX.")
    ])
    area_id = SelectField('Área de Avaliação Qualis', choices=[], validators=[
        DataRequired(message="A seleção de uma área de avaliação Qualis é obrigatória.")
    ])
    subarea_id = SelectField('Área Específica', choices=[], validators=[
        DataRequired(message="A seleção de uma área específica é obrigatória.")
    ])
    autores = StringField('Autores', validators=[
        DataRequired(message="Insira pelo menos um autor.")
    ])
    internacionalizacao = BooleanField('Internacionalização')
    classificacao = StringField('Classificação', render_kw={'readonly': True})
    fator_impacto = DecimalField('Fator de Impacto', validators=[
        NumberRange(min=0, message="O fator de impacto deve ser um número positivo."),
        DataRequired(message="Insira um número decimal com ponto (.)")
    ])

    submit = SubmitField('Enviar')

