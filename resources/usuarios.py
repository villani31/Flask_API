from flask_restful import Resource, reqparse
from models.usuario import UserModel
from flask_jwt_extended import create_access_token, jwt_required, get_raw_jwt
import hmac
from blacklist import BLCKLIST

atributos = reqparse.RequestParser()
atributos.add_argument("login", type=str, required=True, help="login nao pode ser em branco")
atributos.add_argument("senha", type=str, required=True, help="Senha nao pode ser em branco")

# Recursos
class User(Resource):
    # /usuarios/user_id
    def get(self, user_id):
        user = UserModel.find_user(user_id)
        if user:
            return user.json()
        return {"message": "User not found"}, 404 # not found

    @jwt_required
    def delete(self, user_id):
        user = UserModel.find_user(user_id)
        if user:
            try:
                user.delete_user()
            except:
                return {"message":"Internal server error"}, 500
            return {"message" : "User Deleted"}
        return {"message" : "User not found"}, 404

class UserRegister(Resource):
    # /cadastro
    def post(self):
        dados = atributos.parse_args()
        if UserModel.find_by_login(dados['login']):
            return {"message" : "The login '{}' already exists".format(dados['login'])}
        user = UserModel(**dados)
        user.save_user()
        return {"message": "User created sucessfuly!"}, 201

class UserLogin(Resource):

    @classmethod
    def post(cls):
        dados = atributos.parse_args()

        user = UserModel.find_by_login(dados["login"])

        if (user and hmac.compare_digest(user.senha , dados["senha"])):
            token_de_acesso = create_access_token(identity=user.user_id)
            return {"access_token" : token_de_acesso}, 200
        return {"message" : "The username or password is incorrect"}, 401

class UserLogout(Resource):

    @jwt_required
    def post(self):
        jwt_id = get_raw_jwt()['jti'] # jwt token identifier
        BLCKLIST.add(jwt_id)
        return {"message":"Logged out sucessfully!"}, 200