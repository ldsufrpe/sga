import os
from app import create_app

app = create_app()  # Passar a classe, não a string

if __name__ == "__main__":
    # Ativa o modo de debug apenas se a variável FLASK_DEBUG for "true": bash export FLASK_DEBUG='true'
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug)
