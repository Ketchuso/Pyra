#!/usr/bin/env python3

# Standard library imports

# Remote library imports
from flask import request, session, make_response
from flask_restful import Resource
from datetime import timedelta

# Local imports
from config import app, db, api
# Add your model imports
from models import Article, User, Comment, FactCheck

import traceback

# Views go here!

class Signup(Resource):
    def post(self):
        data = request.get_json()

        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
        password = data.get("password", "").strip()
        password_confirmation = data.get("password_confirmation", "").strip()

        if not all([username, email, password, password_confirmation]):
            return {"error": "All fields are required."}, 400

        if password != password_confirmation:
            return {"error": "Passwords do not match."}, 400

        try:
            user = User(username=username, email=email)
            user.password_hash = password  # This should trigger any validation logic
            db.session.add(user)
            db.session.commit()
        except ValueError as ve:
            return {"error": str(ve)}, 400
        except Exception as e:
            db.session.rollback()
            print("Server Error:", e)  # Make sure this prints!
            traceback.print_exc()
            return {"error": "Something went wrong on the server."}, 500

        # Set up session
        stay_signed_in = data.get("stay_signed_in", False)
        session.permanent = stay_signed_in
        if stay_signed_in:
            app.permanent_session_lifetime = timedelta(days=30)
        session["user_id"] = user.id

        return user.to_dict(), 201



class CheckSession(Resource):
    def get(self):
        user = db.session.get(User, session.get('user_id'))
        if user:
            return make_response(user.to_dict(), 200)
        else:
            return {"error": "Unauthorized"}, 401

class Login(Resource):
    def post(self):
        data = request.get_json()
        username = data.get('username')
        password = data.get('password', '')
        stay_signed_in = data.get('stay_signed_in', False)

        query = db.select(User).where(User.username == username)
        user = db.session.execute(query).scalar_one_or_none()

        if user and user.check_password(password):
            session.permanent = stay_signed_in
            if stay_signed_in:
                app.permanent_session_lifetime = timedelta(days=30)
            session['user_id'] = user.id
            return user.to_dict(), 200
        
        return {"error": "Invalid username or password"}, 401

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session.pop('user_id', None)
            return make_response('', 204)
        else:
            return {"error": "Not logged in"}, 401
        
class Articles(Resource):
    def get(self):
        try:
            articles = db.session.query(Article).all()
            return [article.to_dict() for article in articles]
            # return [a.to_dict(only=('id', 'title', 'url')) for a in Article.query.all()], 200
        except Exception as e:
            return {"error" : str(e)}, 500

# Add to API
api.add_resource(Signup, '/signup')
api.add_resource(CheckSession, '/check_session')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(Articles, '/articles')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
