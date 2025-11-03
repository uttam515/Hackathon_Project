from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api, Resource
from flask_cors import CORS

app = Flask(__name__)
app.config['SECRET_KEY']='SUPER-SECRET-KEY'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'

db  = SQLAlchemy(app)
api = Api(app)
CORS(app)


app.config['SECRET_KEY']='SUPER-SECRET-KEY'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.db'

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), unique = True, nullable = False)
    password = db.Column(db.String(100), nullable = False)

with app.app_context():
    db.create_all()

class UserRegisteration(Resource):
    def post(self):
        data = request.get_json()
        username = data['username']
        password = data['password']
        if not username or not password:
            return {'message':'Missing username or password'}, 400
        if User.query.filter_by(username = username).first():
            return {'message':'Username already taken'}, 400
        
        new_user = User(username=username,password=password)
        db.session.add(new_user)
        db.session.commit()
        return {'message':'User created successfully'}, 200
    
api.add_resource(UserRegisteration,'/signup')   








if __name__ == '__main__':
    app.run(debug=True)