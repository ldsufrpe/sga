from app import db
from flask_login import UserMixin
# class Autor(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     nome_canonico = db.Column(db.String(255), unique=True, nullable=False)
#     variacoes = db.relationship('VariacaoAutor', backref='autor', lazy=True)
#
# class VariacaoAutor(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     autor_id = db.Column(db.Integer, db.ForeignKey('autor.id'), nullable=False)
#     nome_variacao = db.Column(db.String(255), nullable=False)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # Campo para identificar se o usuário é administrador

    def __repr__(self):
        return f'<User {self.email}>'



class Area(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False, unique=True)
    subareas = db.relationship('Subarea', backref='area', lazy=True)

class Subarea(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(255), nullable=False, unique=True)
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=False)
    #qualis_areas = db.relationship('QualisArea', backref='subarea', lazy=True)



class Artigo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    doi = db.Column(db.String(255), unique=True, nullable=True)
    titulo = db.Column(db.String(255), nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    revista = db.Column(db.String(255), nullable=False)
    issn = db.Column(db.String(9), nullable=False)
    area_id = db.Column(db.Integer, nullable=False)
    subarea_id = db.Column(db.Integer, nullable=False)
    autores = db.Column(db.String(255), nullable=False)  # Armazenar autores como string, pode ser melhorado com tabela relacional
    internacionalizacao = db.Column(db.Boolean, default=False)
    classificacao = db.Column(db.String(10), nullable=True)
    fator_impacto = db.Column(db.Numeric(5, 3), nullable=True)
