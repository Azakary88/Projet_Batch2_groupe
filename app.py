from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from models import db, User, Project, Vote
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(Config)

# Initialiser la base de données
db.init_app(app)
migrate = Migrate(app, db)

# Page d'accueil qui affiche les utilisateurs et les projets
@app.route('/')
def index():
    users = User.query.all()
    projects = Project.query.all()
    return render_template('index.html', users=users, projects=projects)

# Page pour ajouter un projet
@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        tokens_required = request.form['tokens_required']

        if not name or not description or not tokens_required:
            return "Tous les champs sont requis", 400

        try:
            new_project = Project(name=name, description=description, tokens_required=int(tokens_required))
            db.session.add(new_project)
            db.session.commit()
            return redirect(url_for('index'))
        except Exception as e:
            db.session.rollback()
            return f"Erreur lors de l'ajout du projet: {e}"

    return render_template('add_project.html')

# Page pour ajouter un utilisateur
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        tokens = request.form['tokens']

        if not username or not password:
            return "Le nom d'utilisateur et le mot de passe sont obligatoires", 400

        hashed_password = generate_password_hash(password)
        try:
            new_user = User(username=username, password_hash=hashed_password, tokens=tokens)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('user_list'))
        except Exception as e:
            db.session.rollback()
            return f"Erreur lors de l'ajout de l'utilisateur: {e}"

    return render_template('add_user.html')

# Page pour afficher les utilisateurs
@app.route('/users')
def user_list():
    users = User.query.all()
    return render_template('user_list.html', users=users)

# Page de connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('index'))
        else:
            return 'Nom d\'utilisateur ou mot de passe incorrect'

    return render_template('login.html')

@app.route('/vote/<int:project_id>', methods=['POST'])
def vote_project(project_id):
    # Vérifie si l'utilisateur est connecté
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Récupère l'utilisateur connecté
    user = User.query.get(session['user_id'])
    
    # Récupère le projet sélectionné par son ID
    project = Project.query.get(project_id)
    
    if not project:
        return jsonify({'message': 'Projet introuvable'}), 404

    # Vérifie si l'utilisateur a suffisamment de tokens pour voter
    if user.tokens < 1:
        return jsonify({'message': 'Vous n\'avez pas assez de tokens pour voter'}), 400

    try:
        # Déduire 1 token de l'utilisateur
        user.tokens -= 1

        # Créer un nouveau vote
        vote = Vote(user_id=user.id, project_id=project_id)
        db.session.add(vote)
        db.session.commit()

        return jsonify({'message': 'Vote enregistré avec succès!'}), 200
    except Exception as e:
        db.session.rollback()
        return f"Erreur lors du vote: {e}", 500


# Déconnexion
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect(url_for('login'))

# Initialisation de la base de données
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
