from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_limiter import Limiter  # Importar Flask-Limiter
from flask_limiter.util import get_remote_address  # Para pegar o endereço IP do cliente

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()  # Inicializa o Flask-Login

# Inicializar o Limiter (Flask-Limiter)
limiter = Limiter(
    get_remote_address,  # Usa o endereço IP do cliente como identificador
    default_limits=["200 per day", "50 per hour"]  # Limite geral por dia/hora para todas as requisições
)

def create_app(config_class='config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar as extensões
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    limiter.init_app(app)  # Inicializar o Flask-Limiter no app

    # Definir a rota de redirecionamento padrão para login quando o usuário não está autenticado
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'  # Categoria de mensagens para feedback ao usuário (opcional)

    # Registrar blueprints
    from app.routes.routes import main_bp
    from app.routes.auth import auth_bp  # Importa o blueprint de autenticação
    from app.routes.admin import admin_bp

    app.register_blueprint(main_bp)  # Rotas gerais do sistema
    app.register_blueprint(auth_bp)  # Rotas de login e autenticação
    app.register_blueprint(admin_bp, url_prefix='/admin')  # Rotas de administração, com prefixo /admin
    # Registrar o manipulador de erros aqui
    @app.errorhandler(429)
    def ratelimit_error(e):
        return "Muitas tentativas de login. Por favor, tente novamente em breve.", 429


    return app


# Função para carregar o usuário no login_manager
@login_manager.user_loader
def load_user(user_id):
    from app.models import User
    return User.query.get(int(user_id))  # Carrega o usuário pelo ID


