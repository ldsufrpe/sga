from app import create_app, db
from app.models import Area, Subarea

def populate_areas():
    areas = {
        "ASTRONOMIA / FÍSICA": [
            "Astronomia de Posição e Mecânica Celeste",
            "Física Geral",
            "Áreas Clássicas de Fenomenologia e suas Aplicações",
            "Física das Partículas Elementares e Campos",
            "Física Nuclear",
            "Física Atômica e Molecular",
            "Física dos Fluidos, Física de Plasmas e Descargas Elétricas",
            "Física da Matéria Condensada"
        ],
        "COMPUTAÇÃO": [
            "Teoria da Computação",
            "Matemática da Computação",
            "Metodologia e Técnicas da Computação",
            "Sistemas de Computação"
        ],
        "EDUCAÇÃO": [
            "Métodos e Técnicas de Ensino",
            "Orientação e Aconselhamento Educacional",
            "Administração Educacional",
            "Planejamento e Avaliação Educacional",
            "Currículo",
            "Ensino-Aprendizagem",
            "Educação Comparada",
            "Tecnologia Educacional",
            "Educação a Distância"
        ],
        "ENGENHARIAS I": [],
        "ENGENHARIAS II": [],
        "ENGENHARIAS III": [],
        "ENSINO": [],
        "INTERDISCIPLINAR": [],
        "MATEMÁTICA / PROBABILIDADE E ESTATÍSTICA": [
            "Álgebra",
            "Análise",
            "Geometria e Topologia",
            "Matemática Aplicada",
            "Probabilidade",
            "Estatística",
            "Probabilidade e Estatística Aplicadas"
        ]
    }

    for area_nome, subareas in areas.items():
        area = Area.query.filter_by(nome=area_nome).first()
        if area:
            print(f"A área '{area_nome}' já está cadastrada.")
        else:
            area = Area(nome=area_nome)
            db.session.add(area)
            db.session.commit()
            print(f"A área '{area_nome}' foi adicionada com sucesso.")

        for subarea_nome in subareas:
            subarea = Subarea.query.filter_by(nome=subarea_nome, area_id=area.id).first()
            if subarea:
                print(f"A subárea '{subarea_nome}' na área '{area_nome}' já está cadastrada.")
            else:
                new_subarea = Subarea(nome=subarea_nome, area_id=area.id)
                db.session.add(new_subarea)
                db.session.commit()
                print(f"A subárea '{subarea_nome}' foi adicionada com sucesso à área '{area_nome}'.")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()  # Certifique-se de que as tabelas existam
        populate_areas()
        print("População dos dados concluída.")
