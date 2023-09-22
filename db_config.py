
from src import create_app, db
from src.user_model import User

app = create_app()

# Questo file serve per la Creazione, Eliminazione e Gestione degli Utenti del db.


def print_users():
    with app.app_context():
        users = User.query.all()
        if len(users) > 0:
            for user in users:
                print(f"Username: {user.username}, Password: {user.password}")
        else:
            print("Nessun Utente")


def create_users(username, password_):
    with app.app_context():
        users = User.query.all()
        for user in users:
            if user.username == username.replace(" ", ""):
                print("ERRORE: Utente gia presente")
                return
        new_user = User(username=username.replace(" ", ""), password=password_)
        db.session.add(new_user)
        db.session.commit()


def remove_users(username, ):
    with app.app_context():
        user = User.query.filter_by(username=username).first()

        if user:
            db.session.delete(user)
            db.session.commit()


if __name__ == "__main__":
    while True:
        print("\n---------------------\n1) Lista Utenti\n2) Aggiungi Utente \n3) Elimina Utente \n4) Elimina Tutti i "
              "dati\n5) Esci\n")
        x = int(input("Scelta di cosa fare: "))
        if x == 1:
            print_users()
        elif x == 2:
            nome = input("Nome Utente :  ")
            password = input("Password :  ")
            create_users(nome, password)
        elif x == 3:
            print_users()
            target_username = input("Inserisci il nome utente dell'utente da eliminare: ")
            remove_users(target_username)
        elif x == 4:
            with app.app_context():
                User.query.delete()
                db.session.commit()
        elif x == 5:
            break
