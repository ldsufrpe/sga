import os

from flask import Flask, jsonify, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
from flask_wtf.csrf import CSRFError
from config import config as config_dict  # Importa o dicionário de configurações
from datetime import timedelta  # Certifique-se de que está importado
import requests
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
limiter = Limiter(
    get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
csrf = CSRFProtect()
def create_app():
    app = Flask(__name__, static_url_path='/sga/static')

    # Obtém o ambiente definido pela variável FLASK_ENV (padrão para 'development')
    env = os.getenv('FLASK_ENV', 'development')

    # Carrega a configuração correta com base no ambiente
    config_class = config_dict.get(env)

    if config_class is None:
        raise ValueError(f"Configuração para o ambiente '{env}' não encontrada.")

    app.config.from_object(config_class)

    # Verifique qual configuração está sendo carregada
    print(f"Configuração carregada: {config_class.__name__}")
    print(f"Banco de dados usado: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Não definido')}")

    # Configurações de sessão
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
    app.config['SESSION_PERMANENT'] = True
    # Inicializar as extensões
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    limiter.init_app(app)

    csrf.init_app(app)

    # Configurações adicionais
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    # Registrar blueprints
    from app.routes.routes import main_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Registrar o manipulador de erros aqui
    @app.errorhandler(429)
    def ratelimit_error(e):
        return "Muitas tentativas de login. Por favor, tente novamente em breve.", 429

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Para fins de depuração, retornar a exceção no ambiente de produção
        if not app.debug:
            return f"Erro interno no servidor: {str(e)}", 500
        else:
            return f"Erro interno no servidor (debug): {str(e)}", 500

    @app.errorhandler(CSRFError)
    def handle_csrf_error(e):
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'status': 'error', 'message': 'Sessão expirada. Por favor, faça login novamente.'}), 400
        else:
            flash('Sessão expirada. Por favor, faça login novamente.', 'error')
            return redirect(url_for('auth.login'))
    return app

@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))


@login_manager.unauthorized_handler
def unauthorized_callback():
    # Verifica se o cabeçalho 'X-Requested-With' é 'XMLHttpRequest' para requisições AJAX
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return jsonify({"error": "Sua sessão expirou. Por favor, faça login novamente."}), 401
    else:
        return redirect(url_for('auth.login'))



