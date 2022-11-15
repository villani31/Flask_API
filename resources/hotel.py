from flask_restful import Resource, reqparse
from models.hotel import HotelModel
from flask_jwt_extended import jwt_required
import sqlite3

'''hoteis = [
    {
        'hotel_id' : 'alpha',
        'nome' : 'Alpha Hotel',
        'estrelas' : 4.3,
        'diaria' : 420.34,
        'estado' : 'Rio de Janeiro'
    },
    {
        'hotel_id' : 'bravo',
        'nome' : 'Bravo Hotel',
        'estrelas' : 4.4,
        'diaria' : 380.34,
        'estado' : 'Santa Catarina'
    },
    {
        'hotel_id' : 'charlie',
        'nome' : 'Charlie Hotel',
        'estrelas' : 3.9,
        'diaria' : 389.24,
        'estado' : 'Santa Catarina'
    }
]'''

def normalize_path_params(estado=None, estrelas_min = 0,
                            estrelas_max = 5,
                            diaria_min = 0,
                            diaria_max = 10000,
                            limit = 50,
                            offset = 0, **dados):
    if estado:
        return {
            "estrelas_min":estrelas_min,
            "estrelas_max":estrelas_max,
            "diaria_min":diaria_min,
            "diaria_max":diaria_max,
            "estado":estado,
            "limit":limit,
            "offset":offset
        }
    return {
            "estrelas_min":estrelas_min,
            "estrelas_max":estrelas_max,
            "diaria_min":diaria_min,
            "diaria_max":diaria_max,
            "limit":limit,
            "offset":offset
        }

# path
path_params = reqparse.RequestParser()
path_params.add_argument("cidade", type=str)
path_params.add_argument("estrelas_min", type=float)
path_params.add_argument("estrelas_max", type=float)
path_params.add_argument("diaria_min", type=float)
path_params.add_argument("diaria_max", type=float)
path_params.add_argument("limit", type=float)
path_params.add_argument("offset", type=float)

# Recursos
class Hoteis(Resource):
    def get(self):
        connection = sqlite3.connect("banco.db")
        cursor = connection.cursor()

        dados = path_params.parse_args()
        dados_validos = {chave:dados[chave] for chave in dados if dados[chave] is not None}
        parametros = normalize_path_params(**dados_validos)

        if parametros.get("cidade"):
            consulta = "SELECT * FROM hoteis \
                WHERE (estrelas > ? and estrelas < ?) \
                    LIMIT ? OFFSET ?"
            tupla = tuple([parametros[chave] for chave in parametros])
            resultado = cursor.execute(consulta, tupla)
        else:
            consulta = "SELECT * FROM hoteis \
                WHERE (estrelas > ? and estrelas < ?) \
                    and (diaria > ? and diaria < ?) \
                    and cidade = ? LIMIT ? OFFSET ?"
            tupla = tuple([parametros[chave] for chave in parametros])
            resultado = cursor.execute(consulta, tupla)

        hoteis = []
        for linha in resultado:
            hoteis.append({
                "hotel_id":linha[0],
                "nome":linha[1],
                "estrelas":linha[2],
                "diaria":linha[3],
                "estado":linha[4],
            })

        return {"hoteis": hoteis} # SELECT * FROM ALL.....

class Hotel(Resource):
    atributos = reqparse.RequestParser()
    atributos.add_argument('nome', type=str, required=True, help="Campo nome nao pode ser em branco")
    atributos.add_argument("estrelas", type=float, required=True, help="Cmpo estrla nao pode ser em branco")
    atributos.add_argument("diaria")
    atributos.add_argument("estado")


    def get(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            return hotel.json()
        return {"message": "Hotel not found"}, 404 # not found

    @jwt_required
    def post(self, hotel_id):
        if (HotelModel.find_hotel(hotel_id)):
            return {"message" : "Hotel id '{}' already exists.".format(hotel_id)}, 400


        dados = Hotel.atributos.parse_args()
        hotel = HotelModel(hotel_id, **dados)

        # Tratamento de erros
        try:
            hotel.save_hotel()
        except:
            {"message":"internal server error error"}, 500
        return hotel.json(),201

        # **dados desempacotar argumentos da variavel dados
        #novo_hotel = {"hotel_id" : hotel_id, **dados}

    @jwt_required
    def put(self, hotel_id):
        dados = Hotel.atributos.parse_args()
        hotel_encotrado = HotelModel.find_hotel(hotel_id)
        if hotel_encotrado:
            hotel_encotrado.update_hotel(**dados)
            hotel_encotrado.save_hotel()
            return hotel_encotrado.json(), 200 # Ok
        hotel = HotelModel(hotel_id, **dados)
        try:
            hotel.save_hotel()
        except:
            return {"message":"Internal server error"}, 500
        return hotel.json(), 201 # 201 created - criado

    @jwt_required
    def delete(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            try:
                hotel.delete_hotel()
            except:
                return {"message":"Internal server error"}, 500
            return {"message" : "Hotel Deleted"}
        return {"message" : "Hotel not found"}, 404
