from flask import Flask, render_template
from flask_login import LoginManager
from auth.routes import auth_bp
from quiz.routes import quiz_bp
from model.userdto import UserDto
from db import srp  # Importar srp desde db.py

# Inicialización de Flask y configuración
app = Flask(__name__)
app.config.from_file('config.json', load=lambda f: __import__("json").load(f))

# Inicializar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Registrar Blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(quiz_bp, url_prefix='/quiz')

# Configurar la carga del usuario para Flask-Login
@login_manager.user_loader
def load_user(email):
    return UserDto.find(srp, email)

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
