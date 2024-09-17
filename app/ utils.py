from functools import wraps
from flask import abort, redirect, url_for
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            # Redireciona ou aborta com 403 se o usuário não for admin
            return abort(403)  # Ou redirecione para uma página de login
        return f(*args, **kwargs)
    return decorated_function
