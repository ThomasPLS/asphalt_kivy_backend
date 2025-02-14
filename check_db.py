from app import db, User, app

with app.app_context():
    users = User.query.all()
    if not users:
        print("⚠️ Aucune entrée trouvée dans la base de données !")
    else:
        print("✅ Utilisateurs trouvés dans la base de données :")
        for user in users:
            print(f"👤 Nom d'utilisateur : {user.username}, Mot de passe : {user.password}")
