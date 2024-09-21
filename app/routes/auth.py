from flask import Blueprint, session
from flask import render_template, flash, request
from app import limiter
from app.forms import LoginForm
from werkzeug.security import check_password_hash
from flask_login import login_user, logout_user, login_required
from flask_limiter.util import get_remote_address
import logging
from flask import redirect, url_for
from flask_login import current_user

# Rota de registro
from app.models import User
from app.routes.routes import main_bp

# Criar o blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.before_request
def log_login_attempt():
    if request.endpoint == 'auth.login' and request.method == 'POST':
        logging.info(f"Tentativa de login para o usuário: {request.form.get('email')} do IP: {request.remote_addr}")


# Rota de login
@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute", key_func=get_remote_address)
def login():
    form = LoginForm()

    if form.validate_on_submit():
        # Buscar o usuário pelo email no banco de dados
        user = User.query.filter_by(email=form.email.data).first()

        # Verificação de existência do usuário
        if not user:
            # Se o usuário não existir
            flash('Usuário não encontrado. Verifique o email ou registre-se.', 'danger')
        elif not check_password_hash(user.password, form.password.data):
            # Se a senha estiver incorreta
            flash('Senha incorreta. Tente novamente.', 'danger')
        else:
            # Sucesso no login
            login_user(user, remember=form.remember.data)
            session.permanent = True  # Adicione esta linha
            logging.info(f"Usuário {user.email} logado com sucesso. IP: {request.remote_addr}")

            # Verificar redirecionamento seguro
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            else:
                return redirect(url_for('main.painel'))

    return render_template('login.html', form=form)



# Rota de logout
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você foi desconectado!', 'info')
    return redirect(url_for('auth.login'))


# Rota principal que redireciona para o login se o usuário não estiver autenticado
@main_bp.route('/')
def index():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))  # Redireciona para a página de login
    return redirect(url_for('main.painel'))  # Redireciona para o painel se o usuário estiver logado


