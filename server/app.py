#!/usr/bin/env python3

# Standard library imports

# Remote library imports
from flask import request, session, jsonify, request, make_response;
from flask_restful import Resource

# Local imports
from config import app, db, api
# Add your model imports
from models import Article, User, Comment, FactCheck;

class Signup(Resource):
    def post(self):
        data = request.get_json()
        user = User(
            username=data["username"]
        )
        user.password_hash = data['password']
        db.session.add(user)
        db.session.commit()
        session['id'] = user.id

        return user.to_dict(), 201

# Views go here!

#for auth, implement flask-login and then maybe implement google-auth later
@app.route('/')
def index():
    return '<h1>Project Server</h1>'
# Add to API
api.add_resource(Signup, '/signup')

if __name__ == '__main__':
    app.run(port=5555, debug=True)

