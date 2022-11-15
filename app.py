from flask import Flask, jsonify
from flask_restful import Api
from resources.hotel import Hoteis, Hotel
from resources.usuarios import User, UserRegister
from resources.usuarios import UserLogin, UserLogout
from flask_jwt_extended import JWTManager
from blacklist import BLCKLIST

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = "DontTellAnyone"
app.config["JWT_BACKLIST_ENABLED"] = True
api = Api(app)
jwt = JWTManager(app)

# Antes da primeira requisicao
@app.before_first_request
def cria_banco():
    banco.create_all()

@jwt.token_in_blackist_loader
def verifica_blacklist(token):
    return token["jti"] in BLCKLIST

@jwt.revoked_token_loader
def token_de_acesso_invalidado():
    return jsonify({"message":"You jave been logged out"}), 401

api.add_resource(Hoteis, "/hoteis")
api.add_resource(Hotel, "/hoteis/<string:hotel_id>")
api.add_resource(User, "/usuarios/<int:user_id>")
api.add_resource(UserRegister, "/cadastro")
api.add_resource(UserLogin, "/login")
api.add_resource(UserLogout, "/logout")

if __name__ == "__main__":
    from sql_alchemy import banco
    banco.init_app(app)
    app.run(debug=True)