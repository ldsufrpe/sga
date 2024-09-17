from app import create_app
from app.models import Area, db

def alterar_nome_area_orm():
    # Busca a área com o nome "COMPUTAÇÃO"
    area = Area.query.filter_by(nome='COMPUTAÇÃO').first()
    if area:
        # Atualiza o nome da área
        area.nome = 'CIÊNCIA DA COMPUTAÇÃO'
        db.session.commit()
        print("Nome da área alterado com sucesso!")
    else:
        print("Área com o nome 'COMPUTAÇÃO' não foi encontrada.")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        alterar_nome_area_orm()
