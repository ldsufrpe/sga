import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'supersecretkey'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True
    # Banco de dados local (SQLite para desenvolvimento)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dev_site.db'

class ProductionConfig(Config):
    DEBUG = False
    # Banco de dados de produção (pode ser SQLite ou outro)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'

# Escolhe a configuração com base na variável de ambiente FLASK_ENV
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}

#export FLASK_ENV=development
#export FLASK_ENV=production
#para verificar a variavel atual: echo $FLASK_ENV