import os
from app import create_app

app = create_app()

if __name__ == "__main__":
    # Ativa o modo de debug apenas se a variável de ambiente FLASK_DEBUG for "true"
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug)
